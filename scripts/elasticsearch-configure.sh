#!/bin/bash

PROG=$0
# expect these parameters to be set prior to running the script
# ELASTIC_HOST="elasticsearch"
# ELASTIC_PORT="9200"
CONFIG_DIR="config"
FORCE=0
OPLOG_TIMESTAMP_LOCATION="/srv/riffyn/mongo-connector/oplogts"

# K8s deployment name follows pattern mongo-connector-indexname
# K8s does not allow _ or uppercase letters in artifact names. So we need to pass
# K8s friendly names to identify index names. This map converts input values to
# actual index names
declare -A INDEX_NAME_MAP=( ["resourcetypes"]="resource_types"
                     ["propertytypes"]="property_types"
                     ["resourcesandrundata"]="resources_and_run_data"

                    )

declare -A INDEX_TO_COLLECTION_MAP=( ["resource_types"]="resourceTypes"
                     ["property_types"]="propertyTypes"
                     ["resources_and_run_data"]="resources_and_run_data"

                    )

echo "Executing elasticsearch-configure.sh ......"
echo " value of INDEX_NAME: ${INDEX_NAME}"
echo " value of ELASTIC_HOST: ${ELASTIC_HOST}"
echo " value of ELASTIC_PORT: ${ELASTIC_PORT}"
echo " value of INDEX_NAME: ${INDEX_NAME}"


INDEX_NAME=${INDEX_NAME:-""}

# convert input K8 friendly index name to actual index name
# Eg: resourcetypes -> resource_types
INDEX_NAME=${INDEX_NAME_MAP[$INDEX_NAME]}

echo "setting mongo-connector for index ${INDEX_NAME}"


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
echo "DELETING oplog.timestamp file  ${OPLOG_TIMESTAMP_LOCATION}/${INDEX_NAME}.oplog.timestamp"
rm ${OPLOG_TIMESTAMP_LOCATION}/${INDEX_NAME}.oplog.timestamp
echo

echo "DELETING  ${INDEX_NAME} INDEX"
curl -XDELETE "$ELASTIC_HOST:$ELASTIC_PORT/$INDEX_NAME" -H 'Content-Type: application/json'
echo


#echo "DELETING MONGODB METADATA"
#curl -XDELETE "$ELASTIC_HOST:$ELASTIC_PORT/mongodb_meta" -H 'Content-Type: application/json'
#echo

echo
echo "SETTING UP ELASTICSEARCH INDEXES"
while curl -XGET "$ELASTIC_HOST:$ELASTIC_PORT/$INDEX_NAME" | grep '"status" : 200'; do
    sleep 1
    echo "Waiting for indiciess to be removed…"
done
echo

echo
echo "Ok to create indices!"
echo

##  NOTE: THE FILE settings.json LIMITS TO 1 SHARD AND NO REPLICAS
# curl -XPUT "$ELASTIC_HOST:$ELASTIC_PORT/mongodb_meta" -H 'Content-Type: application/json'
# echo

curl -XPUT "$ELASTIC_HOST:$ELASTIC_PORT/$INDEX_NAME/?format=yaml" -H 'Content-Type: application/json' -d @$CONFIG_DIR/settings.json
echo


echo
echo "ADDING ${INDEX_TO_COLLECTION_MAP[$INDEX_NAME]} DOC TYPE MAPPING"
curl -XPUT "$ELASTIC_HOST:$ELASTIC_PORT/$INDEX_NAME/_mapping/${INDEX_TO_COLLECTION_MAP[$INDEX_NAME]}?format=yaml" -H 'Content-Type: application/json' -d @$CONFIG_DIR/mapping_$INDEX_NAME.json
echo

echo
echo "FINISHED executing elasticsearch-configure.sh ......"

exit 0
