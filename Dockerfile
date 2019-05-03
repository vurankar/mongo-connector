# Mongo-Connector container
#
# https://github.com/mongodb-labs/mongo-connector

FROM python:3.5-jessie

ENV DEBIAN_FRONTEND noninteractive
RUN pip install --upgrade pip

# Install mongo-connector
WORKDIR "/srv/riffyn/mongo-connector"

ADD mongo-elastic.tar ./
RUN ls -l
RUN pip install elastic2-doc-manager[elastic5]
RUN pip install elastic2-doc-manager/dist/elastic2_doc_manager-*.whl
RUN pip install mongo-connector/dist/mongo_connector-*.whl


ADD config ./config
ADD scripts/elasticsearch-configure.sh ./elasticsearch-configure.sh
ADD scripts/start-mongo-connector.sh ./start-mongo-connector.sh

#ADD mongo-connector .././
#RUN git clone 'https://github.com/RiffynInc/elastic2-doc-manager.git#search'
#ADD elastic2-doc-manager ./elastic2-doc-manager
#RUN pip install './mongo-connector[elastic5]'
#RUN pip install -e ./elastic2-doc-manager[elastic5]

ENTRYPOINT [ "bash", "start-mongo-connector.sh"]
