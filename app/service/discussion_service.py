from common.util import PRCTX
from model.discussion_model import Discussion
from model.exchange_model import Exchange
from model.matter_model import Matter
from model.topic_model import Topic
from model.utterance_model import Utterance


class DiscussionService:
    async def get_state(self, discussion: Discussion) -> (Topic, Matter, Exchange, Utterance):
        prctx = PRCTX.get()
        topic: Topic = await prctx.topic_dao.get_latest_by_discussion(discussion)
        if topic is None:
            return None, None, None, None
        topic.evaluation = await prctx.evaluation_dao.get_by_hash(topic.evaluation_hash)

        matter: Matter = await prctx.matter_dao.get_latest_by_topic(topic)
        if matter is None:
            return topic, None, None, None

        exchange: Exchange = await prctx.exchange_dao.get_latest_by_matter(matter)
        if exchange is None:
            return topic, matter, None, None
        exchange.answer = await prctx.answer_dao.get_by_hash(exchange.answer_hash)

        exchange.utterances = await prctx.utterance_dao.get_by_exchange(exchange)
        if len(exchange.utterances) == 0:
            return topic, matter, exchange, None

        return topic, matter, exchange, exchange.utterances[-1]
