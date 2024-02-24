import asyncpg

from common.constant import MST
from model.exchange_model import Exchange
from predefined.answer_item_model import AnswerItem
from predefined.evaluation_item_model import EvaluationItem


class Matter:
    def __init__(self, rec: asyncpg.Record, topic):
        self.id: int = rec["id"]
        self.topic = topic
        self.evaluation_item: EvaluationItem = topic.evaluation.items[rec["evaluation_item_code"]]
        self.answer_item: AnswerItem = None
        if rec["answer_item_code"] is not None:
            self.answer_item: AnswerItem = self.evaluation_item.answer.items[rec["answer_item_code"]]
        self.created_at = rec["created_at"]
        self.updated_at = rec["updated_at"]
        self.completed_at = rec["completed_at"]
        self.exchanges: list[Exchange] = []

    def discussion_flow_state(self) -> MST:
        if self.completed_at is None:
            return MST.INCO
        if self.topic.evaluation.next_item(self.evaluation_item) is None:
            return MST.COLA
        return MST.CONL

    async def post_action(self):
        await self.evaluation_item.post_action()