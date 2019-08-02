#!/bin/bash

PROG=$0
# expect these parameters to be set prior to running the script
# ELASTIC_HOST="elasticsearch"
# ELASTIC_PORT="9200"
CONFIG_DIR="config"
FORCE=0

declare -A INDEX_TO_COLLECTION_MAP=( ["resource_types"]="resourceTypes"
                     ["property_types"]="propertyTypes"
                     ["resources_and_run_data"]="resources_and_run_data"

                    )

# expect INDEX_LIST environment variable to provide the list of ES indexes this instance of mongo-connector
# should work for. Expect a single index name or a comma separated list
# Eg: "resource_types"  or "resource_types,property_types,resources_and_run_data"
INDEX_LIST=${INDEX_LIST:-""}

echo "setting mongo-connector for indices ${INDEX_LIST}"

# copy the indices into an array
IFS=',' read -r -a INDEX_ARRAY <<< "$INDEX_LIST"

function usage {
    echo "usage: $PROG [-f] [-h]"
    echo
    echo "clears all Elasticsearch indexes and reconfigures with the definitions in $CONFIG_DIR"
    echo
    echo "connects to $ELASTIC_HOST:$ELASTIC_PORT"
    echo
    echo "    -f    force clear/reconfigure, skips confirmation"
    echo "    -h    display this help text"
    echo
}

while getopts "fh" opt; do
    case $opt in
        f)
            echo "forcing operation / skipping confirmation"
            echo
            FORCE=1
        ;;
        h)
            usage
            exit 0
        ;;
        *)
            usage
            exit
        ;;
    esac
done

if [ $FORCE != 1 ]; then
    echo
    echo "WARNING! THIS WILL DELETE ALL ELASTICSEARCH INDEXES AND DATA AND RECONFIGURE ELASTICSEARCH"
    read -r -p "DO YOU WISH TO PROCEED? [y/N] " CONFIRMATION
    echo
    if [[ "$CONFIRMATION" =~ ^([yY][eE][sS]|[yY])+$ ]]; then
        echo "CONFIRMED - PROCEEDING"
        echo
    else
        echo "NOT CONFIRMED - ABORTING"
        echo
        exit 0
    fi
else
    echo
    echo "FORCE IS TRUE - PROCEEDING"
    echo
fi

##
##  DELETE/RECREATE/RECONFIGURE INDEXES AND MAPPINGS
##

for index in "${INDEX_ARRAY[@]}"
do
    echo "DELETING  $index INDEX"
    curl -XDELETE "$ELASTIC_HOST:$ELASTIC_PORT/$index" -H 'Content-Type: application/json'
    echo
done


#echo "DELETING MONGODB METADATA"
#curl -XDELETE "$ELASTIC_HOST:$ELASTIC_PORT/mongodb_meta" -H 'Content-Type: application/json'
#echo

echo
echo "SETTING UP ELASTICSEARCH INDEXES"
while curl -XGET "$ELASTIC_HOST:$ELASTIC_PORT/$INDEX_LIST,mongodb_meta" | grep '"status" : 200'; do
    sleep 1
    echo "Waiting for indiciess to be removed…"
done
echo

echo
echo "Ok to create indices!"
echo

##  NOTE: THE FILE settings.json LIMITS TO 1 SHARD AND NO REPLICAS
curl -XPUT "$ELASTIC_HOST:$ELASTIC_PORT/mongodb_meta" -H 'Content-Type: application/json'
echo

for index in "${INDEX_ARRAY[@]}"
do
    curl -XPUT "$ELASTIC_HOST:$ELASTIC_PORT/$index/?format=yaml" -H 'Content-Type: application/json' -d @$CONFIG_DIR/settings.json
    echo
done


for index in "${INDEX_ARRAY[@]}"
do
    #curl -XPUT "$ELASTIC_HOST:$ELASTIC_PORT/$index/?format=yaml" -H 'Content-Type: application/json' -d @$CONFIG_DIR/settings.json
    echo
    echo "ADDING $INDEX_TO_COLLECTION_MAP[$index] DOC TYPE MAPPING"
    curl -XPUT "$ELASTIC_HOST:$ELASTIC_PORT/$index/_mapping/$INDEX_TO_COLLECTION_MAP[$index]?format=yaml" -H 'Content-Type: application/json' -d @$CONFIG_DIR/mapping_$index.json
    echo
done

echo
echo "FINISHED"

exit 0
