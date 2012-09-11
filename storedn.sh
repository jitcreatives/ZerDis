#!/bin/bash

source /etc/cerdis/cerdis.conf
source /etc/cerdis/functions.sh


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

trace "Called: $0 '$1' '$2' '$3'"

CERT="$(findcertbydn "${CERDIS_CERTDIR}" "${DN}")"
KEY="$(getkeybycert "${CERT}")"

if [ -z "${CERT}" ]; then
    warn "No certificate stored for dn '${DN}'"
	exit 2
fi

debug "Store certificate: ${CERT}"
debug "Store key: ${KEY}"

ENCKEY="$(encryptkey "${KEY}" "${PASS}")"
if [ -z "${ENCKEY}" ]; then
    error Could not encrypt private key "'${KEY}'"
    exit 3
fi
trace "Encrypted key: ${ENCKEY}"

X509_USER_CERT="${CERT}" X509_USER_KEY="${KEY}" myproxy-store \
    --pshost "${MYPROXY_SERVER:=localhost}" \
    --psport "${MYPROXY_PORT:=7512}" \
    --certfile "${CERT}" \
    --keyfile "${ENCKEY}" \
    --username "${USER}" \
    &>/dev/null \
|| exit 1

rm "${ENCKEY}"

echo "\"${CERDIS_CERTDIR}/${CERT}\" ${CERDIS_CERTDIR}/${KEY}"

