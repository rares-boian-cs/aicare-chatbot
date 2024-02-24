from enum import Enum, auto


COMMAND_MARKER = '!!!'

STAFF: list[str] = []

class ParticipantGroup(Enum):
    OTHER = 'other'
    STAFF = 'staff'


class DiscussionStatus(Enum):
    ACTIVE = 'active'
    COMPLETED = 'completed'
    HOLD = 'hold'


class DST(Enum):  # Discussion STate
    INCO = auto()  # incomplete
    COMP = auto()  # complete


class TST(Enum):  # Topic STate
    INCO = auto()  # incomplete
    COMP = auto()  # complete


class MST(Enum):  # Matter STate
    INCO = auto()  # incomplete
    CONL = auto()  # completed-not-last
    COLA = auto()  # completed-last


class EST(Enum):  # Exchange STate
    INWA = auto()  # incomplete-waiting
    INFO = auto()  # incomplete-forgotten
    INFO2 = auto() # incomplete-forgotten-2
    INYO = auto()  # incomplete-young
    INUN = auto()  # incomplete-unprocessed
    CONL = auto()  # completed-not-last
    COLA = auto()  # completed-last


class UST(Enum):  # Utterance STate
    SENT = auto()  # sent but not delivered
    DLVR = auto()  # sent and delivered
    DNAN = auto()  # sent and delivered, no answer needed
    RCVD = auto()  # sent, delivered, and received a response


class EIT(Enum): # Evaluation Item Type
    CHOICE = 'choice'
    OPEN = 'open'
    DUAL = 'dual'
    NONE = 'none'


class MFST(Enum):  # Matter Flow STate
    ASK = 'ask'
    ASK_OPEN = 'ask-open'
    ASK_CHOICE = 'ask-choice'
    CLARIFY_C = 'clarify-c'
    CLARIFY_AC = 'clarify-ac'
    COMPLETED = 'completed'
    CONFIRM = 'confirm'


class MIT(Enum):  # Matter Input Type
    EXACT = 'exact' # Input identifies without doubt one of the answer items
    OTHER = 'other' # Open/descriptive/free answer
    EXACT_AND_OTHER = 'exact-and-other' # Input identifies without doubt one of the answer items and also contains open/descriptive/free text
    AGREE = 'agree' # Like CHOICE, but specific to the CONFIRM state
    DISAGREE = 'disagree' # Like CHOICE, but specific to the CONFIRM state
    MATCHING = 'matching' # Input identifies one of the answer items but requires confirmation


class Matching(Enum):
    EQUAL_ONLY = auto()
    INCLUDED_ONLY = auto()
    BOTH = auto()


class AcknowledgmentCode(Enum):
    CHEERFUL = 'cheerful'
    NEUTRAL = 'neutral'
    SYMPATHETIC = 'medium'
    CONCERNED = 'concerned'
    SYMPATHETIC_PHQ_9 = 'sympathetic-phq-9'
    CONCERNED_PHQ_9 = 'concerned-phq-9'
    SYMPATHETIC_PCL_5 = 'sympathetic-pcl-5'
    CONCERNED_PCL_5 = 'concerned-pcl-5'


class AnswerCode(Enum):
    NO_YES_01 = 'no-yes-01'
    PROFICIENCY_03 = 'proficiency-03'
    GENERAL_FREQUENCY_04 = 'general-frequency-04'
    DAY_FREQUENCY_03 = 'day-frequency-03'
    INTENSITY_04 = 'intensity-04'
    AGREE_04 = 'agree-04'
    RATE_04 = 'rate-04'
    DIFFICULTY_04 = 'difficulty-04'
    SATISFACTION_04 = 'satisfaction-04'
    GENDER_5 = 'gender-5'
    SELECT_EVALUATION = 'select-evaluation'


class EvaluationCode(Enum):
    INTRO = 'intro'
    CONSENT_DATA_COLLECTION = 'consent-data-collection'
    CONSENT_NLP1 = 'consent-nlp1'
    DEMOGRAPHICS = 'demographics'
    PHQ_9 = 'phq-9'
    GAD_7 = 'gad-7'
    PCL_5 = 'pcl-5'
    PHQ_9_CO = 'phq-9-co'
    GAD_7_CO = 'gad-7-co'
    PCL_5_CO = 'pcl-5-co'
    USABILITY_1 = 'usability-1'
    USABILITY_2 = 'usability-2'
    TRANSITION_NLP1 = 'transition-nlp1'
    THANKS = 'thanks'
    SELECT_N = 'select-n'
    ANNOUNCE_LAST = 'announce-last'


class StudyCode(Enum):
    INTRO = 'intro'
    DATA_COLLECTION = 'data-collection'
    NLP1 = 'nlp1'
    NLP1A = 'nlp1a'


class DiscordGuild(Enum):
    AICARE = 123
    AICARE_PHASE_2 = 234
    AICARE_PHASE_21 = 345
    AICARE_PHASE_22 = 456
    AICARE_STAFF = 567
    AICARE_DEV_1 = 678
    AICARE_DEV_2 = 789

    def get_name_by_value(v) -> str:
        for dg in DiscordGuild:
            if dg.value == v:
                return dg.name
        return None


class EvalStateResult(Enum):
    CONTINUE = auto()
    WAIT_FOR_MESSAGE = auto()
    WAIT_FOR_DEADLINE_OR_MESSAGE = auto()
    STOP = auto()
