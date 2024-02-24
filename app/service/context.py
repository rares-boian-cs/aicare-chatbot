from dao.answer_dao import AnswerDao
from dao.discussion_dao import DiscussionDao
from dao.evaluation_dao import EvaluationDao
from dao.exchange_dao import ExchangeDao
from dao.matter_dao import MatterDao
from dao.participant_dao import ParticipantDao
from dao.topic_dao import TopicDao
from dao.utterance_dao import UtteranceDao
from model.discussion_model import Discussion
from model.topic_model import Topic
from model.matter_model import Matter
from model.exchange_model import Exchange
from model.utterance_model import Utterance
from service.discussion_service import DiscussionService
from service.matter_service import MatterService


class ParticipantContext:
    def __init__(self, id: int, discord_id: int, discord_tag: str):
        self.id: int = id
        self.discord_id: int = discord_id
        self.discord_tag: str = discord_tag

        self.participant_dao: ParticipantDao = ParticipantDao()
        self.discussion_dao: DiscussionDao = DiscussionDao()
        self.topic_dao: TopicDao = TopicDao()
        self.evaluation_dao: EvaluationDao = EvaluationDao()
        self.matter_dao: MatterDao = MatterDao()
        self.exchange_dao: ExchangeDao = ExchangeDao()
        self.answer_dao: AnswerDao = AnswerDao()
        self.utterance_dao: UtteranceDao = UtteranceDao()

        self.discussion_service: DiscussionService = DiscussionService()
        self.matter_service: MatterService = MatterService()

        self.connection = None
        self.discussion: Discussion = None
        self.topic: Topic = None
        self.matter: Matter = None
        self.exchange: Exchange = None
        self.utterance: Utterance = None

        self.delay_scale = 1
        self.debug = False
        self.ack_count = 0

        self.wakeup_deadline = None
