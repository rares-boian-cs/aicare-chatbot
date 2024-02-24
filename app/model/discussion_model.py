import asyncpg

from common.constant import DiscussionStatus
from predefined.study_model import Study


class Discussion:
    def __init__(self, rec: asyncpg.Record, participant, study: Study):
        self.id: str = rec["id"]
        self.study: Study = study
        self.participant = participant
        self.round: int = rec["round"]
        self.status: DiscussionStatus = DiscussionStatus(rec["status"])
        self.created_at = rec["created_at"]
        self.updated_at = rec["updated_at"]
        self.completed_at = rec["completed_at"]
