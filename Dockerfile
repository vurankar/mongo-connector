# Mongo-Connector container
#
# https://github.com/mongodb-labs/mongo-connector

FROM python:2.7.15-jessie

ENV DEBIAN_FRONTEND noninteractive
RUN pip install --upgrade pip

# Install mongo-connector
WORKDIR "/srv/riffyn/mongo-connector"

ADD mongo-connector.tar ./
RUN pip install /srv/riffyn/mongo-connector/dist/mongo_connector-*.whl

ADD config ./config
ADD elasticsearch-configure.sh ./scripts/elasticsearch-configure.sh
ADD start-mongo-connector.sh ./scripts/start-mongo-connector.sh

ADD mongo-connector .././
RUN git clone 'https://github.com/RiffynInc/elastic2-doc-manager.git#search'
ADD elastic2-doc-manager ./elastic2-doc-manager
RUN pip install './mongo-connector[elastic5]'
RUN pip install -e ./elastic2-doc-manager[elastic5]

ENTRYPOINT [ "bash", "start-mongo-connector.sh"]
