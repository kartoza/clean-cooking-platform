#!/bin/bash
set -e

function create_user_and_database() {
	local db=$1
	echo "  Creating user and database '$db'"
	psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
	    CREATE USER $db;
		ALTER USER $db with encrypted password '$EAE_DB_PASS';
	    CREATE DATABASE $db;
	    GRANT ALL PRIVILEGES ON DATABASE $db TO $db;
EOSQL
}

function update_database_with_postgis() {
    local db=$1
    echo "  Updating database '$db' with extension"
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$db" <<-EOSQL
        CREATE EXTENSION IF NOT EXISTS postgis;
EOSQL
}

function run_eae_sql() {
    local db=$1
    echo "  Run eae sql in '$db'"
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$db" -f db.sql
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$db" -f categories.sql
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$db" -f files.sql
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$db" -f geographies.sql
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$db" -f datasets.sql
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$db" -f _datasets_files.sql
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$db" -f circles.sql
    psql --username "$POSTGRES_USER" --dbname "$db" -f tablegrants.sql
}

create_user_and_database 'eae'
update_database_with_postgis 'eae'
run_eae_sql 'eae'
