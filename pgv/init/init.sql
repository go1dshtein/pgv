drop schema pgv cascade;

create schema pgv;

create table if not exists pgv.revisions(
  revisions_id bigserial primary key,
  revision character(127) unique not null,
  time timestamp not null default current_timestamp
);

create table if not exists pgv.versions(
  versions_id bigserial primary key,
  revisions_id bigint not null unique references pgv.revisions,
  version character(127) unique not null
);

create table if not exists pgv.scripts(
  scripts_id bigserial primary key,
  script text not null,
  start timestamp not null default current_timestamp,
  stop timestamp,
  successful boolean not null default true,
  error text not null default ''
);


create or replace function pgv.run(p_script text)
returns bigint as $$
  declare
    o_scripts_id bigint;
  begin
    insert into pgv.scripts (script, stop) values (p_scripts, null) returning scripts_id into o_scripts_id;
    return o_scripts_id;
  end;
$$
language plpgsql;

create or replace function pgv.success(p_script_id bigint)
returns void as $$
  begin
    update pgv.scripts
       set stop = current_timestamp
     where scripts_id = p_script_id;
  end;
$$
language plpgsql
strict;

create or replace function pgv.error(p_script_id bigint, p_error text)
returns void as $$
  begin
    update pgv.scripts
       set stop = current_timestamp,
	   error = p_error,
	   successful = false
     where scripts_id = p_script_id;
  end;
$$
language plpgsql
strict;

create or replace function pgv.commit(p_revision character(127))
returns bigint as $$
  declare
    o_revisions_id bigint;
  begin
    insert into pgv.revisions (revision) values (p_revision) returning revisions_id into o_revisions_id;
    return o_revisions_id;
  end;

$$
language plpgsql;
