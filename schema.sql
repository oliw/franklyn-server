drop table if exists goals;
drop table if exists devices;

create table goals (
  id integer primary key autoincrement,
  description text not null,
  done integer null,
  feedback text null,
  date_created text not null
);

create table devices (
  device_id text primary key
);

insert into goals (description,date_created,done) VALUES ("Sample: Do a cartwheel","2013-10-03",1);
insert into goals (description,date_created,done) VALUES ("Sample: Read french book for 30mins","2013-10-02",1);
insert into goals (description,date_created,done,feedback) VALUES ("Sample: Do a backflip","2013-10-03",2,"Gave myself a nosebleed");