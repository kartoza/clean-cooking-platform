# Energy Access Explorer Database

This is the SQL (PostgreSQL) code for the platform's database.

Naturally, PostgreSQL must be installed and running. You can find some minor
development utilities in the `makefile`. Create a `default.mk` file and create
values to your needs:

```
DB_NAME = <database-name>
PG = postgres://<user>:<passwd>@<server>:5432
SQL_FILES = db geographies categories datasets files ...
```

Then, you can run `make build`.

It is written with having in mind that a PostgREST instance will run in front
it. Hence, the external dependencies/extensions must be pre-installed on the
system:
- [pgjwt](https://github.com/michelp/pgjwt)
