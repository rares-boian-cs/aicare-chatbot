import datetime

from common.util import PRCTX
from model.discussion_model import Discussion
from model.discussion_model import DiscussionStatus
from predefined.study_model import Study
from model.participant_model import Participant


class DiscussionDao:
    async def create(self, study: Study, participant: Participant) -> Discussion:
        prctx = PRCTX.get()
        now = datetime.datetime.now().astimezone()
        rid = await prctx.connection.fetchval('insert into discussion (study_code, participant_id, created_at, updated_at, status, round) '
                                              'values (                        $1,             $2,         $3,         $3,     $4, (select round from participant where id = $2)) '
                                              'returning id',
                                              study.code.value, participant.id, now, DiscussionStatus.ACTIVE.value)
        r = await prctx.connection.fetchrow('select * from discussion where id = $1', rid)
        return Discussion(r, participant, study)

    async def get_by_participant_and_study_and_status(self, participant: Participant, study: Study, status: DiscussionStatus) -> list[Discussion]:
        prctx = PRCTX.get()
        return list(map(lambda r: Discussion(r, participant, study),
                        await prctx.connection.fetch('select d.* '
                                                     'from discussion d '
                                                     '     inner join participant p on d.participant_id = p.id and d.round = p.round '
                                                     'where p.id = $1 and d.study_code = $2 and d.status = $3 '
                                                     'order by d.created_at',
                                                     participant.id, study.code.value, status.value)))

    async def set_status(self, discussion: Discussion, status: DiscussionStatus):
        prctx = PRCTX.get()
        now = datetime.datetime.now().astimezone()
        if status == DiscussionStatus.COMPLETED:
            await prctx.connection.execute('update discussion set status = $1, updated_at = $3, completed_at = $3 where id = $2', status.value, discussion.id, now)
        else:
            await prctx.connection.execute('update discussion set status = $1, updated_at = $3 where id = $2', status.value, discussion.id, now)

    async def set_participant_identification(self, discussion: Discussion, identification: str):
        prctx = PRCTX.get()
        now = datetime.datetime.now().astimezone()
        await prctx.connection.execute('update discussion set participant_identification = $1, updated_at = $3 where id = $2', identification, discussion.id, now)

    async def set_participant_age(self, discussion: Discussion, age: str):
        prctx = PRCTX.get()
        now = datetime.datetime.now().astimezone()
        await prctx.connection.execute('update discussion set participant_age = $1, updated_at = $3 where id = $2', age, discussion.id, now)

    async def set_participant_gender(self, discussion: Discussion, gender: str):
        prctx = PRCTX.get()
        now = datetime.datetime.now().astimezone()
        await prctx.connection.execute('update discussion set participant_gender = $1, updated_at = $3 where id = $2', gender, discussion.id, now)

    async def set_participant_english_proficiency(self, discussion: Discussion, proficiency: str):
        prctx = PRCTX.get()
        now = datetime.datetime.now().astimezone()
        await prctx.connection.execute('update discussion set participant_english_proficiency = $1, updated_at = $3 where id = $2', proficiency, discussion.id, now)

