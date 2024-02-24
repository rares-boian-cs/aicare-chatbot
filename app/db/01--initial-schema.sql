create extension hstore;

create table bot_version
(
    version    text                     not null,
    created_at timestamp with time zone not null,
    constraint bot_version_pk primary key (version)
);

create table pgroup
(
    code text not null,
    constraint pgroup_pk primary key (code)
);

create table participant
(
    id          serial,
    discord_id  bigint  not null,
    discord_tag text    not null,
    pgroup      text    not null default 'other',
    round       integer not null,
    constraint participant_pk primary key (id),
    constraint participant_u1 unique (discord_id),
    constraint participant_u2 unique (discord_tag)
);

create table discussion
(
    id                              serial,
    study_code                      text                     not null,
    participant_id                  integer                  not null,
    participant_english_proficiency text,
    participant_identification      text,
    participant_age                 text,
    participant_gender              text,
    round                           integer                  not null,
    created_at                      timestamp with time zone not null,
    updated_at                      timestamp with time zone not null,
    completed_at                    timestamp with time zone,
    status                          text                     not null,
    constraint discussion_pk primary key (id),
    constraint discussion_fk1 foreign key (participant_id) references participant (id),
    constraint discussion_u1 unique (round, participant_id, study_code)
);

create table evaluation
(
    hash text  not null,
    obj  jsonb not null,
    constraint evaluation_pk primary key (hash)
);

create table topic
(
    id              serial,
    code            text                     not null,
    discussion_id   integer                  not null,
    evaluation_hash text                     not null,
    to_acknowledge  text[]                   not null,
    created_at      timestamp with time zone not null,
    updated_at      timestamp with time zone not null,
    completed_at    timestamp with time zone,
    score           integer,
    constraint topic_pk primary key (id),
    constraint topic_fk1 foreign key (discussion_id) references discussion (id),
    constraint topic_fk2 foreign key (evaluation_hash) references evaluation (hash)
);

create table matter
(
    id                   serial                   not null,
    topic_id             integer                  not null,
    evaluation_item_code text,
    answer_item_code     text,
    score                int                      not null,
    created_at           timestamp with time zone not null,
    updated_at           timestamp with time zone not null,
    completed_at         timestamp with time zone,
    constraint matter_pk primary key (id),
    constraint matter_fk1 foreign key (topic_id) references topic (id)
);

create table answer
(
    hash text  not null,
    obj  jsonb not null,
    constraint answer_pk primary key (hash)
);

create table exchange
(
    id                      serial                   not null,
    matter_id               integer                  not null,
    answer_hash             text,
    matter_flow_state       text                     not null,
    input_type              text,
    target_answer_item_code text,
    answer_item_code        text,
    next_matter_flow_state  text,
    created_at              timestamp with time zone not null,
    updated_at              timestamp with time zone not null,
    constraint exchange_pk primary key (id),
    constraint exchange_fk1 foreign key (matter_id) references matter (id),
    constraint exchange_fk3 foreign key (answer_hash) references answer (hash)
);

create table utterance
(
    id                 serial                   not null,
    exchange_id        integer                  not null,
    discord_message_id bigint                   not null,
    content            text                     not null,
    resent_counter     integer                  not null,
    discord_created_at timestamp with time zone not null,
    discord_edited_at  timestamp with time zone,
    sent_at            timestamp with time zone,
    delivered_at       timestamp with time zone,
    received_at        timestamp with time zone,
    created_at         timestamp with time zone not null,
    updated_at         timestamp with time zone not null,
    constraint utterance_pk primary key (id),
    constraint utterance_fk1 foreign key (exchange_id) references exchange (id)
);

create index utterance_discord_message_id_idx on utterance(discord_message_id);
