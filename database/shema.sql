create table users (
 id serial primary key,
 login varchar(100) not null,
 password varchar(255) not null,
 is_active BOOLEAN default true
);


create unique index idx_user_status on users(LOWER(login)) where is_active = true;


create table session (
 guid varchar(255) primary key,
 date timestamp not null, 
 agent TEXT not null,
 user_id integer not null,
 foreign key (user_id) references users(id)
);


create table flat(
 id serial primary key,
 user_id integer not null,
 name varchar(255) not null,
 foreign key (user_id) references users(id)
);


create table photo(
 id serial primary key,
 path text not null,
 flat_id integer not null,
 foreign key (flat_id) references flat(id)
);


create table report(
 id serial primary key,
 flat_id integer not null,
 foreign key (flat_id) references flat(id)
);


create table report_part(
 id serial primary key,
 report_id integer not null,
 info text,
 path text,
 foreign key (report_id) references report(id)
);


create table calendar(
 id serial primary key,
 date timestamp not null,
 is_clear BOOLEAN default true,
 user_id integer not null,
 foreign key (user_id) references users(id) 
);