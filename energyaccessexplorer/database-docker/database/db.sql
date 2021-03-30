create extension unaccent;
create extension pgcrypto;
create extension pgjwt;     -- https://github.com/michelp/pgjwt

-- create role guest nologin;
-- create role usr nologin;
-- create role root nologin;
-- create role master nologin;
-- create role admin nologin;

create domain epiphet as name check (value ~ '^[a-z][a-z0-9\-]+$');

create type environments as enum ('test', 'staging', 'production');
-- select enum_range(null::environments);

create function before_any_create()
returns trigger
language plpgsql immutable as $$ begin
	new.created = current_timestamp;
	new.created_by = current_setting('request.jwt.claim.email', true);

	return new;
end $$;

create or replace function before_any_update()
returns trigger
language plpgsql immutable as $$ begin
	if (old.updated_by != new.updated_by) or
		(old.created_by != new.created_by) or
		(old.updated != new.updated) or
		(old.created != new.created)
	then
		raise exception 'Columns "updated", "updated_by", "created" and "created_by" are not editable';
	end if;

	new.updated = current_timestamp;
	new.updated_by = current_setting('request.jwt.claim.email', true);

	return new;
end $$;
