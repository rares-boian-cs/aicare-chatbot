alter table utterance alter column discord_created_at drop not null;
alter table utterance alter column discord_message_id drop not null;
