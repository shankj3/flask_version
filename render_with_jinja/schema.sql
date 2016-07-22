drop table if exists templates;
create table templates (
    id integer primary key autoincrement,
    filename text not null,
    'contents' text not null
);
