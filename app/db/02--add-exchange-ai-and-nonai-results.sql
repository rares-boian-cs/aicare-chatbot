alter table exchange add column ai_input_type text;
alter table exchange add column ai_answer_item_code text;
alter table exchange add column ai_probabilities real[];
alter table exchange add column nonai_input_type text;
alter table exchange add column nonai_answer_item_code text;

update exchange set nonai_input_type = input_type, nonai_answer_item_code = answer_item_code;
