import datetime

import asyncpg

from common.util import config, PRCTX
from common.constant import MFST, MIT, EST, EIT
from model.utterance_model import Utterance
from predefined.answer_model import Answer


class Exchange:
    def __init__(self, rec: asyncpg.Record, matter):
        self.id: int = rec["id"]
        self.matter_flow_state: MFST = MFST(rec["matter_flow_state"])
        self.next_matter_flow_state: MFST = None
        if rec["next_matter_flow_state"] is not None:
            self.next_matter_flow_state: MFST = MFST(rec["next_matter_flow_state"])
        self.input_type: MIT = None
        if rec["input_type"] is not None:
            self.input_type: MIT = MIT(rec["input_type"])
        self.answer_hash: str = rec["answer_hash"]
        self.answer: Answer = None
        self.target_answer_item_code: str = None
        if rec["target_answer_item_code"] is not None:
            self.target_answer_item_code: str = rec["target_answer_item_code"]
        self.answer_item_code: str = None
        if rec["answer_item_code"] is not None:
            self.answer_item_code: str = rec["answer_item_code"]
        self.created_at = rec["created_at"]
        self.updated_at = rec["updated_at"]
        self.utterances: list[Utterance] = []
        self.matter = matter

    def discussion_flow_state(self) -> EST:
        if self.next_matter_flow_state is not None and self.next_matter_flow_state == MFST.COMPLETED:
            return EST.COLA
        if self.next_matter_flow_state is not None:
            return EST.CONL

        prctx = PRCTX.get()
        mature = datetime.timedelta(seconds=config.get_int('application', 'mature-answer-age')*prctx.delay_scale)
        forgotten = datetime.timedelta(seconds=config.get_int('application', 'forgotten-question-age')*prctx.delay_scale)
        forgotten2 = datetime.timedelta(seconds=config.get_int('application', 'forgotten-2-question-age')*prctx.delay_scale)

        now = datetime.datetime.now().astimezone()
        if self.utterances[-1].received_at is not None:
            t = max(map(lambda m: m.received_at, filter(lambda m: m.received_at is not None, self.utterances)))
            if now - t < mature:
                return EST.INYO
            return EST.INUN
        elif self.matter.evaluation_item.item_type == EIT.NONE and self.utterances[-1].delivered_at is not None:
            if now - self.utterances[-1].delivered_at < mature:
                return EST.INYO
            return EST.INUN

        if now - self.utterances[0].sent_at > forgotten2:
            return EST.INFO2
        if now - self.utterances[0].sent_at > forgotten:
            return EST.INFO
        return EST.INWA

    def allow_bullet_answer(self) -> bool:
        return self.matter_flow_state in [MFST.ASK_CHOICE, MFST.CLARIFY_C, MFST.CLARIFY_AC] or (self.matter_flow_state == MFST.ASK and self.matter.evaluation_item.item_type == EIT.CHOICE)

    def get_joined_received_utterances(self) -> str:
        return '\n'.join(list(map(lambda u: u.content, filter(lambda u: u.received_at is not None, self.utterances))))