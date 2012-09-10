#!/bin/bash

source /etc/cerdis/cerdis.conf
source /etc/cerdis/functions.sh


function usage() {
    echo "Usage: $0 FQDN"
}

if [ -z "$1" ]; then
    usage
    exit 1
fi
FQDN="$1"

getvalues ${FQDN} "${CERDIS_FQDN_DN_MAP_PATH}"

