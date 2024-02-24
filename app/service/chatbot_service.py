import asyncio
import datetime
import math
import re
from asyncio import QueueEmpty
from io import BytesIO

import asyncpg
import discord
from discord.ext import tasks, commands
from tabulate import tabulate

from common.constant import TST, MST, EST, UST, DiscussionStatus, MFST, MIT, Matching, EIT, STAFF, EvalStateResult, DiscordGuild
from common.util import logger, PRCTX, version, config
from dao import context_free_dao
from dao.participant_dao import ParticipantDao
from model.discussion_model import Discussion
from model.exchange_model import Exchange
from model.participant_model import Participant
from model.utterance_model import Utterance
from predefined.acknowledgment_predefined import Acknowledgments
from predefined.answer_item_model import AnswerItem
from predefined.answer_model import Answer
from predefined.answer_predefined import Answers
from predefined.evaluation_model import Evaluation
from predefined.evaluation_predefined import WORDING
from predefined.study_predefined import next_study
from service.ai_service import AiService
from service.context import ParticipantContext


class ChatbotService(commands.Cog):
    def __init__(self, bot: commands.Bot, pool: asyncpg.Pool):
        self.bot = bot
        self.pool = pool
        self.state: dict[int, Participant] = {}
        self.lock = asyncio.Lock()

        self.participant_dao: ParticipantDao = ParticipantDao()
        self.ai_service: AiService = AiService()

        self.loop.add_exception_type(asyncpg.PostgresConnectionError)
        self.loop.start()

    def cog_unload(self):
        self.loop.cancel()

    def state2str(self, state):
        if state is not None:
            return state.name
        return "-"

    def get_discussion_flow_state(self, x):
        if x is None:
            return None
        return x.discussion_flow_state()

    def adjust_choice_if_confirming(self, exchange: Exchange, answer_item: AnswerItem) -> MIT:
        if exchange.matter_flow_state == MFST.CLARIFY_C:
            if answer_item.code == Answers.NO_YES_01.value.get_item_by_ordinal(0).code:  # yes
                return MIT.AGREE
            elif answer_item.code == Answers.NO_YES_01.value.get_item_by_ordinal(1).code:  # no
                return MIT.DISAGREE
        return MIT.EXACT

    def pmax(self, a: list[float], skip: list[int]) -> (float, int):
        mv: float = 0
        mi: int = 0
        first: bool = True
        for i, v in enumerate(a):
            if i in skip:
                continue
            if first:
                mv = v
                mi = i
                first = False
                continue
            if v > mv:
                mv = v
                mi = i
        return mv, mi

    def ai_prediction(self, prctx: ParticipantContext, lines: list[str]) -> (MIT, AnswerItem, list[float]):
        # For algorithm details, see https://docs.google.com/spreadsheets/d/102vRddF8L6oBoeJVeFK5AYn5Oaa7H4xrBuRGd9NpJvY/edit#gid=0
        threshold_exact = 0.7
        threshold_confirm = 0.5
        distance_confirm = 0.2

        r = self.ai_service.predict_answer(prctx.matter.evaluation_item.get_content(), lines, prctx.topic.evaluation.code)
        if r is None:
            return None, None, None
        probabilities: list[float] = r[0].tolist()

        mv0, mi0 = self.pmax(probabilities, [])
        if mi0 > 0:
            if mv0 >= threshold_exact:
                return MIT.EXACT_AND_OTHER, prctx.exchange.answer.get_item_by_ordinal(mi0-1), probabilities

            if mv0 > threshold_confirm:
                mv1, _ = self.pmax(probabilities, [mi0])
                if mv0 > mv1 + distance_confirm:
                    return MIT.MATCHING, prctx.exchange.answer.get_item_by_ordinal(mi0-1), probabilities

        return MIT.OTHER, None, probabilities

    def calculate_input_type(self, prctx: ParticipantContext) -> (MIT, AnswerItem, MIT, AnswerItem, list[float], MIT, AnswerItem):
        # For algorithm details, see https://docs.google.com/spreadsheets/d/16gduyLJuA4qC7cZQyi9q8EW837LDx1vmqSxAbwYmpWQ/edit#gid=1546476474
        exchange: Exchange = prctx.exchange
        if exchange.answer is None:
            return MIT.OTHER, None, None, None, None, MIT.OTHER, None

        expected: list[AnswerItem] = list(exchange.answer.items.values())
        received: list[Utterance] = list(filter(lambda m: m.sent_at is None, exchange.utterances))
        lines: list[str] = []
        for u in received:
            lines += list(map(lambda s: s.lower(), u.content.replace('\r\n', '\n').split('\n')))

        equal_answer_items: list[list[AnswerItem]] = [[], []]
        included_answer_items: list[list[AnswerItem]] = [[], []]
        matching_line_count: int = 0
        matched_answer_items_count: int = 0
        for k, line in enumerate(lines):
            i = 0 if k == 0 else 1
            matching = False
            if exchange.allow_bullet_answer() and (len(line) == 1 or (len(line) == 2 and line[1] == ')')) and ord('a') <= ord(line[0]) <= ord('a') + len(expected) - 1:
                matching = True
                ai = exchange.answer.get_item_by_ordinal(ord(line[0]) - ord('a'))
                if ai not in equal_answer_items[i]:
                    equal_answer_items[i].append(ai)
                    if ai not in equal_answer_items[(i+1) % 2] and ai not in included_answer_items[0] and ai not in included_answer_items[1]:
                        matched_answer_items_count += 1
            else:
                for ai in expected:
                    if ai.wording.is_exactly(line):
                        matching = True
                        if ai not in equal_answer_items[i]:
                            equal_answer_items[i].append(ai)
                            if ai not in equal_answer_items[(i+1) % 2] and ai not in included_answer_items[0] and ai not in included_answer_items[1]:
                                matched_answer_items_count += 1
                    elif ai.wording.appears_in(line):
                        matching = True
                        if ai not in included_answer_items[i]:
                            included_answer_items[i].append(ai)
                            if ai not in equal_answer_items[0] and ai not in equal_answer_items[1] and ai not in included_answer_items[(i+1) % 2]:
                                matched_answer_items_count += 1
            if matching:
                matching_line_count += 1

        first_line_is_matching = len(equal_answer_items[0]) > 0 or len(included_answer_items[0]) > 0

        if matching_line_count > 1:
            matching_line_count = 2
        if matched_answer_items_count > 1:
            matched_answer_items_count = 2

        matching_type: Matching = None
        total_equal: int = len(equal_answer_items[0]) + len(equal_answer_items[1])
        total_included: int = len(included_answer_items[0]) + len(included_answer_items[1])

        if total_equal > 0 and total_included == 0:
            matching_type = Matching.EQUAL_ONLY
        elif total_equal == 0 and total_included > 0:
            matching_type = Matching.INCLUDED_ONLY
        elif total_equal > 0 and total_included > 0:
            matching_type = Matching.BOTH

        answer_item: AnswerItem = None
        input_type: MIT = MIT.OTHER
        if (matching_line_count, matched_answer_items_count) == (2, 1) or \
                (first_line_is_matching, matching_line_count, matched_answer_items_count) == (False, 1, 1) or \
                (first_line_is_matching, matching_line_count, matched_answer_items_count, matching_type) == (True, 1, 1, Matching.INCLUDED_ONLY):
            if len(equal_answer_items[0]) > 0:
                answer_item = equal_answer_items[0][0]
            elif len(equal_answer_items[1]) > 0:
                answer_item = equal_answer_items[1][0]
            elif len(included_answer_items[0]) > 0:
                answer_item = included_answer_items[0][0]
            elif len(included_answer_items[1]) > 0:
                answer_item = included_answer_items[1][0]
            input_type = MIT.MATCHING
        elif (first_line_is_matching, matching_line_count, matched_answer_items_count, matching_type) == (True, 1, 1, Matching.EQUAL_ONLY):
            answer_item = equal_answer_items[0][0]
            input_type = MIT.EXACT if len(lines) == 1 else MIT.EXACT_AND_OTHER

        if exchange.matter_flow_state in [MFST.CONFIRM, MFST.CLARIFY_C] and input_type in [MIT.EXACT, MIT.EXACT_AND_OTHER]:
            if answer_item.code == Answers.NO_YES_01.value.get_item_by_ordinal(0).code:  # yes
                input_type = MIT.AGREE
            elif answer_item.code == Answers.NO_YES_01.value.get_item_by_ordinal(1).code:  # no
                input_type = MIT.DISAGREE

        if prctx.matter.evaluation_item.item_type == EIT.DUAL and  exchange.matter_flow_state == MFST.ASK and input_type in [MIT.EXACT_AND_OTHER, MIT.MATCHING, MIT.OTHER]:
            ai_input_type, ai_answer_item, ai_probabilities = self.ai_prediction(prctx, lines)
            if ai_probabilities is not None:
                combined_input_type: MIT = MIT.OTHER
                combined_answer_item: AnswerItem = None
                if ai_input_type in [MIT.EXACT, MIT.EXACT_AND_OTHER] or (ai_input_type == MIT.MATCHING and ai_answer_item == answer_item):
                    combined_input_type = MIT.EXACT_AND_OTHER
                    combined_answer_item = ai_answer_item
                elif ai_input_type == MIT.MATCHING:
                    combined_input_type = MIT.MATCHING
                    combined_answer_item = ai_answer_item
                elif input_type == MIT.MATCHING:
                    combined_input_type = MIT.MATCHING
                    combined_answer_item = answer_item
                return combined_input_type, combined_answer_item, ai_input_type, ai_answer_item, ai_probabilities, input_type, answer_item

        return input_type, answer_item, None, None, None, input_type, answer_item

    async def utter(self, member: discord.Member, content: str, exchange: Exchange, is_acknowledgment: bool = False):
        prctx = PRCTX.get()
        finish_reading_delay = await prctx.participant_dao.get_finish_reading_delay(prctx.id)
        subject_change_delay = await prctx.participant_dao.get_subject_change_delay(prctx.id)
        await asyncio.sleep(max(finish_reading_delay, subject_change_delay))
        suffix = '\n\u200b' if is_acknowledgment or exchange.matter.evaluation_item.item_type == EIT.NONE else ''
        c: str = content+suffix
        u = await prctx.utterance_dao.create_pre_send(exchange, c)
        m = await member.send(c)
        await prctx.utterance_dao.mark_as_sent(u, m)

    async def reutter(self, member: discord.Member, content: str, utterance: Utterance, discussion: Discussion = None):
        prctx = PRCTX.get()
        suffix = '\n\u200b' if utterance.exchange.matter.evaluation_item.item_type == EIT.NONE else ''
        _ = await member.send(content+suffix)
        if discussion is None:
            await prctx.utterance_dao.increment_resent_counter(utterance)
        else:
            async with prctx.connection.transaction():
                await prctx.utterance_dao.increment_resent_counter(utterance)
                await prctx.discussion_dao.set_status(discussion, DiscussionStatus.HOLD)

    async def next_exchange(self, member: discord.Member):
        prctx = PRCTX.get()
        answer: Answer = None
        text: str = None
        target_answer_item_code: str = None
        if prctx.exchange.next_matter_flow_state == MFST.ASK_OPEN:
            text = WORDING.ASK_OPEN.value.get_random()
        elif prctx.exchange.next_matter_flow_state == MFST.ASK_CHOICE:
            answer = prctx.matter.evaluation_item.answer
            text = WORDING.ASK_CHOICE.value.get_random() + '\n' + answer.get_bullets()
        elif prctx.exchange.next_matter_flow_state == MFST.CLARIFY_AC:
            answer = prctx.exchange.answer
            text = WORDING.CLARIFY.value.get_random() + '\n' + answer.get_bullets()
        elif prctx.exchange.next_matter_flow_state == MFST.CONFIRM:
            text = WORDING.CONFIRM.value.get_random() + f'"{prctx.exchange.answer.items[prctx.exchange.answer_item_code].wording.get_content()}"?'
            answer = Answers.NO_YES_01.value
            target_answer_item_code = prctx.exchange.answer_item_code
        elif prctx.exchange.next_matter_flow_state == MFST.CLARIFY_C:
            answer = prctx.exchange.answer
            text = WORDING.CLARIFY.value.get_random() + '\n' + answer.get_bullets()
            target_answer_item_code = prctx.exchange.target_answer_item_code
        else:
            raise Exception(f'Unsupported exchange next state value {prctx.exchange.next_matter_flow_state.value}')

        answer_hash: str = await prctx.answer_dao.store(answer)
        ex: Exchange = await prctx.exchange_dao.create(prctx.matter, answer_hash, prctx.exchange.next_matter_flow_state, target_answer_item_code)
        await self.utter(member, text, ex)

    async def evaluate_state(self, participant: Participant, member: discord.Member) -> EvalStateResult:
        prctx = PRCTX.get()

        async with self.pool.acquire() as conn:
            result: EvalStateResult = EvalStateResult.CONTINUE

            prctx.connection = conn
            study, prctx.discussion = await next_study(participant, conn)
            if study is None or (prctx.discussion is not None and prctx.discussion.status == DiscussionStatus.HOLD):
                return EvalStateResult.STOP
            if prctx.discussion is None:
                prctx.discussion = await prctx.discussion_dao.create(study, participant)
            prctx.topic, prctx.matter, prctx.exchange, prctx.utterance = await prctx.discussion_service.get_state(prctx.discussion)

            if prctx.utterance is not None and prctx.utterance.discord_message_id is None:
                logger.warn(f'Failed utterance [{prctx.utterance.id}] found for {participant.discord_tag}[{participant.id}] trying again')
                await asyncio.sleep(2*participant.delay_scale)
                m = await member.send(prctx.utterance.content)
                logger.warn(f'Resent failed utterance [{prctx.utterance.id}] to {participant.discord_tag}[{participant.id}]')
                await prctx.utterance_dao.mark_as_sent(prctx.utterance, m)
                return EvalStateResult.CONTINUE

            if prctx.topic is not None:
                prctx.topic.score = await prctx.topic_dao.calculate_score(prctx.topic)
            st = (self.get_discussion_flow_state(prctx.topic),
                  self.get_discussion_flow_state(prctx.matter),
                  self.get_discussion_flow_state(prctx.exchange),
                  self.get_discussion_flow_state(prctx.utterance))

            again = False
            logger.info(f'Processing {participant.discord_tag}[{participant.id}]  '
                        f'{prctx.discussion.study.code.value}[{prctx.discussion.id}]/{prctx.discussion.status.value}  '
                        f'{prctx.topic.code if prctx.topic is not None else None}[{prctx.topic.id if prctx.topic is not None else None}]/{self.state2str(st[0])}  '
                        f'{prctx.matter.evaluation_item.code if prctx.matter is not None and prctx.matter.evaluation_item is not None else None}[{prctx.matter.id if prctx.matter is not None else None}]/{self.state2str(st[1])}  '
                        f'{prctx.exchange.matter_flow_state.value if prctx.exchange is not None and prctx.exchange.matter_flow_state is not None else None}[{prctx.exchange.id if prctx.exchange is not None else None}]/{self.state2str(st[2])}  '
                        f'{prctx.utterance.id if prctx.utterance is not None else None}/{self.state2str(st[3])} -> '
                        f'{prctx.exchange.next_matter_flow_state.value if prctx.exchange is not None and prctx.exchange.next_matter_flow_state is not None else None}')
            now = datetime.datetime.now().astimezone()

            # For state actions see https://docs.google.com/spreadsheets/d/1XvQL4azq10ll_X8mlh6sfkYrmo2zqOFwpK77izfuzZI/edit#gid=997915990
            if st in [(    None,     None,     None,     None),
                      (TST.COMP, MST.COLA, EST.COLA, UST.DNAN),
                      (TST.COMP, MST.COLA, EST.COLA, UST.RCVD)]:
                next_evaluation: Evaluation
                next_evaluation_code: str
                next_evaluation, next_evaluation_code, _ = await study.next_eval(prctx.discussion)

                if next_evaluation is None:
                    await prctx.discussion_dao.set_status(prctx.discussion, DiscussionStatus.COMPLETED)
                else:
                    async with prctx.connection.transaction():
                        await prctx.evaluation_dao.store(next_evaluation)
                        prctx.topic = await prctx.topic_dao.create(next_evaluation, next_evaluation_code, prctx.discussion)
                        prctx.matter = await prctx.matter_dao.create(prctx.topic, next_evaluation.first_item())

                        answer: Answer = None
                        if prctx.matter.evaluation_item is not None:
                            answer = prctx.matter.evaluation_item.answer
                        answer_hash: str = await prctx.answer_dao.store(answer)
                        prctx.exchange = await prctx.exchange_dao.create(prctx.matter, answer_hash, MFST.ASK, None)
                        await asyncio.sleep(5*prctx.delay_scale)
                        await self.utter(member, prctx.matter.evaluation_item.get_content(), prctx.exchange)
            elif st in [(TST.INCO, MST.INCO, EST.INWA, UST.SENT),
                        (TST.INCO, MST.INCO, EST.INWA, UST.DLVR)]:
                result = EvalStateResult.WAIT_FOR_MESSAGE
            elif st in [(TST.INCO, MST.INCO, EST.INYO, UST.SENT),
                        (TST.INCO, MST.INCO, EST.INYO, UST.DLVR)]:
                prctx.wakeup_deadline = now + datetime.timedelta(seconds=1*prctx.delay_scale)
                result = EvalStateResult.WAIT_FOR_DEADLINE_OR_MESSAGE
            elif st in [(TST.INCO, MST.INCO, EST.INFO, UST.SENT),
                        (TST.INCO, MST.INCO, EST.INFO, UST.DLVR)]:
                prctx.wakeup_deadline = prctx.exchange.utterances[0].sent_at + datetime.timedelta(seconds=config.get_int('application', 'forgotten-2-question-age')*prctx.delay_scale)
                result = EvalStateResult.WAIT_FOR_DEADLINE_OR_MESSAGE
                if prctx.utterance.resent_counter == 0:
                    await self.reutter(member, prctx.matter.evaluation_item.get_content(), prctx.utterance)
            elif st in [(TST.INCO, MST.INCO, EST.INFO2, UST.SENT),
                        (TST.INCO, MST.INCO, EST.INFO2, UST.DLVR)]:
                result = EvalStateResult.WAIT_FOR_MESSAGE
                if prctx.utterance.resent_counter == 1:
                    await self.reutter(member, prctx.matter.evaluation_item.get_content(), prctx.utterance, prctx.discussion)
            elif st == (TST.INCO, MST.INCO, EST.INUN, UST.DNAN):
                await prctx.exchange_dao.store_transition(prctx.exchange, MIT.OTHER, MFST.COMPLETED, None, None, None, None, None, None)
                again = True
            elif st == (TST.INCO, MST.INCO, EST.INUN, UST.RCVD):
                input_type, answer_item, ai_input_type, ai_answer_item, ai_probabilities, nonai_input_type, nonai_answer_item = self.calculate_input_type(prctx)
                if prctx.debug and prctx.exchange.matter_flow_state == MFST.ASK and prctx.exchange.answer is not None:
                    debug_items: list[str] = ["unknown"]
                    for anit in prctx.exchange.answer.sorted_items:
                        debug_items.append(anit.wording.content)
                    table: list[list[str]] = []
                    for dii, div in enumerate(debug_items):
                        row = [div, "", "", ""]
                        if ai_probabilities is not None:
                            row[1] = str(math.floor(ai_probabilities[dii]*10000)/100)+"%"
                            if ai_input_type == MIT.OTHER and dii == 0:
                                row[1] += " \u2713 + clarify"
                            elif ai_answer_item is not None and dii == ai_answer_item.ordinal + 1:
                                row[1] += " \u2713"
                                if ai_input_type == MIT.MATCHING:
                                    row[1] += " + confirm"

                        if nonai_input_type == MIT.OTHER and dii == 0:
                            row[2] = "\u2713 + clarify"
                        elif nonai_answer_item is not None and dii == nonai_answer_item.ordinal + 1:
                            row[2] = "\u2713"
                            if nonai_input_type == MIT.MATCHING:
                                row[2] += " + confirm"
                            elif nonai_input_type == MIT.EXACT:
                                row[2] += " + ask-open"

                        if input_type == MIT.OTHER and dii == 0:
                            row[3] = "\u2713 + clarify"
                        elif answer_item is not None and dii == answer_item.ordinal + 1:
                            row[3] = "\u2713"
                            if input_type == MIT.MATCHING:
                                row[3] += " + confirm"
                            elif input_type == MIT.EXACT:
                                row[3] += " + ask-open"
                        table.append(row)

                    _ = await member.send(f'`{tabulate(table, ["", "AI", "Non-AI", "Final"], tablefmt="psql")}`')

                next_state: MFST = prctx.matter_service.next_state(prctx.matter.evaluation_item.item_type, prctx.exchange.matter_flow_state, input_type)
                again = True
                try:
                    if next_state == MFST.COMPLETED and \
                            answer_item is not None and \
                            prctx.matter.evaluation_item.acknowledgment_set is not None and \
                            prctx.matter.evaluation_item.code in prctx.topic.to_acknowledge:
                        k = prctx.exchange.target_answer_item_code or answer_item.code
                        if prctx.matter.evaluation_item.acknowledgment_set[k] is not None:
                            ack = prctx.matter.evaluation_item.acknowledgment_set[k].get_permuted(prctx.discussion.id, prctx.ack_count)
                            await self.utter(member, ack, prctx.exchange, True)
                            prctx.ack_count += 1
                            again = False
                except BaseException as e:
                    logger.error("Acknowledgement utterance failed", e)
                await prctx.exchange_dao.store_transition(prctx.exchange, input_type, next_state, answer_item, ai_input_type, ai_answer_item, ai_probabilities, nonai_input_type, nonai_answer_item)
            elif st in [(TST.INCO, MST.INCO, EST.CONL, UST.DNAN),
                        (TST.INCO, MST.INCO, EST.CONL, UST.RCVD)]:
                await self.next_exchange(member)
            elif st in [(TST.INCO, MST.INCO, EST.COLA, UST.DNAN),
                        (TST.INCO, MST.INCO, EST.COLA, UST.DLVR),
                        (TST.INCO, MST.INCO, EST.COLA, UST.RCVD)]:
                async with prctx.connection.transaction():
                    answer_item: AnswerItem = None
                    answer_item_code = await prctx.matter_dao.calculate_answer_item_code(prctx.matter)
                    if answer_item_code is not None and prctx.matter.evaluation_item.answer is not None:
                        answer_item = prctx.matter.evaluation_item.answer.items[answer_item_code]
                    await prctx.matter_dao.complete(prctx.matter, answer_item)
                again = True
            elif st in [(TST.INCO, MST.CONL, EST.COLA, UST.DNAN),
                        (TST.INCO, MST.CONL, EST.COLA, UST.DLVR),
                        (TST.INCO, MST.CONL, EST.COLA, UST.RCVD)]:
                async with prctx.connection.transaction():
                    await prctx.matter.post_action()
                    prctx.matter = await prctx.matter_dao.create(prctx.topic, prctx.topic.evaluation.next_item(prctx.matter.evaluation_item))

                    answer: Answer = None
                    if prctx.matter.evaluation_item is not None:
                        answer = prctx.matter.evaluation_item.answer
                    answer_hash: str = await prctx.answer_dao.store(answer)
                    prctx.exchange = await prctx.exchange_dao.create(prctx.matter, answer_hash, MFST.ASK, None)
                    await self.utter(member, prctx.matter.evaluation_item.get_content(), prctx.exchange)
            elif st in [(TST.INCO, MST.COLA, EST.COLA, UST.DNAN),
                        (TST.INCO, MST.COLA, EST.COLA, UST.RCVD)]:
                await prctx.matter.post_action()
                await prctx.topic_dao.complete(prctx.topic)
                again = True

        if again:
            return await self.evaluate_state(participant, member)

        return result

    async def init_participant(self, discord_id: int, discord_name: str, discord_discriminator: int, guild: str) -> Participant:
        async with self.lock:
            async with self.pool.acquire() as conn:
                prtag = f'{discord_name}#{discord_discriminator}'
                prid = await context_free_dao.get_participant_id_and_create_if_not_exist(conn, discord_id, prtag, guild)
                if prid not in self.state.keys():
                    self.state[prid] = Participant(prid, discord_id, prtag)
                return self.state[prid]

    async def store_message(self, message: discord.Message, now):
        u = message.author
        pr = await self.init_participant(u.id, u.name, u.discriminator, None)

        async with pr.lock:
            async with self.pool.acquire() as conn:
                prctx = PRCTX.get()
                prctx.connection = conn
                xid = await prctx.exchange_dao.get_id_of_latest_delivered_by_participant(pr)
                await prctx.utterance_dao.create_received(xid, message, now)

    async def record_message_delivery(self, message: discord.Message, now):
        async with self.pool.acquire() as conn:
            prctx = PRCTX.get()
            prctx.connection = conn
            await prctx.utterance_dao.record_delivery(message, now)

    async def handle_new_message(self, message: discord.Message):
        now = datetime.datetime.now().astimezone()

        dest = message.author
        if message.author.id == self.bot.user.id:
            dest = message.channel.recipient
        pr = await self.init_participant(dest.id, dest.name, dest.discriminator, None)
        async with pr.lock:
            if message.author.id == self.bot.user.id:
                await pr.queue.put(lambda: self.record_message_delivery(message, now))
            else:
                async with self.pool.acquire() as conn:
                    study, discussion = await next_study(pr, conn)
                    if discussion is not None and discussion.status == DiscussionStatus.HOLD:
                        await context_free_dao.set_discussion_status(conn, discussion, DiscussionStatus.ACTIVE)
                await pr.queue.put(lambda: self.store_message(message, now))

    async def handle_command_version(self, ctx: discord.ext.commands.Context):
        await ctx.send(version)

    async def handle_command_acks(self, ctx: discord.ext.commands.Context):
        m: str = ""
        for ack in Acknowledgments:
            for i, w in enumerate(ack.value.all):
                if len(m) + len(w) + 10 > 2000:
                    await ctx.send(m)
                    m = ""
                m += f'{ack.name}-{i+1}. {w}\n'
        await ctx.send(m)

    async def handle_command_speed(self, ctx: discord.ext.commands.Context, k: float):
        if f'{ctx.author.name}#{ctx.author.discriminator}' not in STAFF:
            return
        async with self.pool.acquire() as conn:
            prid = await context_free_dao.get_participant_id_by_discord_id(conn, ctx.author.id)
        if prid is None:
            return

        self.state[prid].delay_scale = k

    async def handle_command_debug(self, ctx: discord.ext.commands.Context, on: bool):
        if f'{ctx.author.name}#{ctx.author.discriminator}' not in STAFF:
            return
        async with self.pool.acquire() as conn:
            prid = await context_free_dao.get_participant_id_by_discord_id(conn, ctx.author.id)
        if prid is None:
            return

        if on is None:
            self.state[prid].debug = not self.state[prid].debug
        else:
            self.state[prid].debug = on

    async def handle_command_report(self, ctx: discord.ext.commands.Context):
        if f'{ctx.author.name}#{ctx.author.discriminator}' not in STAFF:
            return
        async with self.pool.acquire() as conn:
            text = '"Participant","Guilds","Last heard from","Evaluations"\n'
            for x in await context_free_dao.get_report_nlp1a(conn):
                name = re.sub("[\n\r\t]", " ", x.participant_name.replace('"', '""'))
                guild_names = x.guild_names if x.guild_names is not None else ""
                last_heard_from = x.last_heard_from if x.last_heard_from is not None else ""
                evaluations = x.evaluations if x.evaluations is not None else ""
                text += f'"{name}","{guild_names}","{last_heard_from}","{evaluations}"\n'
            logger.info('\n'+text)
            try:
                m = await ctx.send(file=discord.File(BytesIO(bytes(text,'utf-8')), f'report-{datetime.datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")}.csv'))
                logger.info(f'Report URL: {m.attachments[0].url if len(m.attachments) > 0 else "???"}')
            except BaseException as e:
                logger.error(f'Failed to send report', exc_info=True)

    async def handle_command_reset(self, ctx: discord.ext.commands.Context):
        if f'{ctx.author.name}#{ctx.author.discriminator}' not in STAFF:
            return

        async with self.pool.acquire() as conn:
            await context_free_dao.increment_participant_round(conn, ctx.author.id)

    async def handle_participant(self, participant: Participant, member: discord.Member):
        prctx = ParticipantContext(participant.id, participant.discord_id, participant.discord_tag)
        PRCTX.set(prctx)

        do_state_evaluation: bool = True
        while True:
            prctx.delay_scale = participant.delay_scale
            prctx.debug = participant.debug

            now = datetime.datetime.now().astimezone()
            if prctx.wakeup_deadline is not None and prctx.wakeup_deadline > now:
                do_state_evaluation = True
                prctx.wakeup_deadline = None

            try:
                while True:
                    async with participant.lock:
                        h = participant.queue.get_nowait()

                    do_state_evaluation = True
                    prctx.wakeup_deadline = None
                    try:
                        await h()
                    except BaseException as e:
                        logger.error(f'Failed to handle queue events for participant {participant.discord_tag}[{participant.id}]', exc_info=True)
            except QueueEmpty:
                pass

            if do_state_evaluation:
                try:
                    r: EvalStateResult = await self.evaluate_state(participant, member)
                    if r == EvalStateResult.STOP:
                        async with participant.lock:
                            participant.active_handler = False
                        break
                    elif r in [EvalStateResult.WAIT_FOR_MESSAGE, EvalStateResult.WAIT_FOR_DEADLINE_OR_MESSAGE]:
                        do_state_evaluation = False
                except BaseException as e:
                    logger.error(f'Failed to evaluate the state for participant {participant.discord_tag}[{participant.id}]', exc_info=True)

            await asyncio.sleep(0.5*participant.delay_scale)

    @tasks.loop(seconds=10)
    async def loop(self):
        processed: list[str] = []
        for guild in self.bot.guilds:
            dgn = DiscordGuild.get_name_by_value(guild.id)
            if dgn is None:
                dgn = str(guild.id)

            for member in guild.members:
                pr = await self.init_participant(member.id, member.name, member.discriminator, dgn)
                if guild.id not in pr.guild_ids:
                    pr.guild_ids.append(guild.id)
                if member.id not in processed and member.id != self.bot.user.id:
                    async with pr.lock:
                        if not pr.active_handler:
                            async with self.pool.acquire() as conn:
                                study, discussion = await next_study(pr, conn)
                            if pr.queue.qsize() > 0 or (study is not None and (discussion is None or discussion.status == DiscussionStatus.ACTIVE)):
                                self.bot.loop.create_task(self.handle_participant(pr, member))
                                pr.active_handler = True
                processed.append(member.id)

    @loop.before_loop
    async def before_loop(self):
        logger.info('Waiting for the bot to connect ...')
        await self.bot.wait_until_ready()
