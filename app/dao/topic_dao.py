import datetime
import math

import numpy

from model.discussion_model import Discussion
from model.topic_model import Topic
from predefined.evaluation_model import Evaluation
from predefined.evaluation_item_model import EvaluationItem
from common.util import PRCTX, config


class TopicDao:
    async def create(self, evaluation: Evaluation, code: str, discussion: Discussion) -> Topic:
        now = datetime.datetime.now().astimezone()
        _, hash = evaluation.json()

        countable: list[EvaluationItem] = evaluation.get_countable_items()
        dist = numpy.zeros(len(countable))
        p = math.floor(config.get_float('application', 'acknowledgment-ratio') * len(countable))
        dist[:p] = 1
        numpy.random.shuffle(dist)
        toack: list[str] = []
        for k, v in enumerate(dist):
            if v == 1:
                toack.append(countable[k].code)

        prctx = PRCTX.get()
        rid = await prctx.connection.fetchval('insert into topic (code, discussion_id, evaluation_hash, to_acknowledge, created_at, updated_at) '
                                              'values (             $1,            $2,              $3,             $4,         $5,         $5) '
                                              'returning id',
                                              code, discussion.id, hash, toack, now)
        r = await prctx.connection.fetchrow('select * from topic where id = $1', rid)
        t = Topic(r, discussion)
        t.evaluation = evaluation
        return t

    async def get_by_discussion(self, discussion: Discussion) -> list[Topic]:
        prctx = PRCTX.get()
        return list(map(lambda r: Topic(r, discussion),
                        await prctx.connection.fetch('select t.*, e.obj '
                                                     'from topic t'
                                                     '     inner join evaluation e on t.evaluation_hash = e.hash '
                                                     'where t.discussion_id = $1 '
                                                     'order by t.created_at', discussion.id)))

    async def get_latest_by_discussion(self, discussion: Discussion) -> Topic:
        prctx = PRCTX.get()
        r = await prctx.connection.fetchrow('select t.*, e.obj '
                                            'from topic t'
                                            '     inner join evaluation e on t.evaluation_hash = e.hash '
                                            'where t.discussion_id = $1 '
                                            'order by t.created_at desc', discussion.id)
        if r is not None:
            return Topic(r, discussion)
        return None

    async def calculate_score(self, topic: Topic) -> int:
        prctx = PRCTX.get()
        return await prctx.connection.fetchval('select sum(score) from matter where topic_id = $1', topic.id)

    async def complete(self, topic: Topic):
        prctx = PRCTX.get()
        now = datetime.datetime.now().astimezone()
        await prctx.connection.execute('update topic set updated_at = $1, completed_at = $1, score = (select sum(score) from matter where topic_id = $2) where id = $2', now, topic.id)
