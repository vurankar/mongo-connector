# Mongo-Connector container
#
# https://github.com/mongodb-labs/mongo-connector

FROM python:3.5-jessie

ENV DEBIAN_FRONTEND noninteractive
RUN pip install --upgrade pip

# Install mongo-connector
WORKDIR "/srv/riffyn/mongo-connector"
# the mongo-elastic.tar contains the mongo-connector and elastic2_doc_manager whls
ADD mongo-elastic.tar ./
RUN ls -l
# The order of installation is important. The commands overwrite previous commands.
# elastic2-doc-manager automatically installs stock-mongo connector.
# install stock elastic2-doc-manager because this brings in all the dependencies
RUN pip install elastic2-doc-manager[elastic5]
# then patch the modified elastic2_doc_manager to see our custom changes
RUN pip install elastic2-doc-manager/dist/elastic2_doc_manager-*.whl
# patch mongo_connector with our custom mongo_connector
RUN pip install mongo-connector/dist/mongo_connector-*.whl


ADD config ./config
ADD scripts/elasticsearch-configure.sh ./elasticsearch-configure.sh
ADD scripts/start-mongo-connector.sh ./start-mongo-connector.sh

#ADD mongo-connector .././
#RUN git clone 'https://github.com/RiffynInc/elastic2-doc-manager.git#6.7
#ADD elastic2-doc-manager ./elastic2-doc-manager
#RUN pip install './mongo-connector[elastic5]'
#RUN pip install -e ./elastic2-doc-manager[elastic5]

ENTRYPOINT [ "bash", "start-mongo-connector.sh"]
