create table users (
    id integer primary key ,
    username text,
    first_name text,
    first_enter integer,
    user_id integer not null unique,
    language_code text,
    chart_id integer
);

create table board (
    id integer primary key,
    board text not null,
    users_id integer not null unique,
    FOREIGN KEY (users_id) REFERENCES users(user_id)
);

create table feedback (
    id integer primary key,
    users_id integer not null,
    message text,
    FOREIGN KEY (users_id) REFERENCES users(user_id)
)
