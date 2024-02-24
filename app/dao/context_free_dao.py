import datetime

from common.constant import ParticipantGroup, DiscussionStatus
from model.discussion_model import Discussion
from model.participant_model import Participant
from model.participant_report_model import ParticipantReport
from predefined.study_predefined import Studies


async def insert_bot_version_if_not_present(version: str, conn):
    await conn.execute("insert into bot_version (version, created_at) values ($1, $2) on conflict do nothing",
                       version, datetime.datetime.now().astimezone())


async def get_participant_id_and_create_if_not_exist(conn, discord_id: int, discord_tag: str, guild: str) -> int:
    prid = await conn.fetchval("select id from participant where discord_id = $1", discord_id)
    if prid is None:
        prid = await conn.fetchval("insert into participant (discord_id, discord_tag, round, pgroup) values ($1, $2, $3, $4) returning id",
                                   discord_id, discord_tag, 1, ParticipantGroup.OTHER.value)
    if guild is not None:
        await conn.execute('update participant set guilds = (select array_agg(distinct e) from unnest(guilds || $1) e) where id = $2', [guild], prid)
    return prid


async def get_participant_id_by_discord_id(conn, discord_id: int) -> int:
    return await conn.fetchval("select id from participant where discord_id = $1", discord_id)


async def increment_participant_round(conn, discord_id: int):
    await conn.execute('update participant set round = round + 1 where discord_id = $1', discord_id)


async def get_discussions_by_participant(conn, participant: Participant) -> list[Discussion]:
    return list(map(lambda r: Discussion(r, participant, Studies.get_value_by_code(r["study_code"])),
                    await conn.fetch('select d.* '
                                     'from discussion d '
                                     '     inner join participant p on d.participant_id = p.id and d.round = p.round '
                                     'where p.id = $1 '
                                     'order by d.created_at',
                                     participant.id)))


async def set_discussion_status(conn, discussion: Discussion, status: DiscussionStatus):
    await conn.execute('update discussion set status = $1 where id = $2', status.value, discussion.id)


async def get_report(conn) -> list[ParticipantReport]:
    return list(map(lambda r: ParticipantReport(r),
                    await conn.fetch("""select p.discord_tag || coalesce(' (' || d.participant_identification || ')', '')             as participant_name,
                                               to_char(q.latest, 'YYYY-MM-DD HH24:MI')                                                as last_heard_from,
                                               d.status || coalesce(' (' || to_char(d.completed_at, 'YYYY-MM-DD HH24:MI') || ')', '') as status,
                                               array_to_string(array_agg(t.code order by t.created_at), ', ')                         as evaluations
                                        from participant p
                                                 left join discussion d
                                                           on p.id = d.participant_id and d.study_code = 'data-collection'
                                                 left join topic t
                                                           on d.id = t.discussion_id and t.code not in ('consent-data-collection', 'select-n', 'announce-last')
                                                 left join (select t2.discussion_id, max(u.created_at) latest
                                                            from topic t2
                                                                     left join matter m on t2.id = m.topic_id
                                                                     left outer join exchange e on m.id = e.matter_id
                                                                     left join utterance u on e.id = u.exchange_id
                                                            where u.received_at is not null
                                                            group by t2.discussion_id) q on d.id = q.discussion_id
                                        group by p.discord_tag,
                                                 d.participant_identification,
                                                 d.created_at,
                                                 d.status,
                                                 d.completed_at,
                                                 q.latest
                                        order by lower(p.discord_tag),
                                                 d.created_at""")))

async def get_report_nlp1(conn) -> list[ParticipantReport]:
    return list(map(lambda r: ParticipantReport(r),
                    await conn.fetch("""select p.discord_tag || coalesce(' (' || d.participant_identification || ')', '')             as participant_name,
                                               to_char(q.latest, 'YYYY-MM-DD HH24:MI')                                                as last_heard_from,
                                               d.status || coalesce(' (' || to_char(d.completed_at, 'YYYY-MM-DD HH24:MI') || ')', '') as status,
                                               array_to_string(array_agg(t.code order by t.created_at), ', ')                         as evaluations
                                        from participant p
                                                 left join discussion d
                                                           on p.id = d.participant_id and d.study_code = 'nlp1'
                                                 left join topic t
                                                           on d.id = t.discussion_id and t.code not in ('consent-nlp1', 'select-n', 'announce-last')
                                                 left join (select t2.discussion_id, max(u.created_at) latest
                                                            from topic t2
                                                                     left join matter m on t2.id = m.topic_id
                                                                     left outer join exchange e on m.id = e.matter_id
                                                                     left join utterance u on e.id = u.exchange_id
                                                            where u.received_at is not null
                                                            group by t2.discussion_id) q on d.id = q.discussion_id
                                        group by p.discord_tag,
                                                 d.participant_identification,
                                                 d.created_at,
                                                 d.status,
                                                 d.completed_at,
                                                 q.latest
                                        order by lower(p.discord_tag),
                                                 d.created_at""")))

async def get_report_nlp1a(conn) -> list[ParticipantReport]:
    return list(map(lambda r: ParticipantReport(r),
                    await conn.fetch("""select p.discord_tag || coalesce(' (' || d.participant_identification || ')', '')             as participant_name,
                                               array_to_string(p.guilds, ',')                                                         as guild_names,
                                               to_char(q.latest, 'YYYY-MM-DD HH24:MI')                                                as last_heard_from,
                                               d.status || coalesce(' (' || to_char(d.completed_at, 'YYYY-MM-DD HH24:MI') || ')', '') as status,
                                               array_to_string(array_agg(t.code order by t.created_at), ', ')                         as evaluations
                                        from participant p
                                                 left join discussion d
                                                           on p.id = d.participant_id and d.study_code = 'nlp1a'
                                                 left join topic t
                                                           on d.id = t.discussion_id and t.code not in ('consent-nlp1', 'select-n', 'announce-last')
                                                 left join (select t2.discussion_id, max(u.created_at) latest
                                                            from topic t2
                                                                     left join matter m on t2.id = m.topic_id
                                                                     left outer join exchange e on m.id = e.matter_id
                                                                     left join utterance u on e.id = u.exchange_id
                                                            where u.received_at is not null
                                                            group by t2.discussion_id) q on d.id = q.discussion_id
                                        group by p.discord_tag,
                                                 d.participant_identification,
                                                 p.guilds,
                                                 d.created_at,
                                                 d.status,
                                                 d.completed_at,
                                                 q.latest
                                        order by lower(p.discord_tag),
                                                 d.created_at""")))

async def get_data(conn) -> list[ParticipantReport]:
    return list(map(lambda r: ParticipantReport(r),
                    await conn.fetch("""select p.id,
                                               p.discord_tag,
                                               d.participant_identification,
                                               d.participant_gender,
                                               d.participant_age,
                                               d.participant_english_proficiency,
                                               t.code,
                                               t.evaluation_hash,
                                               t.score,
                                               m.evaluation_item_code,
                                               u.content,
                                               u.sent_at,
                                               u.received_at,
                                               u.created_at
                                        from participant p
                                                 left join discussion d on p.id = d.participant_id and d.study_code = 'data-collection'
                                                 left join topic t on d.id = t.discussion_id and t.code not in ('consent-data-collection', 'select-n', 'announce-last')
                                                 left join matter m on t.id = m.topic_id
                                                 left join exchange e on m.id = e.matter_id
                                                 left join utterance u on e.id = u.exchange_id
                                        order by p.id,
                                                 t.code,
                                                 m.evaluation_item_code,
                                                 u.created_at;
                                        """)))
