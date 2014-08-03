drop schema if exists pgv cascade;

create schema pgv;

create table if not exists pgv.revisions(
  revisions_id bigserial primary key,
  revision character varying(127) unique not null,
  time timestamp not null default current_timestamp,
  meta json not null default '{}::json'
);

create table if not exists pgv.scripts(
  scripts_id bigserial primary key,
  script text not null,
  start timestamp not null default current_timestamp,
  stop timestamp,
  successful boolean not null default true,
  error text not null default ''
);

create or replace function pgv.is_installed(p_revision text)
returns bigint as $$
  declare
    o_result bigint;
  begin
    select revisions_id
      into o_result
      from pgv.revisions
     where revision = p_revision;
    return o_result;
  end;
$$
language plpgsql
strict;

create or replace function pgv.run(p_script text)
returns bigint as $$
  declare
    o_scripts_id bigint;
  begin
    insert into pgv.scripts (script, stop) values (p_script, null) returning scripts_id into o_scripts_id;
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

create or replace function pgv.commit(p_revision character varying(127))
returns bigint as $$
  declare
    o_revisions_id bigint;
  begin
    insert into pgv.revisions (revision) values (p_revision) returning revisions_id into o_revisions_id;
    return o_revisions_id;
  end;

$$
language plpgsql;

create or replace function pgv.commit(p_revision character varying(127), p_meta json)
returns bigint as $$
  declare
    o_revisions_id bigint;
  begin
    insert into pgv.revisions (revision, meta) values (p_revision, p_meta) returning revisions_id into o_revisions_id;
    return o_revisions_id;
  end;

$$
language plpgsql;

create or replace function pgv.revision()
returns character varying(127) as $$
  declare
    o_revision character varying(127);
  begin
    select revision into o_revision from pgv.revisions order by revisions_id desc limit 1;
    return o_revision;
  end;
$$
language plpgsql
security definer;
