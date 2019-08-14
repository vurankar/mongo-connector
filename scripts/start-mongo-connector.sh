#!/bin/bash

declare -A INDEX_NAME_MAP=( ["resourcetypes"]="resource_types"
                     ["propertytypes"]="property_types"
                     ["resourcesandrun_data"]="resources_and_run_data"

                    )


SKIP_INDEX_RESET=${SKIP_INDEX_RESET:-0}
#SKIP_INDEX_RESET  : 0: skip and 1: do not skip


echo " value of SKIP_INDEX_RESET: ${SKIP_INDEX_RESET}"
echo " value of ELASTIC_HOST: ${ELASTIC_HOST}"
echo " value of ELASTIC_PORT: ${ELASTIC_PORT}"
echo " value of MONGO_HOSTS: ${MONGO_HOSTS}"
echo " value of INDEX_NAME: ${INDEX_NAME}"

if [ $SKIP_INDEX_RESET -eq 1 ]
then
    bash elasticsearch-configure.sh -f
else
    echo "skipping elastic search configure because SKIP_INDEX_RESET is set to $SKIP_INDEX_RESET"
fi

INDEX_NAME=${INDEX_NAME:-""}

echo "setting mongo-connector for indices ${INDEX_NAME}"

# $MONGO_HOSTS should be in format HOSTNAME:PORT
# example mongodb01:27017,mongodb02:27017,mongodb03:27017
mongo-connector --auto-commit-interval=0 -m $MONGO_HOSTS -c config/connector_${INDEX_NAME_MAP[$INDEX_NAME]}.json --oplog-ts /srv/riffyn/mongo-connector/oplogts/ -t $ELASTIC_HOST:$ELASTIC_PORT --stdout

sleep 10

echo " FINISHED executing mongo-connector.sh "
