import asyncpg

from common.constant import TST
from predefined.evaluation_model import Evaluation


class Topic:
    def __init__(self, rec: asyncpg.Record, discussion):
        self.id: int = rec["id"]
        self.code: str = rec["code"]
        self.discussion = discussion
        self.evaluation_hash: str = rec["evaluation_hash"]
        self.to_acknowledge: list[str] = rec["to_acknowledge"]
        self.evaluation: Evaluation = None
        self.created_at = rec["created_at"]
        self.updated_at = rec["updated_at"]
        self.completed_at = rec["completed_at"]
        self.score = rec["score"]

    def discussion_flow_state(self) -> TST:
        if self.completed_at is not None:
            return TST.COMP
        return TST.INCO