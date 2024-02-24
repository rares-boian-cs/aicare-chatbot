from enum import Enum

from predefined.answer_model import Answer
from predefined.answer_item_model import AnswerItem
from predefined.wording_model import Wording
from common.constant import AnswerCode


class Answers(Enum):
    NO_YES_01 = Answer(AnswerCode.NO_YES_01, [
        AnswerItem(0, 1, Wording('yes', ['yeah', 'sure', 'yea', 'yep', 'of course', 'ok', 'aye', 'certainly', 'definitely', 'positively', 'naturally'])),
        AnswerItem(1, 0, Wording('no',  ['nah', 'nope', 'nop', 'no way', 'nay', 'nix', 'not', 'negative', 'not at all', 'absolutely not'])),
    ])
    PROFICIENCY_03 = Answer(AnswerCode.PROFICIENCY_03, [
        AnswerItem(0, 0, Wording('poor', ['inferior', 'mediocre', 'miserable', 'shoddy', 'weak', 'modest', 'shabby'])),
        AnswerItem(1, 1, Wording('acceptable', ['sufficient', 'tolerable', 'decent', 'fair', 'average', 'ok', 'standard'])),
        AnswerItem(2, 2, Wording('good', ['superior', 'super', 'great', 'satisfactory', 'high'])),
        AnswerItem(3, 3, Wording('excellent', ['first-rate', 'outstanding', 'superb', 'very high', 'top-notch'])),
    ])
    GENERAL_FREQUENCY_04 = Answer(AnswerCode.GENERAL_FREQUENCY_04, [
        AnswerItem(0, 0, Wording('never', ['not in any way', 'not in the least', 'not on your life', 'not under any condition', 'no way', 'forget it'])),
        AnswerItem(1, 1, Wording('seldom', ['sporadically', 'hardly ever', 'very few times', 'scarcely ever', 'not very often', 'uncommonly', 'very little'])),
        AnswerItem(2, 2, Wording('sometimes', ['occasionally', 'at times', 'every so often', 'from time to time', 'here and there', 'intermittently', 'now and again'])),
        AnswerItem(3, 3, Wording('usually', ['mostly', 'regularly', 'routinely', 'most often', 'more often than not', 'now and again', 'normally'])),
        AnswerItem(4, 4, Wording('always', ['without exception', 'consistently', 'without exception'])),
    ])
    DAY_FREQUENCY_03 = Answer(AnswerCode.DAY_FREQUENCY_03, [
        AnswerItem(0, 0, Wording('not at all', ['not a bit', 'not likely', 'not measurably', 'not notably', 'not quite'])),
        AnswerItem(1, 1, Wording('several days', ['infrequently', 'a day or two', 'a few days', 'handful of days', 'small number of days', 'some days', 'sparsely'])),
        AnswerItem(2, 2, Wording('more than half the days', ['regularly', 'repeatedly', 'usually', 'time and again', 'time after time', 'oftentimes', 'most of the days'])),
        AnswerItem(3, 3, Wording('nearly every day', ['very often', 'without exception'])),
    ])
    INTENSITY_04 = Answer(AnswerCode.INTENSITY_04, [
        AnswerItem(0, 0, Wording('not at all', ['not a bit', 'not likely', 'not measurably', 'not notably', 'not quite'])),
        AnswerItem(1, 1, Wording('a little bit', ['somewhat', 'scantly', 'slightly', 'brief', 'limited', 'short-lived', 'sparse'])),
        AnswerItem(2, 2, Wording('moderately', ['fairly ', ' rather', 'more or less', 'averagely', 'so-so', 'sort of', 'within reason', 'within limits'])),
        AnswerItem(3, 3, Wording('quite a bit', ['all in all', 'considerably', 'positively', 'altogether', 'really', 'actually', 'absolutely'])),
        AnswerItem(4, 4, Wording('extremely', ['exceedingly', 'exceptionally', 'excessively', 'highly', 'hugely', 'intensely', 'severely'])),
    ])
    AGREE_04 = Answer(AnswerCode.AGREE_04, [
        AnswerItem(0, 0, Wording('strongly disagree', ['heavily differ', 'firmly differ', 'fully disagree', 'steadily disagree', 'heavily disagree', 'solidly disagree', 'heartily disagree'])),
        AnswerItem(1, 1, Wording('disagree', ['diverge', 'dissent', 'disaccord', 'contend', 'oppose', 'dispute', 'take issue'])),
        AnswerItem(2, 2, Wording('neutral', ['indeterminate', 'unaligned', 'undecided', 'indistinct', 'equally', 'impartial', 'in the middle'])),
        AnswerItem(3, 3, Wording('agree', ['accede', 'concede', 'conform', 'in accord', 'in concert', 'subscribe', 'yes'])),
        AnswerItem(4, 4, Wording('strongly agree', ['firmly accede', 'firmly concede', 'steadily admit', 'steadily concur', 'steadily recognize', 'steadily accede', 'steadily concede'])),
    ])
    RATE_04 = Answer(AnswerCode.RATE_04, [
        AnswerItem(0, 0, Wording('very slow', ['exceedingly slow', 'excessively slow', 'extremely slow', 'incredibly slow', 'pretty slow'])),
        AnswerItem(1, 1, Wording('slow', ['slow-moving', 'snaillike', 'crawling', 'lethargic', 'ponderous', 'leaden'])),
        AnswerItem(2, 2, Wording('suitable', ['reasonable', 'satisfactory', 'sufficient', 'fitting', 'ok', 'appropriate'])),
        AnswerItem(3, 3, Wording('fast', ['rapid', 'swift', 'racing', 'expeditious', 'expeditive', 'snappy'])),
        AnswerItem(4, 4, Wording('very fast', ['exceedingly fast', 'excessively fast', 'extremely fast', 'incredibly fast'])),
    ])
    DIFFICULTY_04 = Answer(AnswerCode.DIFFICULTY_04, [
        AnswerItem(0, 0, Wording('very difficult', ['exceedingly difficult', 'excessively difficult', 'extremely difficult', 'incredibly difficult', 'pretty difficult'])),
        AnswerItem(1, 1, Wording('difficult', ['painful', 'strenuous', 'tough', 'effortful', 'difficile', 'trying', 'severe'])),
        AnswerItem(2, 2, Wording('normal', ['routine', 'typical', 'average', 'standard', 'common', 'ok'])),
        AnswerItem(3, 3, Wording('easy', ['smooth', 'straightforward', 'uncomplicated', 'child''s play', 'facile', 'plain'])),
        AnswerItem(4, 4, Wording('very easy', ['exceedingly easy', 'excessively easy', 'extremely easy', 'incredibly easy', 'pretty easy'])),
    ])
    SATISFACTION_04 = Answer(AnswerCode.SATISFACTION_04, [
        AnswerItem(0, 0, Wording('very dissatisfied', ['exceedingly dissatisfied', 'excessively dissatisfied', 'extremely dissatisfied', 'incredibly dissatisfied', 'pretty dissatisfied'])),
        AnswerItem(1, 1, Wording('dissatisfied', ['disaffected', 'disgruntled', 'displeased', 'frustrated', 'offended', 'unhappy', 'unsatisfied'])),
        AnswerItem(2, 2, Wording('satisfied', ['pleased', 'gratified', 'sated', 'ok'])),
        AnswerItem(3, 3, Wording('quite satisfied', ['positively', 'altogether', 'really', 'actually'])),
        AnswerItem(4, 4, Wording('very satisfied', ['exceedingly satisfied', 'excessively satisfied', 'extremely satisfied', 'incredibly satisfied', 'pretty satisfied'])),
    ])
    GENDER_5 = Answer(AnswerCode.GENDER_5, [
        AnswerItem(0, 0, Wording('female', [])),
        AnswerItem(1, 0, Wording('male', [])),
        AnswerItem(2, 0, Wording('non-binary', [])),
        AnswerItem(3, 0, Wording('transgender', [])),
        AnswerItem(4, 0, Wording('other', []))
    ])

    def get_by_code(code: str) -> Answer:
        for an in Answers:
            if an.value.code.value == code:
                return an
        return None
