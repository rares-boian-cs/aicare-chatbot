from common.constant import DiscussionStatus, StudyCode
from common.util import PRCTX, config


class ParticipantDao:
    async def get_status_study_lists(self, participant_id: int) -> dict[DiscussionStatus, list[StudyCode]]:
        ret: dict[DiscussionStatus, list[StudyCode]] = {}
        prctx = PRCTX.get()
        for r in await prctx.connection.fetch('select study_code, status '
                                              'from discussion d inner join participant p on d.participant_id = p.id and d.round = p.round '
                                              'where p.id = $1', participant_id):
            k = DiscussionStatus(r['status'])
            v = StudyCode(r['study_code'])
            if not k in ret:
                ret[k] = []
            ret[k].append(v)
        return ret

    async def get_finish_reading_delay(self, participant_id: int) -> float:
        prctx = PRCTX.get()
        t = await prctx.connection.fetchval('select '
                                            '    case when received_at is null then coalesce(extract(epoch from coalesce(delivered_at, sent_at) + (length(content)/30) * interval \'1 second\' - now()), 5) '
                                            '         else 0 '
                                            '    end '
                                            'from utterance u '
                                            '     inner join exchange e on e.id = u.exchange_id '
                                            '     inner join matter m on m.id = e.matter_id '
                                            '     inner join topic t on t.id = m.topic_id '
                                            '     inner join discussion d on d.id = t.discussion_id '
                                            'where '
                                            '    d.participant_id = $1 '
                                            'order by '
                                            '    u.created_at desc '
                                            'limit 1', participant_id)
        if t is None or t < 0:
            t = 0
        if t > 20:
            t = 20
        return t*prctx.delay_scale

    async def get_subject_change_delay(self, participant_id: int) -> float:
        prctx = PRCTX.get()
        scd = config.get_float('application', 'subject-change-delay')
        t = await prctx.connection.fetchval('select '
                                            f'    coalesce(extract(epoch from coalesce(delivered_at, sent_at) + {config.get_float("application", "subject-change-delay")} * interval \'1 second\' - now()), 0) '
                                            'from utterance u '
                                            '     inner join exchange e on e.id = u.exchange_id '
                                            '     inner join matter m on m.id = e.matter_id '
                                            '     inner join topic t on t.id = m.topic_id '
                                            '     inner join discussion d on d.id = t.discussion_id '
                                            'where '
                                            '    d.participant_id = $1 and '
                                            '    m.completed_at is not null and '
                                            '    u.sent_at is not null '
                                            'order by '
                                            '    u.created_at desc '
                                            'limit 1', participant_id)
        if t is None or t < 0:
            t = 0
        if t > 3:
            t = 3
        return t*prctx.delay_scale
