#!/bin/bash

SKIP_INDEX_RESET=${SKIP_INDEX_RESET:-0}

if [ $SKIP_INDEX_RESET -eq 1 ]
then
    bash elasticsearch-configure.sh -f
else
    echo "skipping elastic search configure because SKIP_INDEX_RESET is set to $SKIP_INDEX_RESET"
fi

# expect INDEX_LIST environment variable to provide the list of ES indexes this instance of mongo-connector
# should work for. Expect a single index name or a comma separated list
# Eg: "resource_types"  or " resource_types,property_types,resources_and_run_data"
INDEX_LIST=${INDEX_LIST:-""}

echo "setting mongo-connector for indices ${INDEX_LIST}"

# copy the indices into an array
IFS=',' read -r -a INDEX_ARRAY <<< "$INDEX_LIST"


for index in "${INDEX_ARRAY[@]}"
do
    # $MONGO_HOSTS should be in format HOSTNAME:PORT
    # example mongodb01:27017,mongodb02:27017,mongodb03:27017
    mongo-connector --auto-commit-interval=0 -m $MONGO_HOSTS -c config/connector_$index.json -t $ELASTIC_HOST:$ELASTIC_PORT --stdout
    sleep 1
done
