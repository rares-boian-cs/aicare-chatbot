import asyncio


class Participant:
    def __init__(self, id: int, discord_id: int, discord_tag: str):
        self.id: int = id
        self.discord_id: int = discord_id
        self.discord_tag: str = discord_tag
        self.lock = asyncio.Lock()
        self.active_handler = False
        self.queue: asyncio.Queue = asyncio.Queue()
        self.delay_scale = 1.0
        self.debug = False
        self.guild_ids: list[int] = []