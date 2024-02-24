import asyncpg


class ParticipantReport:
    def __init__(self, rec: asyncpg.Record):
        self.participant_name: str = rec['participant_name']
        self.guild_names: str = rec['guild_names']
        self.participant_name: str = rec['participant_name']
        self.last_heard_from: str = rec['last_heard_from']
        self.status: str = rec['status']
        self.evaluations: str = rec['evaluations']