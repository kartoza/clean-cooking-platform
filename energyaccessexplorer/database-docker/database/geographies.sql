create table geographies (
	  id uuid primary key default gen_random_uuid()
	, name varchar(64)
	, adm int
	, cca3 varchar(3) not null
	, circle epiphet default 'public'
	, pack epiphet default 'all'
	, parent_id uuid references geographies (id)
	, boundary_file uuid references files (id)
	, configuration jsonb default jsonb_build_object(
		'boundaries_name', null,
		'timeline', false,
		'timeline_dates', null,
		'flag', null,
		'sort_branches', array[]::text[],
		'sort_subbranches', array[]::text[],
		'sort_datasets', array[]::text[]
		)
	, envs environments[] default array[]::environments[]
	, created date default current_date
	, created_by varchar(64)
	, updated timestamp with time zone default current_timestamp
	, updated_by varchar(64)
	);

alter table geographies rename constraint geographies_parent_id_fkey to parent;

alter table geographies enable row level security;

create policy public on geographies
	for select to public
	using (circle in ('public'));

create policy admins on geographies
	using (current_role in ('admin'));

create policy superusers on geographies
	using (current_role in ('master', 'root'));
alter table geographies rename constraint geographies_boundary_file_fkey to boundary;

create trigger geographies_before_create
	before insert on geographies
	for each row
	execute procedure before_any_create();

create trigger geographies_before_update
	before update on geographies
	for each row
	execute procedure before_any_update();
