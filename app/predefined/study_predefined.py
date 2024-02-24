import copy
import datetime
import re
from enum import Enum

import pytz

from common.constant import AnswerCode, EvaluationCode, StudyCode, DiscordGuild
from common.util import PRCTX
from dao import context_free_dao
from model.discussion_model import Discussion
from model.topic_model import Topic
from model.discussion_model import DiscussionStatus
from model.participant_model import Participant
from predefined.evaluation_predefined import Evaluations
from predefined.study_model import Study
from predefined.evaluation_model import Evaluation
from predefined.evaluation_item_model import EvaluationItem
from predefined.answer_model import Answer
from predefined.answer_item_model import AnswerItem
from predefined.wording_model import Wording


async def next_eval__intro(discussion: Discussion) -> (Evaluation, str, Topic):
    prctx = PRCTX.get()
    topics: list[Topic] = await prctx.topic_dao.get_by_discussion(discussion)

    for t in topics:
        t.evaluation = await prctx.evaluation_dao.get_by_hash(t.evaluation_hash)

    if len(topics) == 0:
        return Evaluations.INTRO.value, EvaluationCode.INTRO.value, None
    if topics[-1].completed_at is None:
        return topics[-1].evaluation, topics[-1].code, topics[-1]
    return None, None, None


async def next_eval__data_collection(discussion: Discussion) -> (Evaluation, str, Topic):
    prctx = PRCTX.get()
    topics: list[Topic] = await prctx.topic_dao.get_by_discussion(discussion)

    for t in topics:
        t.evaluation = await prctx.evaluation_dao.get_by_hash(t.evaluation_hash)

    if len(topics) == 0:
        return Evaluations.CONSENT_DATA_COLLECTION.value, EvaluationCode.CONSENT_DATA_COLLECTION.value, None
    if topics[-1].completed_at is None:
        return topics[-1].evaluation, topics[-1].code, topics[-1]

    evals: list[EvaluationCode] = list(map(lambda t: t.evaluation.code, topics))
    if EvaluationCode.DEMOGRAPHICS not in evals:
        return Evaluations.DEMOGRAPHICS.value, EvaluationCode.DEMOGRAPHICS.value, None

    core_evals: list[Evaluation] = [Evaluations.PHQ_9.value, Evaluations.GAD_7.value, Evaluations.PCL_5.value]
    remaining_core_evals: list[Evaluation] = [e for e in core_evals if e.code not in evals]
    if len(remaining_core_evals) == 1:
        x: Evaluation = remaining_core_evals[0]
        if topics[-1].evaluation.code == EvaluationCode.ANNOUNCE_LAST:
            return x, x.code.value, None
        ev: Evaluation = copy.deepcopy(Evaluations.ANNOUNCE_LAST.value)
        ev.get_item_by_ordinal([1]).content = Wording(ev.get_item_by_ordinal([1]).content.content.format(code=x.code.value.upper(), name=x.name, action=x.action), [])
        return ev, ev.code.value, None

    if len(remaining_core_evals) > 1:
        if topics[-1].evaluation.code == EvaluationCode.SELECT_N:
            ei: EvaluationItem = topics[-1].evaluation.get_item_by_ordinal([1])
            aic = await prctx.matter_dao.get_answer_item_code_by_topic_and_evaluation_item(topics[-1], ei)
            a = ei.answer.items[aic].wording.content
            return Evaluations.get_by_code(EvaluationCode(a).value), a, None
        s: str = "    " + "\n    ".join(list(map(lambda e: f'* you can {e.action} with the {e.name} ({e.code.value.upper()})', remaining_core_evals)))
        ev: Evaluation = copy.deepcopy(Evaluations.SELECT_N.value)
        ev.get_item_by_ordinal([1]).content = Wording(ev.get_item_by_ordinal([1]).content.content.format(evaluations=s), [])
        ev.get_item_by_ordinal([1]).answer = Answer(AnswerCode.SELECT_EVALUATION, list(map(lambda x: AnswerItem(x[0], 0, Wording(x[1].code.value, x[1].nickcodes)), enumerate(remaining_core_evals))))
        return ev, ev.code.value, None

    if EvaluationCode.USABILITY_1 not in evals:
        return Evaluations.USABILITY_1.value, EvaluationCode.USABILITY_1.value, None

    if EvaluationCode.THANKS not in evals:
        return Evaluations.THANKS.value, EvaluationCode.THANKS.value, None

    return None, None, None


async def next_eval__nlp1(discussion: Discussion) -> (Evaluation, str, Topic):
    prctx = PRCTX.get()
    topics: list[Topic] = await prctx.topic_dao.get_by_discussion(discussion)

    for t in topics:
        t.evaluation = await prctx.evaluation_dao.get_by_hash(t.evaluation_hash)

    if len(topics) == 0:
        return Evaluations.CONSENT_NLP1.value, EvaluationCode.CONSENT_NLP1.value, None
    if topics[-1].completed_at is None:
        return topics[-1].evaluation, topics[-1].code, topics[-1]

    evals: list[EvaluationCode] = list(map(lambda t: t.evaluation.code, topics))
    if EvaluationCode.DEMOGRAPHICS not in evals:
        return Evaluations.DEMOGRAPHICS.value, EvaluationCode.DEMOGRAPHICS.value, None

    core_evals: list[Evaluation] = [Evaluations.PHQ_9.value, Evaluations.GAD_7.value, Evaluations.PCL_5.value]
    remaining_core_evals: list[Evaluation] = [e for e in core_evals if e.code not in evals]
    if len(remaining_core_evals) == 1:
        x: Evaluation = remaining_core_evals[0]
        if topics[-1].evaluation.code == EvaluationCode.ANNOUNCE_LAST:
            return x, x.code.value, None
        ev: Evaluation = copy.deepcopy(Evaluations.ANNOUNCE_LAST.value)
        ev.get_item_by_ordinal([1]).content = Wording(ev.get_item_by_ordinal([1]).content.content.format(code=x.code.value.upper(), name=x.name, action=x.action), [])
        return ev, ev.code.value, None

    if len(remaining_core_evals) > 1:
        if topics[-1].evaluation.code == EvaluationCode.SELECT_N:
            ei: EvaluationItem = topics[-1].evaluation.get_item_by_ordinal([1])
            aic = await prctx.matter_dao.get_answer_item_code_by_topic_and_evaluation_item(topics[-1], ei)
            a = ei.answer.items[aic].wording.content
            return Evaluations.get_by_code(EvaluationCode(a).value), a, None
        s: str = "    " + "\n    ".join(list(map(lambda e: f'* you can {e.action} with the {e.name} ({e.code.value.upper()})', remaining_core_evals)))
        ev: Evaluation = copy.deepcopy(Evaluations.SELECT_N.value)
        ev.get_item_by_ordinal([1]).content = Wording(ev.get_item_by_ordinal([1]).content.content.format(evaluations=s), [])
        ev.get_item_by_ordinal([1]).answer = Answer(AnswerCode.SELECT_EVALUATION, list(map(lambda x: AnswerItem(x[0], 0, Wording(x[1].code.value, x[1].nickcodes)), enumerate(remaining_core_evals))))
        return ev, ev.code.value, None

    if EvaluationCode.USABILITY_2 not in evals:
        return Evaluations.USABILITY_2.value, EvaluationCode.USABILITY_2.value, None

    if EvaluationCode.TRANSITION_NLP1 not in evals:
        return Evaluations.TRANSITION_NLP1.value, EvaluationCode.TRANSITION_NLP1.value, None

    core_evals_choice_only: list[Evaluation] = [Evaluations.PHQ_9_CO.value, Evaluations.GAD_7_CO.value, Evaluations.PCL_5_CO.value]
    remaining_core_evals_choice_only: list[Evaluation] = [e for e in core_evals_choice_only if e.code not in evals]
    if len(remaining_core_evals_choice_only) == 1:
        x: Evaluation = remaining_core_evals_choice_only[0]
        if topics[-1].evaluation.code == EvaluationCode.ANNOUNCE_LAST:
            return x, x.code.value, None
        ev: Evaluation = copy.deepcopy(Evaluations.ANNOUNCE_LAST.value)
        ev.get_item_by_ordinal([1]).content = Wording(ev.get_item_by_ordinal([1]).content.content.format(code=re.sub("-CO$", "", x.code.value.upper()), name=x.name, action=x.action), [])
        return ev, ev.code.value, None

    if len(remaining_core_evals_choice_only) > 1:
        if topics[-1].evaluation.code == EvaluationCode.SELECT_N:
            ei: EvaluationItem = topics[-1].evaluation.get_item_by_ordinal([1])
            aic = await prctx.matter_dao.get_answer_item_code_by_topic_and_evaluation_item(topics[-1], ei)
            a = ei.answer.items[aic].wording.content
            return Evaluations.get_by_code(EvaluationCode(a+"-co").value), a+"-co", None
        s: str = "    " + "\n    ".join(list(map(lambda e: f'* you can {e.action} with the {e.name} ({re.sub("-CO$", "", e.code.value.upper())})', remaining_core_evals_choice_only)))
        ev: Evaluation = copy.deepcopy(Evaluations.SELECT_N.value)
        ev.get_item_by_ordinal([1]).content = Wording(ev.get_item_by_ordinal([1]).content.content.format(evaluations=s), [])
        ev.get_item_by_ordinal([1]).answer = Answer(AnswerCode.SELECT_EVALUATION, list(map(lambda x: AnswerItem(x[0], 0, Wording(re.sub("-[Cc][Oo]$", "", x[1].code.value), x[1].nickcodes)), enumerate(remaining_core_evals_choice_only))))
        return ev, ev.code.value, None

    if EvaluationCode.THANKS not in evals:
        return Evaluations.THANKS.value, EvaluationCode.THANKS.value, None

    return None, None, None


async def next_eval__nlp1a(discussion: Discussion) -> (Evaluation, str, Topic):
    prctx = PRCTX.get()
    topics: list[Topic] = await prctx.topic_dao.get_by_discussion(discussion)

    for t in topics:
        t.evaluation = await prctx.evaluation_dao.get_by_hash(t.evaluation_hash)

    if len(topics) == 0:
        return Evaluations.CONSENT_NLP1.value, EvaluationCode.CONSENT_NLP1.value, None
    if topics[-1].completed_at is None:
        return topics[-1].evaluation, topics[-1].code, topics[-1]

    evals: list[EvaluationCode] = list(map(lambda t: t.evaluation.code, topics))
    if EvaluationCode.DEMOGRAPHICS not in evals:
        return Evaluations.DEMOGRAPHICS.value, EvaluationCode.DEMOGRAPHICS.value, None

    core_evals: list[Evaluation] = [Evaluations.PHQ_9.value, Evaluations.GAD_7.value, Evaluations.PCL_5.value]
    remaining_core_evals: list[Evaluation] = [e for e in core_evals if e.code not in evals]
    if len(remaining_core_evals) == 1:
        x: Evaluation = remaining_core_evals[0]
        if topics[-1].evaluation.code == EvaluationCode.ANNOUNCE_LAST:
            return x, x.code.value, None
        ev: Evaluation = copy.deepcopy(Evaluations.ANNOUNCE_LAST.value)
        ev.get_item_by_ordinal([1]).content = Wording(ev.get_item_by_ordinal([1]).content.content.format(code=x.code.value.upper(), name=x.name, action=x.action), [])
        return ev, ev.code.value, None

    if len(remaining_core_evals) > 1:
        if topics[-1].evaluation.code == EvaluationCode.SELECT_N:
            ei: EvaluationItem = topics[-1].evaluation.get_item_by_ordinal([1])
            aic = await prctx.matter_dao.get_answer_item_code_by_topic_and_evaluation_item(topics[-1], ei)
            a = ei.answer.items[aic].wording.content
            return Evaluations.get_by_code(EvaluationCode(a).value), a, None
        s: str = "    " + "\n    ".join(list(map(lambda e: f'* you can {e.action} with the {e.name} ({e.code.value.upper()})', remaining_core_evals)))
        ev: Evaluation = copy.deepcopy(Evaluations.SELECT_N.value)
        ev.get_item_by_ordinal([1]).content = Wording(ev.get_item_by_ordinal([1]).content.content.format(evaluations=s), [])
        ev.get_item_by_ordinal([1]).answer = Answer(AnswerCode.SELECT_EVALUATION, list(map(lambda x: AnswerItem(x[0], 0, Wording(x[1].code.value, x[1].nickcodes)), enumerate(remaining_core_evals))))
        return ev, ev.code.value, None

    if EvaluationCode.TRANSITION_NLP1 not in evals:
        return Evaluations.TRANSITION_NLP1.value, EvaluationCode.TRANSITION_NLP1.value, None

    core_evals_choice_only: list[Evaluation] = [Evaluations.PHQ_9_CO.value, Evaluations.GAD_7_CO.value, Evaluations.PCL_5_CO.value]
    remaining_core_evals_choice_only: list[Evaluation] = [e for e in core_evals_choice_only if e.code not in evals]
    if len(remaining_core_evals_choice_only) == 1:
        x: Evaluation = remaining_core_evals_choice_only[0]
        if topics[-1].evaluation.code == EvaluationCode.ANNOUNCE_LAST:
            return x, x.code.value, None
        ev: Evaluation = copy.deepcopy(Evaluations.ANNOUNCE_LAST.value)
        ev.get_item_by_ordinal([1]).content = Wording(ev.get_item_by_ordinal([1]).content.content.format(code=re.sub("-CO$", "", x.code.value.upper()), name=x.name, action=x.action), [])
        return ev, ev.code.value, None

    if len(remaining_core_evals_choice_only) > 1:
        if topics[-1].evaluation.code == EvaluationCode.SELECT_N:
            ei: EvaluationItem = topics[-1].evaluation.get_item_by_ordinal([1])
            aic = await prctx.matter_dao.get_answer_item_code_by_topic_and_evaluation_item(topics[-1], ei)
            a = ei.answer.items[aic].wording.content
            return Evaluations.get_by_code(EvaluationCode(a+"-co").value), a, None
        s: str = "    " + "\n    ".join(list(map(lambda e: f'* you can {e.action} with the {e.name} ({re.sub("-CO$", "", e.code.value.upper())})', remaining_core_evals_choice_only)))
        ev: Evaluation = copy.deepcopy(Evaluations.SELECT_N.value)
        ev.get_item_by_ordinal([1]).content = Wording(ev.get_item_by_ordinal([1]).content.content.format(evaluations=s), [])
        ev.get_item_by_ordinal([1]).answer = Answer(AnswerCode.SELECT_EVALUATION, list(map(lambda x: AnswerItem(x[0], 0, Wording(re.sub("-[Cc][Oo]$", "", x[1].code.value), x[1].nickcodes)), enumerate(remaining_core_evals_choice_only))))
        return ev, ev.code.value, None

    if EvaluationCode.THANKS not in evals:
        return Evaluations.THANKS.value, EvaluationCode.THANKS.value, None

    return None, None, None


class Studies(Enum):
    INTRO = Study(StudyCode.INTRO, 'Self Introduction', [1], None, None, next_eval__intro)
    DATA_COLLECTION = Study(StudyCode.DATA_COLLECTION, 'Data Collection', [2], None, datetime.datetime(2022, 5, 21, 23, 59, 59, 999, pytz.UTC), next_eval__data_collection)
    NLP1 = Study(StudyCode.NLP1, 'NLP1', [3], [DiscordGuild.AICARE_STAFF, DiscordGuild.AICARE_PHASE_2, DiscordGuild.AICARE_DEV_1, DiscordGuild.AICARE_DEV_2], datetime.datetime(2022, 11, 23, 23, 59, 59, 999, pytz.UTC), next_eval__nlp1)
    NLP1A = Study(StudyCode.NLP1A, 'NLP1A', [4], [DiscordGuild.AICARE_STAFF,  DiscordGuild.AICARE_PHASE_21, DiscordGuild.AICARE_PHASE_22, DiscordGuild.AICARE_DEV_1, DiscordGuild.AICARE_DEV_2], None, next_eval__nlp1a)

    def get_value_by_code(code: str) -> Study:
        for st in Studies:
            if st.value.code.value == code:
                return st.value
        return None


async def next_study(participant: Participant, conn) -> (Study, Discussion):
    discussions: list[Discussion] = await context_free_dao.get_discussions_by_participant(conn, participant)
    if len(discussions) > 0 and discussions[-1].status != DiscussionStatus.COMPLETED:
        return discussions[-1].study, discussions[-1]

    for st in sorted(list(map(lambda s: s.value, Studies)), key=lambda x: x.ordinal):
        if not st.applicable(participant.guild_ids):
            continue
        found = False
        for d in discussions:
            if d.study.code == st.code:
                found = True
                break
        if not found:
            return st, None
    return None, None
