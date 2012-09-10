#!/bin/bash

source cerdis.conf
source functions.sh


function usage() {
    echo "Usage: $0 FQDN"
}

if [ -z "$1" ]; then
    usage
    exit 1
fi
FQDN="$1"

getvalues "${CERDIS_FQDN_DN_MAP_PATH}" "${FQDN}"

