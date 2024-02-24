import datetime
from typing import Any

from common.constant import StudyCode, DiscordGuild
from predefined.evaluation_model import Evaluation


class Study:
    def __init__(self, code: StudyCode, name: str, ordinal: list[int], applicability: list[DiscordGuild], expires_at, fnext):
        self.code: StudyCode = code
        self.name: str = name
        self.ordinal: list[int] = ordinal
        self.applicability: list[DiscordGuild] = applicability
        self.expires_at = expires_at
        self.fnext = fnext

    async def next_eval(self, discussion) -> (Evaluation, str, Any):
        return await self.fnext(discussion)

    def applicable(self, guild_ids: list[int]) -> bool:
        now = datetime.datetime.now().astimezone()
        if self.expires_at is not None and now > self.expires_at:
            return False
        if self.applicability is None:
            return True
        for g in self.applicability:
            if g.value in guild_ids:
                return True
        return False
