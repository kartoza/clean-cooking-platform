#--------- Generic stuff all our Dockerfiles should start with so we get caching ------------
FROM geonode/spcgeonode:django-3.0
MAINTAINER Dimas Ciputra<dimas@kartoza.com>

RUN mkdir -p /usr/share/man/man1
RUN apt-get update -y && apt-get -y --allow-downgrades --allow-remove-essential --allow-unauthenticated install yui-compressor rpl mdbtools git gdal-bin python-gdal
RUN echo "Activate memcached" && \
    apt-get update && apt-get install -y memcached && \
    pip install pylibmc  && pip install sherlock

WORKDIR /spcgeonode

# TODO: base repo : https://github.com/kartoza/geonode/commit/4f64450061046881aea74ea43673965440318e64
RUN git pull https://github.com/kartoza/geonode.git 3.2.1
RUN pip install -r requirements.txt

RUN pip uninstall -y django-geonode-mapstore-client

ADD deployment/docker/REQUIREMENTS.txt /REQUIREMENTS.txt
RUN pip uninstall -y celery && pip install -r /REQUIREMENTS.txt
#
#USER www-data
ADD django_project /home/web/django_project
WORKDIR /home/web/django_project

RUN curl -sL https://deb.nodesource.com/setup_16.x | bash - && \
      apt-get install -y nodejs && cd custom && \
      npm install --quiet -g webpack@4.16.5 && \
      npm install --quiet -g webpack-cli@4.2.0 && \
      npm install --quiet && webpack --mode production

# Open port 8080 as we will be running our uwsgi socket on that
#EXPOSE 8080

ADD deployment/docker/entrypoint.sh /entrypoint.sh
ADD deployment/docker/initialize.py /initialize.py
ADD deployment/docker/uwsgi.conf /uwsgi.conf
ENTRYPOINT ["/entrypoint.sh"]
CMD ["uwsgi", "--ini", "/uwsgi.conf"]
