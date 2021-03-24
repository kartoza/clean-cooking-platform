#--------- Generic stuff all our Dockerfiles should start with so we get caching ------------
FROM ubuntu:20.10
MAINTAINER Irwan Fathurrahman<anita@kartoza.com>

# Pandoc needed to generate rst dumps, uic compressor needed for django-pipeline
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update --fix-missing -y && apt-get upgrade -y && apt-get install -y python3-pip python3-dev gdal-bin gettext libcurl4-openssl-dev libssl-dev yui-compressor python3-gdal git

ENV PATH /usr/local/bin:$PATH
RUN pip3 install --upgrade pip && pip install --upgrade pip

# setup node
RUN curl -sL https://deb.nodesource.com/setup_10.x -o nodesource_setup.sh
RUN bash nodesource_setup.sh
RUN apt-get install nodejs -y
RUN ln -s /usr/bin/python3 /usr/local/bin/python

ADD uganda /uganda
CMD ["/uganda/runme"]