from common.constant import EIT
from common.util import PRCTX
from predefined.answer_model import Answer
from predefined.wording_model import Wording


class EvaluationItem:
    def __init__(self, ordinal: list[int], item_type: EIT, countable: bool, answer: Answer, acknowledgment_set: dict[str, Wording], action, nextord, content: Wording):
        self.code: str = ''
        self.ordinal: list[int] = ordinal
        self.countable: bool = countable
        self.item_type: EIT = item_type
        self.answer: Answer = answer
        self.acknowledgment_set: dict[str, Wording] = acknowledgment_set
        self.content: Wording = content
        self.action = action
        self.nextord = nextord
        self.next = None if nextord is None else lambda: nextord(PRCTX.get()) if callable(nextord) else nextord

    async def post_action(self):
        if self.action is not None:
            await self.action(PRCTX.get())

    def get_content(self):
        c = self.content.get_random()
        if self.item_type == EIT.CHOICE:
            c += '\n' + self.answer.get_bullets()
        return c