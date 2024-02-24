import asyncpg

from common.constant import UST, EIT


class Utterance:
    def __init__(self, rec: asyncpg.Record, exchange):
        self.id: int = rec["id"]
        self.content: str = rec["content"]
        self.discord_message_id: int = rec["discord_message_id"]
        self.sent_at = rec["sent_at"]
        self.delivered_at = rec["delivered_at"]
        self.received_at = rec["received_at"]
        self.resent_counter = rec["resent_counter"]
        self.created_at = rec["created_at"]
        self.updated_at = rec["updated_at"]
        self.exchange = exchange

    def discussion_flow_state(self) -> UST:
        if self.received_at is not None:
            if self.exchange.matter.evaluation_item.item_type == EIT.NONE:
                return UST.DNAN
            return UST.RCVD
        if self.delivered_at is not None:
            if self.exchange.matter.evaluation_item.item_type == EIT.NONE:
                return UST.DNAN
            return UST.DLVR
        return UST.SENT