create table categories (
	  id uuid primary key default gen_random_uuid()
	, name epiphet unique not null
	, name_long varchar(64) not null
	, unit varchar(32)
	, domain jsonb default 'null'
	, domain_init jsonb default 'null'
	, colorstops jsonb default 'null'
	, raster jsonb default 'null'
	, vectors jsonb default 'null'
	, csv jsonb default 'null'
	, analysis jsonb default 'null'
	, timeline jsonb default 'null'
	, controls jsonb default jsonb_build_object(
		'range', null,
		'range_steps', null,
		'range_label', null,
		'path', array[]::text[],
		'weight', false
		)
	, metadata jsonb default jsonb_build_object(
		'why', null
		)
	, created date default current_date
	, created_by varchar(64)
	, updated timestamp with time zone default current_timestamp
	, updated_by varchar(64)
	);

create trigger categories_before_create
	before insert on categories
	for each row
	execute procedure before_any_create();

create trigger categories_before_update
	before update on categories
	for each row
	execute procedure before_any_update();
