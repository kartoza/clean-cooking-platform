FROM mdillon/postgis:11
MAINTAINER Dimas Ciputra<dimas@kartoza.com>

# Install pgjwt - https://github.com/michelp/pgjwt
RUN apt-get update && apt-get install -y make git postgresql-server-dev-11 postgresql-11-pgtap ca-certificates
RUN git clone https://github.com/michelp/pgjwt.git /pgjwt
WORKDIR "/pgjwt"
RUN make && make install

# Run .sql files
ADD database /database
WORKDIR "/database"

COPY ./entrypoint.sh /docker-entrypoint-initdb.d/eae.sh
