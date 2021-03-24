FROM ubuntu:18.04
MAINTAINER Irwan Fathurrahman<irwan@kartoza.com>

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

# setup project
WORKDIR /home/explorer
RUN npm install
RUN npm install -g gulp-cli
RUN npm install -g yarn

COPY setup.sh /usr/local/bin/
RUN ln -s /usr/local/bin/setup.sh