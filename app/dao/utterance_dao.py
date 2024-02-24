import datetime

import discord
from discord import Message, utils

from model.exchange_model import Exchange
from model.utterance_model import Utterance
from common.util import PRCTX


class UtteranceDao:
    async def create_pre_send(self, exchange: Exchange, content: str) -> Utterance:
        prctx = PRCTX.get()
        now = datetime.datetime.now().astimezone()
        rid = await prctx.connection.fetchval('insert into utterance (exchange_id, resent_counter, created_at, updated_at, content) '
                                              'values (                        $1,             $2,         $3,         $3,      $4) '
                                              'returning id',
                                              exchange.id, 0, now, utils.remove_markdown(content))
        r = await prctx.connection.fetchrow('select * from utterance where id = $1', rid)
        return Utterance(r, exchange)

    async def mark_as_sent(self, utterance: Utterance, message: Message):
        prctx = PRCTX.get()
        now = datetime.datetime.now().astimezone()
        await prctx.connection.fetchval('update utterance set sent_at = $1, discord_message_id = $2, discord_created_at = $3, content = $4 where id = $5',
                                        now, message.id, message.created_at, utils.remove_markdown(message.clean_content), utterance.id)

    async def create_received(self, exchange_id: int, message: Message, now):
        prctx = PRCTX.get()
        crat = message.created_at.replace(tzinfo=datetime.timezone.utc)
        edat = None
        if message.edited_at is not None:
            edat = message.created_at.replace(tzinfo=datetime.timezone.utc)
        await prctx.connection.execute('insert into utterance (exchange_id, discord_message_id, content, resent_counter, discord_created_at, discord_edited_at, received_at, created_at, updated_at) '
                                       '               values (         $1,                 $2,      $3,             $4,                 $5,                $6,      $7,           $7,          $7)',
                                       exchange_id, message.id, utils.remove_markdown(message.clean_content), 0, crat, edat, now)

    async def get_by_exchange(self, exchange: Exchange) -> list[Utterance]:
        prctx = PRCTX.get()
        return list(map(lambda r: Utterance(r, exchange), await prctx.connection.fetch('select * from utterance where exchange_id = $1 order by created_at', exchange.id)))

    async def increment_resent_counter(self, utterance: Utterance):
        prctx = PRCTX.get()
        await prctx.connection.execute('update utterance set resent_counter = resent_counter + 1 where id = $1', utterance.id)

    async def record_delivery(self, message: discord.Message, now):
        prctx = PRCTX.get()
        await prctx.connection.execute("update utterance u set delivered_at = $1, updated_at = $1 where discord_message_id = $2 and delivered_at is null", now, message.id)
