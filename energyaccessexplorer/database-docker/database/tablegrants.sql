grant select on all tables in schema public to guest;
grant all on all tables in schema public to admin;

grant select on geography_boundaries to public;

grant all on circles to master;
grant all on pg_authid to master;
grant all on pg_roles to master;

grant usr to admin;
       grant admin to master;
                grant master to root;
