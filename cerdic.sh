#!/bin/bash

source cerdic.conf
source functions.sh


function usage() {
    echo "Usage:"
    echo "$0 init"
    echo " or"
    echo "$0 update"
}

if [ ! "$#" -eq 1 ]; then
    usage
    exit 1
fi
COMMAND="$1"
shift

function cerdic_init() {
    # Get all dns and...
    ssh "${CERDIS_USER}@${CERDIS_HOST}" getdnbyfqdn.sh "${FQDN}" | \
    while read DN; do

        # generate user and password
        USER="${FQDN}.$(echo "${DN}" | md5sum | cut -d' ' -f1)"
        PASS="$(pwgen 12 | head -n1)"

        # let each certificate be stored by generated token
        PAIR="$(ssh "${CERDIS_USER}@${CERDIS_HOST}" storedn.sh "${USER}" "${PASS}" "${DN}")"
        REMOTECERTPATH="$(echo "${PAIR}" | getkeys)"
        REMOTEKEYPATH="$(getvalue "${PAIR}")"

        # get CN of DN
        CN="$(getcnofdn "${DN}")"

        CERT="${CERDIC_CREDENTIALS_PATH}/${CN}.crt"
        KEY="${CERDIC_CREDENTIALS_PATH}/${CN}.key"

        scp "${CERDIS_USER}@${CERDIS_HOST}:${REMOTECERTPATH}" "${CERT}"
        scp "${CERDIS_USER}@${CERDIS_HOST}:${REMOTEKEYPATH}" "${KEY}"

        # store token
        multimap_put "${DN}" "${USER} ${PASS}" "${CERDIC_DN_TOKEN_MAP}"
    done
}


function cerdic_update() {
    # Get all dns
    # check validity of each corresponding certificate and
    # update it or send mail about it 

    # Get all dns and...
    ssh "${CERDIS_USER}@${CERDIS_HOST}" getdnbyfqdn.sh "${FQDN}" | \
    while read DN; do

        # get user and password
        PAIR="$(getvalues "${DN}" "${CERDIC_DN_TOKEN_MAP}")"
        USER="$(echo "${PAIR}" | getkeys)"
        PASS="$(getvalue "${PAIR}")"

        # get CN of DN
        CN="$(getcnofdn "${DN}")"

        CERT="${CERDIC_CREDENTIALS_PATH}/${CN}.crt"
        KEY="${CERDIC_CREDENTIALS_PATH}/${CN}.key"

        if certificate_valid "${CERT}" "${PERIOD}"; then
            continue
        fi

        # retrieve stored certificate
        echo "${PASS}" | X509_USER_CERT="${CERT}" X509_USER_KEY="${KEY}" myproxy-retrieve \
            --pshost "${MYPROXY_SERVER:=localhost}" \
            --psport "${MYPROXY_PORT:=7512}" \
            --certfile "${CERT}" \
            --keyfile "${ENCKEY}" \
            --username "${USER}"

        if certificate_valid "${CERT}" "${PERIOD}"; then
            continue
        fi

        # send mail to admin if there has not been a new certificate
        ENDDATE=$(openssl x509 -in "${CERT}" -noout -enddate | cut -d'=' -f2)
        mail -s "Certificate expires!" \
                "${ADMINEMAIL}" \
                "Certificate '${DN}' on '${FQDN}' will expire on ${ENDDATE}."
    done
}

case ${COMMAND} in
    init)
        cerdic_init
        ;;

    update)
        cerdic_update
        ;;
esac
