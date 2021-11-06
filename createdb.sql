create table users(
    id_user integer primary key,
    boss boolean,
    moderators boolean,
    created datetime,
    other_category text,
    tlg_name text,
    flow_name text)
