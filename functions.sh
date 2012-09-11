#!/bin/bash

################################################################################
# Multimap


## Get all key value pairs of a multimap in a certain file to a certain key.
# \param KEY The key to get the pairs for.
# \param MAPFILE The file to read the multimap from.
# \return Print all pairs to stdout.
function getpairs() {
    KEY="$1"
    MAPFILE="${2:--}"

    # grep all key value pairs matching KEY
    grep -F "\"${KEY}\"" "${MAPFILE}" | \
    while read PAIR; do
        echo "${PAIR:${#KEY}+2}" | {
            read VALUE
            echo "\"${KEY}\" ${VALUE}"
        }
    done
}


## Get the value of a pair.
# \param PAIR The pair to get the value from.
# \return Prints the value
function getvalue() {
    PAIR="${1}"
    KEY="$(echo "${PAIR}" | cut -d'"' -f2)"

    echo "${PAIR:${#KEY}+2}" | {
        read VALUE;
        echo "${VALUE}"
    }
}


## Get all values of a multimap in a certain file to a certain key.
# \param KEY The key to get the values for.
# \param MAPFILE The file to read the multimap from.
# \return Print all values of KEY to stdout.
function getvalues() {
    KEY="$1"
    MAPFILE="${2:--}"

    # grep all key value pairs matching KEY
    grep -F "\"${KEY}\"" "${MAPFILE}" | \
    while read PAIR; do
        echo "${PAIR:${#KEY}+2}" | {
            read VALUE;
            echo "${VALUE}"
        }
    done
}

## Get all keys of a multimap in a certain file.
# \param MAPFILE The file to read the multimap from.
# \return Print all keys to stdout.
function getkeys() {
    MAPFILE="${1:--}"

    # grep all keys
    grep -oE "^\"[^\"]*\"" "${MAPFILE}" | \
    while read KEY; do
        echo "${KEY:1:${#KEY}-2}"
    done | \
    sort | \
    uniq
}


function _multimap_put() {
    KEY="$1"
    VALUE="$2"

    {
        cat -
        echo "\"${KEY}\"" "${VALUE}"
    } | sort | uniq

}


## Add a new key value pair to the multimap
# \param KEY The key to store.
# \param VALUE The value of the key.
# \param MAPFILE Which mapfile to manipulate.
function multimap_put() {
    KEY="$1"
    VALUE="$2"
    MULTIMAP="${3:-}"

    if [ -z "$3" ]; then
        _multimap_put "${KEY}" "${VALUE}"
    else
        MAP="$(cat "${MULTIMAP}")"

        echo -e "${MAP}" | \
        _multimap_put "${KEY}" "${VALUE}" \
        > "${MULTIMAP}"
    fi
}



################################################################################
# Timing utils

## Prints the number of seconds since 1970.
# \param DATE The date to convert.
# \return The converted time in unix.
function getunixtimebydate() {
    DATE="$1"

    date -d "$DATE" +%s
}

################################################################################
# Certificate utils

## Find the path of a certificate by its dn.
# \param DIR The path to search recursively.
# \param DN The dn to search for.
# \return Prints all paths of matching certificates.
function findcertbydn() {
    DIR="$1"
    DN="$2"

    # find all files recursively
    find "${DIR}" -type f | \
    while read CERT; do
        # filter all certificates with matching dn
        openssl x509 -noout -subject -in "${CERT}" 2>/dev/null | \
        grep -F "${DN}" &>/dev/null

        if [ $? -eq 0 ]; then
            # get longest applicable certificate
            ENDDATE="$(openssl x509 -noout -enddate -in ${CERT} | cut -d'=' -f2-)"
            ENDTIME="$(getunixtimebydate "${ENDDATE}")"
            echo "${ENDTIME} ${CERT}"
        fi
    done | \
    sort -g | \
    head -n1 | \
    cut -d' ' -f2-
}


## Get the path of a key according to a certificate.
# \param CERT The certificate to get the key for.
# \return Prints the path of the key.
function getkeybycert() {
    BASE="${1%.crt}"
    echo "${BASE}.key"
}


## Encrypts an rsa key.
# \param KEY The key to encrypt.
# \param PASSPHRASE The passphrase to use for encryption.
# \return Prints the location of the encrypted key.
function encryptkey() {
    KEY="$1"
    PASSPHRASE="$2"
    UUID=$(uuid)
    KEYOUT="/tmp/cerdis.${UUID}.enc.key"

    openssl rsa -des3 -in "${KEY}" -passout pass:"${PASSPHRASE}" -out "${KEYOUT}" &>/dev/null && \
    echo "${KEYOUT}"
}


## Get the CN of a DN.
# \param DN The dn to get the cn from.
# \return Prints the cn.
function getcnofdn() {
    DN="$1"
    CN="${DN##*CN=}"
    CN="${CN%%/*}"

    echo "${CN}"
}


## Check validity of a certificate regarding expiration.
# \param CERT The location of the certificate to check.
# \param PERIOD How much forerun should be cared for.
# \return 0 on success
certificate_valid() {
        CERT="$1"
        shift
        PERIOD=$*

        local ENDDATE=$(openssl x509 -in "${CERT}" -noout -enddate | cut -d'=' -f2)
        local ENDTIME=$(date -d "${ENDDATE} ${PERIOD}" +%s)
        local TODAY=$(date +%Y-%m-%d)
        local NOW=$(date -d "${TODAY}" +%s)

        test $((${ENDTIME} - ${NOW})) -ge 0
}

################################################################################
# misc utils

function error() {
    if [ -n "${ERROR}" -o -n "${WARN}" -o -n "${INFO}" -o -n "${DEBUG}" -o -n "${TRACE}" ]; then
        if [ 0 -eq $# ]; then
            echo -n "ERROR: " >&2
            cat - >&2
        else
            echo "ERROR: $@" >&2
        fi
    fi
}


function warn() {
    if [ -n "${WARN}" -o -n "${INFO}" -o -n "${DEBUG}" -o -n "${TRACE}" ]; then
        if [ 0 -eq $# ]; then
            echo -n "WARN: " >&2
            cat - >&2
        else
            echo "WARN: $@" >&2
        fi
    fi
}


function info() {
    if [ -n "${INFO}" -o -n "${DEBUG}" -o -n "${TRACE}" ]; then
        if [ 0 -eq $# ]; then
            echo -n "INFO: " >&2
            cat - >&2
        else
            echo "INFO: $@" >&2
        fi
    fi
}


function debug() {
    if [ -n "${DEBUG}" -o -n "${TRACE}" ]; then
        if [ 0 -eq $# ]; then
            echo -n "DEBUG: " >&2
            cat - >&2
        else
            echo "DEBUG: $@" >&2
        fi
    fi
}


function trace() {
    if [ -n "${TRACE}" ]; then
        if [ 0 -eq $# ]; then
            echo -n "TRACE: " >&2
            cat - >&2
        else
            echo "TRACE: $@" >&2
        fi
    fi
}
