import datetime

from model.topic_model import Topic
from model.matter_model import Matter
from predefined.evaluation_item_model import EvaluationItem
from predefined.answer_item_model import AnswerItem
from common.util import PRCTX


class MatterDao:
    async def create(self, topic: Topic, evaluation_item: EvaluationItem) -> Matter:
        eicode: str = None
        if evaluation_item is not None:
            eicode = evaluation_item.code
        now = datetime.datetime.now().astimezone()
        prctx = PRCTX.get()
        rid = await prctx.connection.fetchval('insert into matter (topic_id, evaluation_item_code, score, created_at, updated_at) '
                                              'values (                  $1,                   $2,    $3,         $4,         $4) '
                                              'returning id',
                                              topic.id, eicode, 0, now)
        r = await prctx.connection.fetchrow('select * from matter where id = $1', rid)
        return Matter(r, topic)

    async def get_answer_item_code_by_topic_and_evaluation_item(self, topic: Topic, evaluation_item: EvaluationItem) -> str:
        prctx = PRCTX.get()
        return await prctx.connection.fetchval('select m.answer_item_code '
                                               'from matter m '
                                               'where m.topic_id = $1 and m.evaluation_item_code = $2', topic.id, evaluation_item.code)

    async def get_latest_by_topic(self, topic: Topic) -> Matter:
        prctx = PRCTX.get()
        r = await prctx.connection.fetchrow('select * from matter where topic_id = $1 order by created_at desc', topic.id)
        if r is not None:
            return Matter(r, topic)
        return None

    async def calculate_answer_item_code(self, matter: Matter) -> str:
        prctx = PRCTX.get()
        return await prctx.connection.fetchval('select coalesce(target_answer_item_code, answer_item_code) '
                                               'from exchange '
                                               'where matter_id = $1 and '
                                               '      (target_answer_item_code is not null or answer_item_code is not null)'
                                               'order by created_at desc '
                                               'limit 1 ', matter.id)

    async def complete(self, matter: Matter, answer_item: AnswerItem):
        now = datetime.datetime.now().astimezone()
        answer_item_code: str = None
        score = 0
        if answer_item is not None:
            answer_item_code = answer_item.code
            score = answer_item.value
        prctx = PRCTX.get()
        await prctx.connection.execute('update matter set updated_at = $1, completed_at = $1, answer_item_code = $2, score = $3 where id = $4', now, answer_item_code, score, matter.id)
