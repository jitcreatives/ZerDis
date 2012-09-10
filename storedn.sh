#!/bin/bash

source cerdis.conf
source functions.sh


function usage() {
    echo "Usage: $0 USER PASSWORD DN"
}

if [ ! "$#" -eq 3 ]; then
    usage
    exit 1
fi
USER="$1"
PASS="$2"
DN="$3"

CERT="$(findcertbydn "${CERDIS_CERTDIR}" "${DN}")"
KEY="$(getkeybycert "${CERT}")"
ENCKEY="$(encryptkey "${KEY}" "${PASS}")"
if [ -z "${ENCKEY}" ]; then
    echo Could not encrypt private key "'${KEY}'"
    exit 2
fi

X509_USER_CERT="${CERT}" X509_USER_KEY="${KEY}" myproxy-store \
    --pshost "${MYPROXY_SERVER:=localhost}" \
    --psport "${MYPROXY_PORT:=7512}" \
    --certfile "${CERT}" \
    --keyfile "${ENCKEY}" \
    --username "${USER}" \
    &>/dev/null \
|| exit 1

echo "\"${CERDIS_CERTDIR}/${CERT}\" ${CERDIS_CERTDIR}/${KEY}"

