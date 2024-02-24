import datetime

from common.constant import MIT, MFST
from common.util import PRCTX
from model.matter_model import Matter
from model.exchange_model import Exchange
from predefined.answer_item_model import AnswerItem
from model.participant_model import Participant


class ExchangeDao:
    async def create(self, matter: Matter, answer_hash: str, matter_flow_state: MFST, target_answer_item_code: str) -> Exchange:
        prctx = PRCTX.get()
        now = datetime.datetime.now().astimezone()
        rid = await prctx.connection.fetchval('insert into exchange (matter_id, answer_hash, matter_flow_state, target_answer_item_code, created_at, updated_at) '
                                              'values (                     $1,          $2,                $3,                      $4,         $5,         $5) '
                                              'returning id',
                                              matter.id, answer_hash, matter_flow_state.value, target_answer_item_code, now)
        r = await prctx.connection.fetchrow('select * from exchange where id = $1', rid)
        return Exchange(r, matter)

    async def get_latest_by_matter(self, matter: Matter) -> Exchange:
        prctx = PRCTX.get()
        r = await prctx.connection.fetchrow('select * from exchange where matter_id = $1 order by created_at desc', matter.id)
        if r is not None:
            return Exchange(r, matter)
        return None

    async def store_transition(self, exchange: Exchange, input_type: MIT, next_state: MFST, answer_item: AnswerItem, ai_input_type: MIT, ai_answer_item: AnswerItem, ai_probabilities: list[float], nonai_input_type: MIT, nonai_answer_item: AnswerItem):
        now = datetime.datetime.now().astimezone()
        query = 'update exchange set input_type = $1, next_matter_flow_state = $2, updated_at = $3'
        params = [input_type.value, next_state.value, now]

        if answer_item is not None:
            params.append(answer_item.code)
            query += f', answer_item_code = ${len(params)}'

        if ai_input_type is not None:
            params.append(ai_input_type.value)
            query += f', ai_input_type = ${len(params)}'

        if ai_answer_item is not None:
            params.append(ai_answer_item.code)
            query += f', ai_answer_item_code = ${len(params)}'

        if ai_probabilities is not None:
            params.append(ai_probabilities)
            query += f', ai_probabilities = ${len(params)}'

        if nonai_input_type is not None:
            params.append(nonai_input_type.value)
            query += f', nonai_input_type = ${len(params)}'

        if nonai_answer_item is not None:
            params.append(nonai_answer_item.code)
            query += f', nonai_answer_item_code = ${len(params)}'

        params.append(exchange.id)
        query += f' where id = ${len(params)}'

        prctx = PRCTX.get()
        await prctx.connection.execute(query, *params)

    async def get_id_of_latest_delivered_by_participant(self, participant: Participant) -> int:
        prctx = PRCTX.get()
        id = await prctx.connection.fetchval('select '
                                             '    u.exchange_id '
                                             'from '
                                             '    utterance u '
                                             '    inner join exchange e on e.id = u.exchange_id '
                                             '    inner join matter m on m.id = e.matter_id '
                                             '    inner join topic t on t.id = m.topic_id '
                                             '    inner join discussion d on d.id = t.discussion_id '
                                             'where '
                                             '    d.participant_id = $1 and '
                                             '    u.delivered_at is not null '
                                             'order by '
                                             '    u.delivered_at desc '
                                             'limit 1', participant.id)

        if id is None:
            id = await prctx.connection.fetchval('select '
                                                 '    u.exchange_id '
                                                 'from '
                                                 '    utterance u '
                                                 '    inner join exchange e on e.id = u.exchange_id '
                                                 '    inner join matter m on m.id = e.matter_id '
                                                 '    inner join topic t on t.id = m.topic_id '
                                                 '    inner join discussion d on d.id = t.discussion_id '
                                                 'where '
                                                 '    d.participant_id = $1 '
                                                 'order by '
                                                 '    u.delivered_at desc '
                                                 'limit 1', participant.id)
        return id