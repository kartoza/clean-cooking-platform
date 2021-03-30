create function circles_parents(rol name)
returns text[] as $$
declare
	arr text[];
begin
	with recursive r as (
		select oid from pg_roles
			where rolname = rol
		union all
		select m.roleid from r
			join pg_auth_members m on m.member = r.oid)
	select array_agg(oid::regrole::text) from r
		where oid::regrole::text != rol
	into arr;

	return arr;
end $$ language plpgsql;

create view circles as
	select rolname, oid, circles_parents(rolname) parents
		from pg_roles
		where pg_has_role(rolname, 'usr', 'member') and
		(rolname not in ('root', 'postgres'));

create function circles_create(rol name, parent name)
returns boolean as $$
declare
	usr boolean;
begin
	if parent = 'postgres' then
		raise exception 'NO NO NO!! (%,%)', rol, parent;
	end if;

	select 'usr' in
		(select a.rolname from pg_authid a where pg_has_role(parent, a.oid, 'member'))
	into usr;

	if not usr then
		raise exception 'Only usrs allowed!! (%,%)', rol, parent;
	end if;

	execute format('
		create role %1$s nologin;
		grant %2$s to %1$s;
	', rol, parent);

	return true;
end $$ language plpgsql;

create function circles_create(rolname name)
returns boolean as $$
	select circles_create(rolname, 'usr');
$$ language sql;

create function circles_drop(rolname name)
returns boolean as $$ begin
	execute format('drop role %1$s;', rolname);
	return true;
end $$ language plpgsql;

create or replace function circles_update(oldname name, newname name)
returns table(rolname name) as $$ begin
	execute format('alter role %1$s rename to %2$s;', oldname, newname);
	return query select pg_roles.rolname from pg_roles where pg_roles.rolname = newname;
end $$ language plpgsql;

create function circles_insert()
returns trigger
as $$ begin
	perform circles_create(new.rolname, 'usr');
	return new;
end $$ language plpgsql;

create trigger circles_instead_insert
	instead of insert on circles
	for each row
	execute procedure circles_insert();

create function circles_delete()
returns trigger as $$ begin
	perform circles_drop(old.rolname);
	return old;
end $$ language plpgsql;

create trigger circles_instead_delete
	instead of delete on circles
	for each row
	execute procedure circles_delete();
