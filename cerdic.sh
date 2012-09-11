#!/bin/bash

source /etc/cerdis/cerdic.conf
source /etc/cerdis/functions.sh


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
    TRACE="${TRACE}" \
    DEBUG="${DEBUG}" \
    INFO="${INFO}" \
    WARN="${WARN}" \
    ERROR="${ERROR}" \
    ssh "${CERDIS_USER}@${CERDIS_HOST}" getdnbyfqdn.sh "${FQDN}" | \
    while read DN; do

        trace "Initialization for DN: '${DN}'"

        # generate user and password
        USER="${FQDN}.$(echo "${DN}" | md5sum | cut -d' ' -f1)"
        PASS="$(pwgen 12 | head -n1)"

        # let each certificate be stored by generated token
        trace "Calling: ssh '${CERDIS_USER}@${CERDIS_HOST}' \"storedn.sh '${USER}' '${PASS}' '${DN}'\""
        PAIR="$( \
            TRACE="${TRACE}" \
            DEBUG="${DEBUG}" \
            INFO="${INFO}" \
            WARN="${WARN}" \
            ERROR="${ERROR}" \
            ssh "${CERDIS_USER}@${CERDIS_HOST}" "storedn.sh '${USER}' '${PASS}' '${DN}'")"
        if [ -z "${PAIR}" ]; then
#                info "Could not find credentials for '${DN}' on remote host"
                exit 2
        fi

        REMOTECERTPATH="$(echo "${PAIR}" | getkeys)"
        REMOTEKEYPATH="$(getvalue "${PAIR}")"
        debug "Remote path for certificate: ${REMOTECERTPATH}"

        # get CN of DN
        CN="$(getcnofdn "${DN}")"

        CERT="${CERDIC_CREDENTIALS_PATH}/${CN}.crt"
        KEY="${CERDIC_CREDENTIALS_PATH}/${CN}.key"
        trace "Local path for certificate: ${CERT}"

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
        debug "Update for DN: '${DN}'"

        PAIR="$(getvalues "${DN}" "${CERDIC_DN_TOKEN_MAP}")"
        USER="$(echo "${PAIR}" | getkeys)"
        PASS="$(getvalue "${PAIR}")"
        trace "User: '${USER}' '${PASS}'"

        # get CN of DN
        CN="$(getcnofdn "${DN}")"

        CERT="${CERDIC_CREDENTIALS_PATH}/${CN}.crt"
        KEY="${CERDIC_CREDENTIALS_PATH}/${CN}.key"
        trace "Updating '${CERT}' and '${KEY}'"

        if [ ! -e "${CERT}" -o ! -e "${KEY}" ]; then
                warn "Could not update Certificate, since there is no old version."
                continue
        fi

        if certificate_valid "${CERT}" "${PERIOD}"; then
            debug "Certificate still valid"
            continue
        fi

        debug "Updating certificate..."

        # retrieve stored certificate
        trace "Calling: X509_USER_CERT=\"${CERT}\" X509_USER_KEY=\"${KEY}\" myproxy-retrieve \
            --pshost \"${MYPROXY_SERVER:=localhost}\" \
            --psport \"${MYPROXY_PORT:=7512}\" \
            --certfile \"${CERT}\" \
            --keyfile \"${ENCKEY}\" \
            --username \"${USER}\""
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
        ISSUER=$(openssl x509 -in "${CERT}" -noout -issuer | cut -d'=' -f2)
        {
            echo "Certificate '${DN}' signed by '${ISSUER}' on '${FQDN}' will expire on ${ENDDATE}."
        } | \
        mail -s "Certificate expires!" \
                "${ADMINEMAIL}"
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
