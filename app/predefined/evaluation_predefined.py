from enum import Enum

from common.constant import EIT, EvaluationCode
from common.util import switch, noop
from model.discussion_model import DiscussionStatus
from predefined.acknowledgment_predefined import AcknowledgmentSets
from predefined.answer_predefined import Answers
from predefined.evaluation_model import Evaluation
from predefined.evaluation_item_model import EvaluationItem
from predefined.wording_model import Wording


class TONE(Enum):
    HAPPY = 'happy'
    NEUTRAL = "neutral"
    SYMPATHETIC = "sympathetic"


class WORDING(Enum):
    EVAL_END_1 = Wording('That question finalized your {evaluation-code} survey. Hope you found it time well spent. Let’s check your results.', [])
    EVAL_END_2 = Wording('That was your last {evaluation-code} question. I am sure you are curious about the results. Now, let\'s see.', [])
    EVAL_END_3 = Wording('That last question marked the end of your {evaluation-code} journey. Time to check your results.', [])
    ASK_CHOICE = Wording('Please specify which of the following describes your answer best:', [])
    ASK_OPEN = Wording('Can you also put this into a casual your-own-words answer?', [])
    CLARIFY = Wording('Please answer with one of the options below:', ['I didn\'t get that ... could you answer with one of the options below?',
                                                                       'Sorry, I\'m not very clear what you mean. Could give me one of the options below?'])
    CONFIRM = Wording('Should I understand that your answer is ', [])


class Evaluations(Enum):
    INTRO = Evaluation(EvaluationCode.INTRO, [], '', '', [
        EvaluationItem([1], EIT.NONE, False, None, None, None, None, Wording('Hello, my name is aiCARE and I am an artificial intelligence chatbot, or learning to become one, although I prefer the term "artificial person" myself. To become more like a real person, I need to learn a lot of stuff. My aim is to someday be able to tell when people are sad, or afraid or feeling down, and to help them get better. You, and other people like you, could help me achieve those things by chatting a little with me. Now, let me explain how.', []))
    ])
    CONSENT_DATA_COLLECTION = Evaluation(EvaluationCode.CONSENT_DATA_COLLECTION, [], '', '', [
        EvaluationItem([1], EIT.CHOICE, False, Answers.NO_YES_01.value, None,
                       lambda ctx: switch(ctx.matter.answer_item.code, 'no-yes-01:1', lambda _: ctx.discussion_dao.set_status(ctx.discussion, DiscussionStatus.HOLD), lambda _: noop()),
                       lambda ctx: switch(ctx.matter.answer_item.code, 'no-yes-01:1', [2,-1], [2,-2]),
                       Wording('The participation in this pilot study involves interacting with the aiCARE intelligent chatbot. This study is conducted by Dr. Ioana Podina from the Faculty of Psychology and Educational Sciences, University of Bucharest. The informed consent at the address below will detail this part of the study, explain the purpose of the research, what will happen during it, as well as the benefits, potential risks and inconveniences. <https://forms.gle/Y83H1kZvyhwMw55Q9> Keep in mind, the chatbot is a work in progress and your responses contribute to its ongoing training and improvement. It is by no means a diagnosis tool. After reading this information, do you consent to be a participant of this study?', [])),
        EvaluationItem([2,-1], EIT.NONE, False, None, None, None, lambda ctx: [1], Wording('Got it. If you change your mind, just drop me a line. Take care!', [])),
        EvaluationItem([2,-2], EIT.NONE, False, None, None, None, None, Wording("""Great, let’s get started! But, before we do, let me explain the rules of our interaction. I'm currently in a learning phase. As a result, our interaction will be the following
(1) I'll ask you a question, (2) you'll respond openly, (3) and then I'll check to see if I understood correctly, giving you several response options.
Example: 
        (1) Question: Are you in a good mood this week?
        (2) Open response: Never been better
        (3) Check: Please specify which of the following describes your answer best:
               a) not at all
               b) somewhat
               c) great
               d) excellent
In this particular case, the response that would fit the open response best would be excellent. If you were to choose excellent, you could write either the word (excellent) or its corresponding letter (d). No worries, I will understand either way. 

Once you have completed all of the questions about depression, anxiety, and chronic stress, a series of other questions about your experience with me will follow. Thank you for the opportunity to learn from you!
""", []))
    ])
    CONSENT_NLP1 = Evaluation(EvaluationCode.CONSENT_NLP1, [], '', '', [
        EvaluationItem([1], EIT.CHOICE, False, Answers.NO_YES_01.value, None,
                       lambda ctx: switch(ctx.matter.answer_item.code, 'no-yes-01:1', lambda _: ctx.discussion_dao.set_status(ctx.discussion, DiscussionStatus.HOLD), lambda _: noop()),
                       lambda ctx: switch(ctx.matter.answer_item.code, 'no-yes-01:1', [2,-1], [2,-2]),
                       Wording("""I am part of a pilot study that involves interacting with me, the aiCARE intelligent chatbot. This study is conducted by Dr. Ioana Podina from the Faculty of Psychology and Educational Sciences, University of Bucharest. The informed consent at the address below will explain the purpose of the study, what will happen during it, as well as the potential risks and benefits. You can access here the informed consent <https://forms.gle/Y83H1kZvyhwMw55Q9> Keep in mind, the chatbot is a work in progress and your responses contribute to its ongoing training and improvement. It is by no means a diagnosis tool.  

After reading this information, do you consent to take part in the study?""", [])),
        EvaluationItem([2,-1], EIT.NONE, False, None, None, None, lambda ctx: [1], Wording('Got it. If you change your mind, just drop me a line. Take care!', [])),
        EvaluationItem([2,-2], EIT.NONE, False, None, None, None, None, Wording("Great, let’s get started! But, before we do, let me explain the rules for our interaction.", [])),
        EvaluationItem([3,1], EIT.NONE, False, None, None, None, None, Wording("""I'm currently in a learning phase, so be kind and patient \N{smiling face with smiling eyes}. As a result, our interaction will consist in 3 main steps:
(1) I'll ask you a question, (2) you'll respond freely (3) and then, ONLY if needed, I will check to see if I understood correctly, giving you several response options.

Example of possible conversations: 
(1) Me: Are you in a good mood this week?
(2) You: Never been better
(3) Me: Please specify which of the following describes your answer best:
       a) not at all
       b) somewhat
       c) great
       d) excellent""", [])),
        EvaluationItem([3,2], EIT.NONE, False, None, None, None, None, Wording("Therefore, sometimes I need to understand your answer better and will ask for clarification or confirmation, as above, other times it is easy for me to understand. I definitely appreciate you having patience with me.", [])),
        EvaluationItem([3,3], EIT.NONE, False, None, None, None, None, Wording("Once you have answered all the questions about depression, anxiety, and chronic stress, a series of other questions about your experience with me will follow. At the end, I will ask you the same series of questions about anxiety, depression, and chronic stress again, this time in the form of a standard questionnaire. This will help me match your open-ended responses with your closed-ended responses. So, take it easy, no need to rush & thank you for the opportunity to learn from you!", []))
    ])
    DEMOGRAPHICS = Evaluation(EvaluationCode.DEMOGRAPHICS, [], '', '', [
        EvaluationItem([1], EIT.NONE, False, None, None, None, None, Wording('Now, let’s get to know each other a bit', [])),
        EvaluationItem([2], EIT.CHOICE, False, Answers.GENDER_5.value, None,
                       lambda ctx: ctx.discussion_dao.set_participant_gender(ctx.discussion, ctx.exchange.get_joined_received_utterances()),
                       None, Wording('The gender that you identify with is:', [])),
        EvaluationItem([3], EIT.OPEN, False, None, None,
                       lambda ctx: ctx.discussion_dao.set_participant_age(ctx.discussion, ctx.exchange.get_joined_received_utterances()),
                       None, Wording('Your age is?', [])),
        EvaluationItem([4], EIT.CHOICE, False, Answers.PROFICIENCY_03.value, None,
                       lambda ctx: ctx.discussion_dao.set_participant_english_proficiency(ctx.discussion, ctx.exchange.get_joined_received_utterances()),
                       None, Wording('What is your proficiency in English?', [])),
        EvaluationItem([5], EIT.CHOICE, False, Answers.NO_YES_01.value, None, None,
                       lambda ctx: switch(ctx.matter.answer_item.code, 'no-yes-01:1', [7], [6]),
                       Wording("Are you receiving research credit/bonus for participating in this study?", [])),
        EvaluationItem([6], EIT.OPEN, False, None, None,
                       lambda ctx: ctx.discussion_dao.set_participant_identification(ctx.discussion, ctx.exchange.get_joined_received_utterances()),
                       None, Wording("""Please tell me your university and faculty name/year of study/full name or student ID""", [])),
        EvaluationItem([7], EIT.NONE, False, None, None, None, None, Wording('Ok', ['Got it', 'Alright'])),
    ])
    PHQ_9 = Evaluation(EvaluationCode.PHQ_9, ['phq9', 'phq'], 'Patient Health Questionnaire', 'check your mood level', [
        EvaluationItem([1],  EIT.DUAL, True, Answers.DAY_FREQUENCY_03.value, AcknowledgmentSets.COMMON.value,       None, None, Wording('[PHQ-9  1/9]  Over the last two weeks, how often did you feel little interest or pleasure in doing things?', [])),
        EvaluationItem([2],  EIT.DUAL, True, Answers.DAY_FREQUENCY_03.value, AcknowledgmentSets.COMMON.value,       None, None, Wording('[PHQ-9  2/9]  Over the last two weeks, how often did you feel down, depressed, or hopeless?', [])),
        EvaluationItem([3],  EIT.DUAL, True, Answers.DAY_FREQUENCY_03.value, AcknowledgmentSets.COMMON.value,       None, None, Wording('[PHQ-9  3/9]  Over the last two weeks, how often did you have trouble falling or staying asleep, or sleeping too much?', [])),
        EvaluationItem([4],  EIT.DUAL, True, Answers.DAY_FREQUENCY_03.value, AcknowledgmentSets.COMMON.value,       None, None, Wording('[PHQ-9  4/9]  Over the last two weeks, how often did you feel tired or as having little energy?', [])),
        EvaluationItem([5],  EIT.DUAL, True, Answers.DAY_FREQUENCY_03.value, AcknowledgmentSets.COMMON.value,       None, None, Wording('[PHQ-9  5/9]  Over the last two weeks, how often have you had a poor appetite, or you were overeating?', [])),
        EvaluationItem([6],  EIT.DUAL, True, Answers.DAY_FREQUENCY_03.value, AcknowledgmentSets.COMMON.value,       None, None, Wording('[PHQ-9  6/9]  Over the last two weeks, how often did you feel bad about yourself - or that you are a failure or have let yourself or your family down?', [])),
        EvaluationItem([7],  EIT.DUAL, True, Answers.DAY_FREQUENCY_03.value, AcknowledgmentSets.COMMON.value,       None, None, Wording('[PHQ-9  7/9]  Over the last two weeks, how often did you have trouble concentrating on things, such as reading the newspaper or watching television?', [])),
        EvaluationItem([8],  EIT.DUAL, True, Answers.DAY_FREQUENCY_03.value, AcknowledgmentSets.COMMON.value,       None, None, Wording('[PHQ-9  8/9]  Over the last two weeks, how often did you move or speak so slowly that other people could have noticed? Or the opposite - being so fidgety or restless that you have been moving around a lot more than usual?', [])),
        EvaluationItem([9],  EIT.DUAL, True, Answers.DAY_FREQUENCY_03.value, AcknowledgmentSets.CAREFUL_LAST.value, None, None, Wording('[PHQ-9  9/9]  Over the last two weeks, how often did you have thoughts that you would be better off dead, or of hurting yourself in some way?', [])),
        EvaluationItem([10], EIT.NONE, False, None, None, None,
                       lambda ctx: switch(ctx.topic.score, lambda x: x <= 4, [11,-1], lambda x: x <= 9, [11,-2], lambda x: x <= 14, [11,-3], lambda x: x <= 19, [11,-4], [11,-5]),
                       WORDING.EVAL_END_1.value),  # TODO alternative eval-end based on last item's answer
        EvaluationItem([11,-1], EIT.NONE, False, None, None, None, None, Wording('Congratulations! Your PHQ-9 score of {topic-score} shows no signs or symptoms of depression.', [])),
        EvaluationItem([11,-2], EIT.NONE, False, None, None, None, None, Wording('Your PHQ-9 score is {topic-score}, which suggests that you may be experiencing mild depression symptoms. Take precautions, and if your depression symptoms are interfering with your daily life, I recommend having your mental health monitored more frequently.', [])),
        EvaluationItem([11,-3], EIT.NONE, False, None, None, None, None, Wording('Your PHQ-9 score is {topic-score}, which indicates that you are experiencing symptoms of moderate depression. Please consider seeking help from a mental health professional if your mood continues to be low.', [])),
        EvaluationItem([11,-4], EIT.NONE, False, None, None, None, None, Wording('Your PHQ-9 score is {topic-score}, which indicates that you are experiencing symptoms of moderately severe major depression. I recommend seeking a specialist for further screening.', [])),
        EvaluationItem([11,-5], EIT.NONE, False, None, None, None, None, Wording('Your PHQ-9 score is {topic-score}, which indicates that you are experiencing symptoms of a severe form of major depression. I highly recommend seeking a specialist for further screening.', [])),
    ])
    PHQ_9_CO = Evaluation(EvaluationCode.PHQ_9_CO, ['phq9', 'phq'], 'Patient Health Questionnaire', 'check your mood level', [
        EvaluationItem([1],  EIT.CHOICE, True,  Answers.DAY_FREQUENCY_03.value, None, None, None, Wording('[PHQ-9  1/9]  Over the last two weeks, how often did you feel little interest or pleasure in doing things?', [])),
        EvaluationItem([2],  EIT.CHOICE, True,  Answers.DAY_FREQUENCY_03.value, None, None, None, Wording('[PHQ-9  2/9]  Over the last two weeks, how often did you feel down, depressed, or hopeless?', [])),
        EvaluationItem([3],  EIT.CHOICE, True,  Answers.DAY_FREQUENCY_03.value, None, None, None, Wording('[PHQ-9  3/9]  Over the last two weeks, how often did you have trouble falling or staying asleep, or sleeping too much?', [])),
        EvaluationItem([4],  EIT.CHOICE, True,  Answers.DAY_FREQUENCY_03.value, None, None, None, Wording('[PHQ-9  4/9]  Over the last two weeks, how often did you feel tired or as having little energy?', [])),
        EvaluationItem([5],  EIT.CHOICE, True,  Answers.DAY_FREQUENCY_03.value, None, None, None, Wording('[PHQ-9  5/9]  Over the last two weeks, how often have you had a poor appetite, or you were overeating?', [])),
        EvaluationItem([6],  EIT.CHOICE, True,  Answers.DAY_FREQUENCY_03.value, None, None, None, Wording('[PHQ-9  6/9]  Over the last two weeks, how often did you feel bad about yourself - or that you are a failure or have let yourself or your family down?', [])),
        EvaluationItem([7],  EIT.CHOICE, True,  Answers.DAY_FREQUENCY_03.value, None, None, None, Wording('[PHQ-9  7/9]  Over the last two weeks, how often did you have trouble concentrating on things, such as reading the newspaper or watching television?', [])),
        EvaluationItem([8],  EIT.CHOICE, True,  Answers.DAY_FREQUENCY_03.value, None, None, None, Wording('[PHQ-9  8/9]  Over the last two weeks, how often did you move or speak so slowly that other people could have noticed? Or the opposite - being so fidgety or restless that you have been moving around a lot more than usual?', [])),
        EvaluationItem([9],  EIT.CHOICE, True,  Answers.DAY_FREQUENCY_03.value, None, None, None, Wording('[PHQ-9  9/9]  Over the last two weeks, how often did you have thoughts that you would be better off dead, or of hurting yourself in some way?', [])),
        EvaluationItem([10], EIT.NONE, False, None, None, None,
                       lambda ctx: switch(ctx.topic.score, lambda x: x <= 4, [11,-1], lambda x: x <= 9, [11,-2], lambda x: x <= 14, [11,-3], lambda x: x <= 19, [11,-4], [11,-5]),
                       WORDING.EVAL_END_1.value),  # TODO alternative eval-end based on last item's answer
        EvaluationItem([11,-1], EIT.NONE, False, None, None, None, None, Wording('Congratulations! Your PHQ-9 score of {topic-score} shows no signs or symptoms of depression.', [])),
        EvaluationItem([11,-2], EIT.NONE, False, None, None, None, None, Wording('Your PHQ-9 score is {topic-score}, which suggests that you may be experiencing mild depression symptoms. Take precautions, and if your depression symptoms are interfering with your daily life, I recommend having your mental health monitored more frequently.', [])),
        EvaluationItem([11,-3], EIT.NONE, False, None, None, None, None, Wording('Your PHQ-9 score is {topic-score}, which indicates that you are experiencing symptoms of moderate depression. Please consider seeking help from a mental health professional if your mood continues to be low.', [])),
        EvaluationItem([11,-4], EIT.NONE, False, None, None, None, None, Wording('Your PHQ-9 score is {topic-score}, which indicates that you are experiencing symptoms of moderately severe major depression. I recommend seeking a specialist for further screening.', [])),
        EvaluationItem([11,-5], EIT.NONE, False, None, None, None, None, Wording('Your PHQ-9 score is {topic-score}, which indicates that you are experiencing symptoms of a severe form of major depression. I highly recommend seeking a specialist for further screening.', [])),
    ])
    GAD_7 = Evaluation(EvaluationCode.GAD_7, ['gad7', 'gad'], 'General Anxiety Disorder questionnaire', 'check your anxiety level', [
        EvaluationItem([1], EIT.DUAL, True, Answers.DAY_FREQUENCY_03.value, AcknowledgmentSets.COMMON.value,      None, None, Wording('[GAD-7  1/7]  Over the last 2 weeks, how often have you been feeling nervous, anxious or on edge?', [])),
        EvaluationItem([2], EIT.DUAL, True, Answers.DAY_FREQUENCY_03.value, AcknowledgmentSets.COMMON.value,      None, None, Wording('[GAD-7  2/7]  Over the last 2 weeks, how often did you find yourself not being able to stop or control worrying?', [])),
        EvaluationItem([3], EIT.DUAL, True, Answers.DAY_FREQUENCY_03.value, AcknowledgmentSets.COMMON.value,      None, None, Wording('[GAD-7  3/7]  Over the last 2 weeks, how often have you been worrying too much about different things?', [])),
        EvaluationItem([4], EIT.DUAL, True, Answers.DAY_FREQUENCY_03.value, AcknowledgmentSets.COMMON.value,      None, None, Wording('[GAD-7  4/7]  Over the last 2 weeks, how often did you have trouble relaxing?', [])),
        EvaluationItem([5], EIT.DUAL, True, Answers.DAY_FREQUENCY_03.value, AcknowledgmentSets.COMMON.value,      None, None, Wording('[GAD-7  5/7]  Over the last 2 weeks, how often have you been so restless that it was hard to sit still?', [])),
        EvaluationItem([6], EIT.DUAL, True, Answers.DAY_FREQUENCY_03.value, AcknowledgmentSets.COMMON.value,      None, None, Wording('[GAD-7  6/7]  Over the last 2 weeks, how often have you been easily annoyed or irritable?', [])),
        EvaluationItem([7], EIT.DUAL, True, Answers.DAY_FREQUENCY_03.value, AcknowledgmentSets.COMMON_LAST.value, None, None, Wording('[GAD-7  7/7]  Over the last 2 weeks, how often have you been feeling afraid, as if something awful might happen?', [])),
        EvaluationItem([8], EIT.NONE, False, None, None, None,
                       lambda ctx: switch(ctx.topic.score, lambda x: x <= 4, [9,-1], lambda x: x <= 9, [9,-2], lambda x: x <= 14, [9,-3], [9,-4]),
                       WORDING.EVAL_END_2.value),
        EvaluationItem([9,-1], EIT.NONE, False, None, None, None, None, Wording('Your GAD-7 score of {topic-score} may indicate minimal signs or no signs of anxiety. I might say you are anxiety free.', [])),
        EvaluationItem([9,-2], EIT.NONE, False, None, None, None, None, Wording('Your GAD-7 score is {topic-score}, which indicates that you are experiencing mild anxiety symptoms. Take precautions and if your anxiety symptoms are interfering with your lifestyle, I recommend seeking further screening of your anxiety!', [])),
        EvaluationItem([9,-3], EIT.NONE, False, None, None, None, None, Wording('Your GAD-7 score is {topic-score}. Based on your score, I\'d say you\'re dealing with symptoms of moderate anxiety. I recommend you to seek the advice of an expert and further screening of your anxiety!', [])),
        EvaluationItem([9,-4], EIT.NONE, False, None, None, None, None, Wording('Your GAD-7 score of {topic-score} suggests that you might have symptoms indicative of severe anxiety. I highly recommend considering a mental health specialist for an in depth screening. ', [])),
    ])
    GAD_7_CO = Evaluation(EvaluationCode.GAD_7_CO, ['gad7', 'gad'], 'General Anxiety Disorder questionnaire', 'check your anxiety level', [
        EvaluationItem([1], EIT.CHOICE, True,  Answers.DAY_FREQUENCY_03.value, None, None, None, Wording('[GAD-7  1/7]  Over the last 2 weeks, how often have you been feeling nervous, anxious or on edge?', [])),
        EvaluationItem([2], EIT.CHOICE, True,  Answers.DAY_FREQUENCY_03.value, None, None, None, Wording('[GAD-7  2/7]  Over the last 2 weeks, how often did you find yourself not being able to stop or control worrying?', [])),
        EvaluationItem([3], EIT.CHOICE, True,  Answers.DAY_FREQUENCY_03.value, None, None, None, Wording('[GAD-7  3/7]  Over the last 2 weeks, how often have you been worrying too much about different things?', [])),
        EvaluationItem([4], EIT.CHOICE, True,  Answers.DAY_FREQUENCY_03.value, None, None, None, Wording('[GAD-7  4/7]  Over the last 2 weeks, how often did you have trouble relaxing?', [])),
        EvaluationItem([5], EIT.CHOICE, True,  Answers.DAY_FREQUENCY_03.value, None, None, None, Wording('[GAD-7  5/7]  Over the last 2 weeks, how often have you been so restless that it was hard to sit still?', [])),
        EvaluationItem([6], EIT.CHOICE, True,  Answers.DAY_FREQUENCY_03.value, None, None, None, Wording('[GAD-7  6/7]  Over the last 2 weeks, how often have you been easily annoyed or irritable?', [])),
        EvaluationItem([7], EIT.CHOICE, True,  Answers.DAY_FREQUENCY_03.value, None, None, None, Wording('[GAD-7  7/7]  Over the last 2 weeks, how often have you been feeling afraid, as if something awful might happen?', [])),
        EvaluationItem([8], EIT.NONE, False, None, None, None,
                       lambda ctx: switch(ctx.topic.score, lambda x: x <= 4, [9,-1], lambda x: x <= 9, [9,-2], lambda x: x <= 14, [9,-3], [9,-4]),
                       WORDING.EVAL_END_2.value),
        EvaluationItem([9,-1], EIT.NONE, False, None, None, None, None, Wording('Your GAD-7 score of {topic-score} may indicate minimal signs or no signs of anxiety. I might say you are anxiety free.', [])),
        EvaluationItem([9,-2], EIT.NONE, False, None, None, None, None, Wording('Your GAD-7 score is {topic-score}, which indicates that you are experiencing mild anxiety symptoms. Take precautions and if your anxiety symptoms are interfering with your lifestyle, I recommend seeking further screening of your anxiety!', [])),
        EvaluationItem([9,-3], EIT.NONE, False, None, None, None, None, Wording('Your GAD-7 score is {topic-score}. Based on your score, I\'d say you\'re dealing with symptoms of moderate anxiety. I recommend you to seek the advice of an expert and further screening of your anxiety!', [])),
        EvaluationItem([9,-4], EIT.NONE, False, None, None, None, None, Wording('Your GAD-7 score of {topic-score} suggests that you might have symptoms indicative of severe anxiety. I highly recommend considering a mental health specialist for an in depth screening. ', [])),
    ])
    PCL_5 = Evaluation(EvaluationCode.PCL_5, ['pcl5', 'pcl'], 'Posttraumatic Stress Disorder Checklist questionnaire', 'check your stress level', [
        EvaluationItem([1],  EIT.DUAL, True, Answers.INTENSITY_04.value, AcknowledgmentSets.COMMON.value,       None, None, Wording('[PCL-5  1/20]  In the past month, how much were you bothered by repeated, disturbing, and unwanted memories of the stressful experience?', [])),
        EvaluationItem([2],  EIT.DUAL, True, Answers.INTENSITY_04.value, AcknowledgmentSets.COMMON.value,       None, None, Wording('[PCL-5  2/20]  In the past month, how much were you bothered by repeated, disturbing dreams of the stressful experience?', [])),
        EvaluationItem([3],  EIT.DUAL, True, Answers.INTENSITY_04.value, AcknowledgmentSets.COMMON.value,       None, None, Wording('[PCL-5  3/20]  In the past month, how much were you bothered by suddenly feeling or acting as if the stressful experience were actually happening again (as if you were actually back there reliving it)?', [])),
        EvaluationItem([4],  EIT.DUAL, True, Answers.INTENSITY_04.value, AcknowledgmentSets.COMMON.value,       None, None, Wording('[PCL-5  4/20]  In the past month, how much were you bothered by feeling very upset when something reminded you of the stressful experience?', [])),
        EvaluationItem([5],  EIT.DUAL, True, Answers.INTENSITY_04.value, AcknowledgmentSets.COMMON.value,       None, None, Wording('[PCL-5  5/20]  In the past month, how much were you bothered by having strong physical reactions when something reminded you of the stressful experience (for example, heart pounding, trouble breathing, sweating)?', [])),
        EvaluationItem([6],  EIT.DUAL, True, Answers.INTENSITY_04.value, AcknowledgmentSets.COMMON.value,       None, None, Wording('[PCL-5  6/20]  In the past month, how much were you bothered by avoiding memories, thoughts, or feelings related to the stressful experience?', [])),
        EvaluationItem([7],  EIT.DUAL, True, Answers.INTENSITY_04.value, AcknowledgmentSets.COMMON.value,       None, None, Wording('[PCL-5  7/20]  In the past month, how much were you bothered by avoiding external reminders of the stressful experience (for example, people, places, conversations, activities, objects, or situations)?', [])),
        EvaluationItem([8],  EIT.DUAL, True, Answers.INTENSITY_04.value, AcknowledgmentSets.COMMON.value,       None, None, Wording('[PCL-5  8/20]  In the past month, how much were you bothered by trouble remembering important parts of the stressful experience?', [])),
        EvaluationItem([9],  EIT.DUAL, True, Answers.INTENSITY_04.value, AcknowledgmentSets.COMMON.value,       None, None, Wording('[PCL-5  9/20]  In the past month, how much were you bothered by having strong negative beliefs about yourself, other people, or the world (for example, having thoughts such as: I am bad, there is something seriously wrong with me, no one can be trusted, the world is completely dangerous)?', [])),
        EvaluationItem([10], EIT.DUAL, True, Answers.INTENSITY_04.value, AcknowledgmentSets.COMMON.value,       None, None, Wording('[PCL-5  10/20]  In the past month, how much were you bothered by blaming yourself or someone else for the stressful experience or what happened after it?', [])),
        EvaluationItem([11], EIT.DUAL, True, Answers.INTENSITY_04.value, AcknowledgmentSets.COMMON.value,       None, None, Wording('[PCL-5  11/20]  In the past month, how much were you bothered by having strong negative feelings such as fear, horror, anger, guilt, or shame?', [])),
        EvaluationItem([12], EIT.DUAL, True, Answers.INTENSITY_04.value, AcknowledgmentSets.COMMON.value,       None, None, Wording('[PCL-5  12/20]  In the past month, how much were you bothered by loss of interest in activities that you used to enjoy?', [])),
        EvaluationItem([13], EIT.DUAL, True, Answers.INTENSITY_04.value, AcknowledgmentSets.COMMON.value,       None, None, Wording('[PCL-5  13/20]  In the past month, how much were you bothered by feeling distant or cut off from other people?', [])),
        EvaluationItem([14], EIT.DUAL, True, Answers.INTENSITY_04.value, AcknowledgmentSets.COMMON.value,       None, None, Wording('[PCL-5  14/20]  In the past month, how much were you bothered by trouble experiencing positive feelings (for example, being unable to feel happiness or have loving feelings for people close to you)?', [])),
        EvaluationItem([15], EIT.DUAL, True, Answers.INTENSITY_04.value, AcknowledgmentSets.COMMON.value,       None, None, Wording('[PCL-5  15/20]  In the past month, how much were you bothered by irritable behavior, angry outbursts, or acting aggressively?', [])),
        EvaluationItem([16], EIT.DUAL, True, Answers.INTENSITY_04.value, AcknowledgmentSets.CAREFUL.value,      None, None, Wording('[PCL-5  16/20]  In the past month, how much were you bothered by taking too many risks or doing things that could cause you harm?', [])),
        EvaluationItem([17], EIT.DUAL, True, Answers.INTENSITY_04.value, AcknowledgmentSets.COMMON.value,       None, None, Wording('[PCL-5  17/20]  In the past month, how much were you bothered by being "superalert" or watchful or on guard?', [])),
        EvaluationItem([18], EIT.DUAL, True, Answers.INTENSITY_04.value, AcknowledgmentSets.COMMON.value,       None, None, Wording('[PCL-5  18/20]  In the past month, how much were you bothered by feeling jumpy or easily startled?', [])),
        EvaluationItem([19], EIT.DUAL, True, Answers.INTENSITY_04.value, AcknowledgmentSets.COMMON.value,       None, None, Wording('[PCL-5  19/20]  In the past month, how much were you bothered by having difficulty concentrating?', [])),
        EvaluationItem([20], EIT.DUAL, True, Answers.INTENSITY_04.value, AcknowledgmentSets.COMMON_LAST.value,  None, None, Wording('[PCL-5  20/20]  In the past month, how much were you bothered by trouble falling or staying asleep?', [])),
        EvaluationItem([21], EIT.NONE, False, None, None, None,
                       lambda ctx: switch(ctx.topic.score, lambda x: x <= 32, [22,-1], [22,-2]),
                       WORDING.EVAL_END_3.value),
        EvaluationItem([22,-1], EIT.NONE, False, None, None, None, None, Wording('There are no clinical stress symptoms or symptoms indicative of post-traumatic stress disorder based on your PCL-5 score of {topic-score}.', [])),
        EvaluationItem([22,-2], EIT.NONE, False, None, None, None, None, Wording('Your PCL-5 score is {topic-score}, indicating that you might have clinical stress symptoms that might be characteristic of a post-traumatic stress disorder. I highly recommend seeking a mental health specialist for further screening.', [])),
    ])
    PCL_5_CO = Evaluation(EvaluationCode.PCL_5_CO, ['pcl5', 'pcl'], 'Posttraumatic Stress Disorder Checklist questionnaire', 'check your stress level', [
        EvaluationItem([1],  EIT.CHOICE, True,  Answers.INTENSITY_04.value, None, None, None, Wording('[PCL-5  1/20]  In the past month, how much were you bothered by repeated, disturbing, and unwanted memories of the stressful experience?', [])),
        EvaluationItem([2],  EIT.CHOICE, True,  Answers.INTENSITY_04.value, None, None, None, Wording('[PCL-5  2/20]  In the past month, how much were you bothered by repeated, disturbing dreams of the stressful experience?', [])),
        EvaluationItem([3],  EIT.CHOICE, True,  Answers.INTENSITY_04.value, None, None, None, Wording('[PCL-5  3/20]  In the past month, how much were you bothered by suddenly feeling or acting as if the stressful experience were actually happening again (as if you were actually back there reliving it)?', [])),
        EvaluationItem([4],  EIT.CHOICE, True,  Answers.INTENSITY_04.value, None, None, None, Wording('[PCL-5  4/20]  In the past month, how much were you bothered by feeling very upset when something reminded you of the stressful experience?', [])),
        EvaluationItem([5],  EIT.CHOICE, True,  Answers.INTENSITY_04.value, None, None, None, Wording('[PCL-5  5/20]  In the past month, how much were you bothered by having strong physical reactions when something reminded you of the stressful experience (for example, heart pounding, trouble breathing, sweating)?', [])),
        EvaluationItem([6],  EIT.CHOICE, True,  Answers.INTENSITY_04.value, None, None, None, Wording('[PCL-5  6/20]  In the past month, how much were you bothered by avoiding memories, thoughts, or feelings related to the stressful experience?', [])),
        EvaluationItem([7],  EIT.CHOICE, True,  Answers.INTENSITY_04.value, None, None, None, Wording('[PCL-5  7/20]  In the past month, how much were you bothered by avoiding external reminders of the stressful experience (for example, people, places, conversations, activities, objects, or situations)?', [])),
        EvaluationItem([8],  EIT.CHOICE, True,  Answers.INTENSITY_04.value, None, None, None, Wording('[PCL-5  8/20]  In the past month, how much were you bothered by trouble remembering important parts of the stressful experience?', [])),
        EvaluationItem([9],  EIT.CHOICE, True,  Answers.INTENSITY_04.value, None, None, None, Wording('[PCL-5  9/20]  In the past month, how much were you bothered by having strong negative beliefs about yourself, other people, or the world (for example, having thoughts such as: I am bad, there is something seriously wrong with me, no one can be trusted, the world is completely dangerous)?', [])),
        EvaluationItem([10], EIT.CHOICE, True,  Answers.INTENSITY_04.value, None, None, None, Wording('[PCL-5  10/20]  In the past month, how much were you bothered by blaming yourself or someone else for the stressful experience or what happened after it?', [])),
        EvaluationItem([11], EIT.CHOICE, True,  Answers.INTENSITY_04.value, None, None, None, Wording('[PCL-5  11/20]  In the past month, how much were you bothered by having strong negative feelings such as fear, horror, anger, guilt, or shame?', [])),
        EvaluationItem([12], EIT.CHOICE, True,  Answers.INTENSITY_04.value, None, None, None, Wording('[PCL-5  12/20]  In the past month, how much were you bothered by loss of interest in activities that you used to enjoy?', [])),
        EvaluationItem([13], EIT.CHOICE, True,  Answers.INTENSITY_04.value, None, None, None, Wording('[PCL-5  13/20]  In the past month, how much were you bothered by feeling distant or cut off from other people?', [])),
        EvaluationItem([14], EIT.CHOICE, True,  Answers.INTENSITY_04.value, None, None, None, Wording('[PCL-5  14/20]  In the past month, how much were you bothered by trouble experiencing positive feelings (for example, being unable to feel happiness or have loving feelings for people close to you)?', [])),
        EvaluationItem([15], EIT.CHOICE, True,  Answers.INTENSITY_04.value, None, None, None, Wording('[PCL-5  15/20]  In the past month, how much were you bothered by irritable behavior, angry outbursts, or acting aggressively?', [])),
        EvaluationItem([16], EIT.CHOICE, True,  Answers.INTENSITY_04.value, None, None, None, Wording('[PCL-5  16/20]  In the past month, how much were you bothered by taking too many risks or doing things that could cause you harm?', [])),
        EvaluationItem([17], EIT.CHOICE, True,  Answers.INTENSITY_04.value, None, None, None, Wording('[PCL-5  17/20]  In the past month, how much were you bothered by being "superalert" or watchful or on guard?', [])),
        EvaluationItem([18], EIT.CHOICE, True,  Answers.INTENSITY_04.value, None, None, None, Wording('[PCL-5  18/20]  In the past month, how much were you bothered by feeling jumpy or easily startled?', [])),
        EvaluationItem([19], EIT.CHOICE, True,  Answers.INTENSITY_04.value, None, None, None, Wording('[PCL-5  19/20]  In the past month, how much were you bothered by having difficulty concentrating?', [])),
        EvaluationItem([20], EIT.CHOICE, True,  Answers.INTENSITY_04.value, None, None, None, Wording('[PCL-5  20/20]  In the past month, how much were you bothered by trouble falling or staying asleep?', [])),
        EvaluationItem([21], EIT.NONE, False, None, None, None,
                       lambda ctx: switch(ctx.topic.score, lambda x: x <= 32, [22,-1], [22,-2]),
                       WORDING.EVAL_END_3.value),
        EvaluationItem([22,-1], EIT.NONE, False, None, None, None, None, Wording('There are no clinical stress symptoms or symptoms indicative of post-traumatic stress disorder based on your PCL-5 score of {topic-score}.', [])),
        EvaluationItem([22,-2], EIT.NONE, False, None, None, None, None, Wording('Your PCL-5 score is {topic-score}, indicating that you might have clinical stress symptoms that might be characteristic of a post-traumatic stress disorder. I highly recommend seeking a mental health specialist for further screening.', [])),
    ])
    USABILITY_1 = Evaluation(EvaluationCode.USABILITY_1, [], '', '', [
        EvaluationItem([1],  EIT.NONE,   False, None,                               None, None, None, Wording('Thank you for all your answers! As we wrap up our conversation, I\'d appreciate your thoughts regarding our interaction. Please respond to the following questions. Your input will be extremely valuable to me.', [])),
        EvaluationItem([2],  EIT.OPEN,   True,  None,                               None, None, None, Wording('[1/33]  What chatbot feature(s) did you like?', [])),
        EvaluationItem([3],  EIT.OPEN,   True,  None,                               None, None, None, Wording('[2/33]  What chatbot feature(s) you disliked?', [])),
        EvaluationItem([4],  EIT.OPEN,   True,  None,                               None, None, None, Wording('[3/33]  Any errors encountered (yes/no)? Which ones?', [])),
        EvaluationItem([5],  EIT.OPEN,   True,  None,                               None, None, None, Wording('[4/33]  Was there a moment where you didn''t know what to do? (yes/no) Which one?', [])),
        EvaluationItem([6],  EIT.OPEN,   True,  None,                               None, None, None, Wording('[5/33]  What improvements would keep you interested in the chatbot?', [])),
        EvaluationItem([7],  EIT.OPEN,   True,  None,                               None, None, None, Wording('[6/33]  Was the conversational flow of the chatbot adequate? ( i.e., short enough, clear enough, clear question/feedback sequence). By conversational flow we understand natural transitions from questions to feedback, from the beginning till the end of the screening. Please detail.', [])),
        EvaluationItem([8],  EIT.OPEN,   True,  None,                               None, None, None, Wording('[7/33]  Did the chatbot offer any question or feedback that was difficult for you to comprehend? Can you recall which one?', [])),
        EvaluationItem([9],  EIT.OPEN,   True,  None,                               None, None, None, Wording('[8/33]  At any time did you have the feeling that the chatbot was stuck in a loop or that you didn''t make any headway in the conversation? (yes/no). If yes, can you remember which part was that?', [])),
        EvaluationItem([10], EIT.CHOICE, True,  Answers.AGREE_04.value,             None, None, None, Wording('[9/33]  How much would you agree that the chatbot’s personality was realistic engaging?', [])),
        EvaluationItem([11], EIT.CHOICE, True,  Answers.AGREE_04.value,             None, None, None, Wording('[10/33]  How much would you agree that the chatbot seemed too robotic?', [])),
        EvaluationItem([12], EIT.CHOICE, True,  Answers.AGREE_04.value,             None, None, None, Wording('[11/33]  How much would you agree that the chatbot was welcoming during the initial setup?', [])),
        EvaluationItem([13], EIT.CHOICE, True,  Answers.AGREE_04.value,             None, None, None, Wording('[12/33]  How much would you agree that the chatbot seemed very unfriendly?', [])),
        EvaluationItem([14], EIT.CHOICE, True,  Answers.AGREE_04.value,             None, None, None, Wording('[13/33]  How much would you agree that the chatbot explained its scope and purpose well?', [])),
        EvaluationItem([15], EIT.CHOICE, True,  Answers.AGREE_04.value,             None, None, None, Wording('[14/33]  How much would you agree that the chatbot gave no indication as to its purpose?', [])),
        EvaluationItem([16], EIT.CHOICE, True,  Answers.AGREE_04.value,             None, None, None, Wording('[15/33]  How much would you agree that the chatbot was easy to navigate?', [])),
        EvaluationItem([17], EIT.CHOICE, True,  Answers.AGREE_04.value,             None, None, None, Wording('[16/33]  How much would you agree that it would be easy to get confused when using the chatbot?', [])),
        EvaluationItem([18], EIT.CHOICE, True,  Answers.AGREE_04.value,             None, None, None, Wording('[17/33]  How much would you agree that the chatbot understood me well?', [])),
        EvaluationItem([19], EIT.CHOICE, True,  Answers.AGREE_04.value,             None, None, None, Wording('[18/33]  How much would you agree that the chatbot failed to recognise a lot of my inputs?', [])),
        EvaluationItem([20], EIT.CHOICE, True,  Answers.AGREE_04.value,             None, None, None, Wording('[19/33]  How much would you agree that chatbot responses were useful, appropriate and informative?', [])),
        EvaluationItem([21], EIT.CHOICE, True,  Answers.AGREE_04.value,             None, None, None, Wording('[20/33]  How much would you agree that chatbot responses were irrelevant?', [])),
        EvaluationItem([22], EIT.CHOICE, True,  Answers.AGREE_04.value,             None, None, None, Wording('[21/33]  How much would you agree that the chatbot coped well with any errors or mistakes?', [])),
        EvaluationItem([23], EIT.CHOICE, True,  Answers.AGREE_04.value,             None, None, None, Wording('[22/33]  How much would you agree that the chatbot seemed unable to handle any errors?', [])),
        EvaluationItem([24], EIT.CHOICE, True,  Answers.AGREE_04.value,             None, None, None, Wording('[23/33]  How much would you agree that the chatbot was very easy to use?', [])),
        EvaluationItem([25], EIT.CHOICE, True,  Answers.AGREE_04.value,             None, None, None, Wording('[24/33]  How much would you agree that the chatbot was very complex?', [])),
        EvaluationItem([26], EIT.CHOICE, True,  Answers.GENERAL_FREQUENCY_04.value, None, None, None, Wording('[25/33]  How well did the system understand you?', [])),
        EvaluationItem([27], EIT.CHOICE, True,  Answers.GENERAL_FREQUENCY_04.value, None, None, None, Wording('[26/33]  How well did you understand the system messages?', [])),
        EvaluationItem([28], EIT.CHOICE, True,  Answers.RATE_04.value,              None, None, None, Wording('[27/33]  In your opinion, the interaction rate was ...', [])),
        EvaluationItem([29], EIT.CHOICE, True,  Answers.DIFFICULTY_04.value,        None, None, None, Wording('[28/33]  In your opinion, the difficulty level of the system was ...', [])),
        EvaluationItem([30], EIT.CHOICE, True,  Answers.GENERAL_FREQUENCY_04.value, None, None, None, Wording('[29/33]  Have you noticed errors during the interaction?', [])),
        EvaluationItem([31], EIT.CHOICE, True,  Answers.GENERAL_FREQUENCY_04.value, None, None, None, Wording('[30/33]  Was it easy to decide what to do after each interaction with the chatbot?', [])),
        EvaluationItem([32], EIT.CHOICE, True,  Answers.SATISFACTION_04.value,      None, None, None, Wording('[31/33]  In general, how satisfied are you with the system?', [])),
        EvaluationItem([33], EIT.CHOICE, True,  Answers.NO_YES_01.value,            None, None, None, Wording('[32/33]  Is Discord a good platform for a chatbot?', [])),
        EvaluationItem([34], EIT.OPEN,   True,  None,                               None, None, None, Wording('[33/33]  Was the feedback you received after some responses too empathetic, not empathetic enough, just the right amount or somewhere in between? Please specify.', [])),
    ])
    USABILITY_2 = Evaluation(EvaluationCode.USABILITY_2, [], '', '', [
        EvaluationItem([1],  EIT.NONE,   False, None,                               None, None, None, Wording('As we wrap up our conversation, I\'d appreciate your thoughts regarding our interaction. Please respond to the following questions. Your input is extremely valuable to me. ', [])),
        EvaluationItem([2], EIT.CHOICE, True,  Answers.AGREE_04.value,              None, None, None, Wording('[1/24]  How much would you agree that the chatbot’s personality was realistic engaging?', [])),
        EvaluationItem([3], EIT.CHOICE, True,  Answers.AGREE_04.value,              None, None, None, Wording('[2/24]  How much would you agree that the chatbot seemed too robotic?', [])),
        EvaluationItem([4], EIT.CHOICE, True,  Answers.AGREE_04.value,              None, None, None, Wording('[3/24]  How much would you agree that the chatbot was welcoming during the initial setup?', [])),
        EvaluationItem([5], EIT.CHOICE, True,  Answers.AGREE_04.value,              None, None, None, Wording('[4/24]  How much would you agree that the chatbot seemed very unfriendly?', [])),
        EvaluationItem([6], EIT.CHOICE, True,  Answers.AGREE_04.value,              None, None, None, Wording('[5/24]  How much would you agree that the chatbot explained its scope and purpose well?', [])),
        EvaluationItem([7], EIT.CHOICE, True,  Answers.AGREE_04.value,              None, None, None, Wording('[6/24]  How much would you agree that the chatbot gave no indication as to its purpose?', [])),
        EvaluationItem([8], EIT.CHOICE, True,  Answers.AGREE_04.value,              None, None, None, Wording('[7/24]  How much would you agree that the chatbot was easy to navigate?', [])),
        EvaluationItem([9], EIT.CHOICE, True,  Answers.AGREE_04.value,              None, None, None, Wording('[8/24]  How much would you agree that it would be easy to get confused when using the chatbot?', [])),
        EvaluationItem([10], EIT.CHOICE, True,  Answers.AGREE_04.value,             None, None, None, Wording('[9/24]  How much would you agree that the chatbot understood me well?', [])),
        EvaluationItem([11], EIT.CHOICE, True,  Answers.AGREE_04.value,             None, None, None, Wording('[10/24]  How much would you agree that the chatbot failed to recognise a lot of my inputs?', [])),
        EvaluationItem([12], EIT.CHOICE, True,  Answers.AGREE_04.value,             None, None, None, Wording('[11/24]  How much would you agree that chatbot responses were useful, appropriate and informative?', [])),
        EvaluationItem([13], EIT.CHOICE, True,  Answers.AGREE_04.value,             None, None, None, Wording('[12/24]  How much would you agree that chatbot responses were irrelevant?', [])),
        EvaluationItem([14], EIT.CHOICE, True,  Answers.AGREE_04.value,             None, None, None, Wording('[13/24]  How much would you agree that the chatbot coped well with any errors or mistakes?', [])),
        EvaluationItem([15], EIT.CHOICE, True,  Answers.AGREE_04.value,             None, None, None, Wording('[14/24]  How much would you agree that the chatbot seemed unable to handle any errors?', [])),
        EvaluationItem([16], EIT.CHOICE, True,  Answers.AGREE_04.value,             None, None, None, Wording('[15/24]  How much would you agree that the chatbot was very easy to use?', [])),
        EvaluationItem([17], EIT.CHOICE, True,  Answers.AGREE_04.value,             None, None, None, Wording('[16/24]  How much would you agree that the chatbot was very complex?', [])),
        EvaluationItem([18], EIT.CHOICE, True,  Answers.GENERAL_FREQUENCY_04.value, None, None, None, Wording('[17/24]  How well did the system understand you?', [])),
        EvaluationItem([19], EIT.CHOICE, True,  Answers.GENERAL_FREQUENCY_04.value, None, None, None, Wording('[18/24]  How well did you understand the system messages?', [])),
        EvaluationItem([20], EIT.CHOICE, True,  Answers.RATE_04.value,              None, None, None, Wording('[19/24]  In your opinion, the interaction rate was ...', [])),
        EvaluationItem([21], EIT.CHOICE, True,  Answers.DIFFICULTY_04.value,        None, None, None, Wording('[20/24]  In your opinion, the difficulty level of the system was ...', [])),
        EvaluationItem([22], EIT.CHOICE, True,  Answers.GENERAL_FREQUENCY_04.value, None, None, None, Wording('[21/24]  Have you noticed errors during the interaction?', [])),
        EvaluationItem([23], EIT.CHOICE, True,  Answers.GENERAL_FREQUENCY_04.value, None, None, None, Wording('[22/24]  Was it easy to decide what to do after each interaction with the chatbot?', [])),
        EvaluationItem([24], EIT.CHOICE, True,  Answers.SATISFACTION_04.value,      None, None, None, Wording('[23/24]  In general, how satisfied are you with the system?', [])),
        EvaluationItem([25], EIT.CHOICE, True,  Answers.NO_YES_01.value,            None, None, None, Wording('[24/24]  Is Discord a good platform for a chatbot?', [])),
    ])
    TRANSITION_NLP1 = Evaluation(EvaluationCode.TRANSITION_NLP1, [], '', '', [
        EvaluationItem([1], EIT.NONE, False, None, None, None, None, Wording("""Now, as you recall, there is one final step that ends our interaction.

You will receive the same set of anxiety, depression, and chronic stress questions, but this time in the form of a standard questionnaire. As mentioned before, this will help me match your open-ended responses with your closed-ended responses. You can take a break if you need to and come back. Please don’t skip this part.

Take it easy, no need to rush & thank you for the opportunity to learn from you!""", []))
    ])
    THANKS = Evaluation(EvaluationCode.THANKS, [], '', '', [
        EvaluationItem([1], EIT.NONE, False, None, None, None, None, Wording('Thank you for your time! Hope it was a mutual learning experience. With your help I am now working on becoming a better "artificial person". Take care!', []))
    ])
    SELECT_N = Evaluation(EvaluationCode.SELECT_N, [], '', '', [
        EvaluationItem([1], EIT.CHOICE, False, None, None, None, None, Wording('Which of these evaluations would you like to proceed with?\n{evaluations}', [])),
        EvaluationItem([2], EIT.NONE, False, None, None, None, None, Wording('Great! Let\'s get started!', ['Awesome! Here are the questions.', 'Ok. On we go.'])),
    ])
    ANNOUNCE_LAST = Evaluation(EvaluationCode.ANNOUNCE_LAST, [], '', '', [
        EvaluationItem([1], EIT.NONE, False, None, None, None, None, Wording('There is one evaluation left. Let\'s {action} with the {name} ({code})', []))
    ])

    def get_by_code(code: str) -> Evaluation:
        for ev in Evaluations:
            if ev.value.code.value == code:
                return ev.value
        return None

