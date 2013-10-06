drop table if exists goals;
create table goals (
  id integer primary key autoincrement,
  description text not null,
  done integer null,
  feedback text null,
  date_created text not null
);

insert into goals (description,date_created) VALUES ("my first ever goal","2013-10-03");
insert into goals (description,date_created) VALUES ("my second ever goal","2013-10-02");
insert into goals (description,date_created) VALUES ("my third ever goal","2013-10-03");