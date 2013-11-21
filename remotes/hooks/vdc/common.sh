#!/bin/bash
# -------------------------------------------------------------------------- #
# Copyright 2013, Gareth Bult <gareth@linux.co.uk>                           #
#                                                                            #
# Licensed under the Apache License, Version 2.0 (the "License"); you may    #
# not use this file except in compliance with the License. You may obtain    #
# a copy of the License at                                                   #
#                                                                            #
# http://www.apache.org/licenses/LICENSE-2.0                                 #
#                                                                            #
# Unless required by applicable law or agreed to in writing, software        #
# distributed under the License is distributed on an "AS IS" BASIS,          #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.   #
# See the License for the specific language governing permissions and        #
# limitations under the License.                                             #
#--------------------------------------------------------------------------- #
if [ -z "${ONE_LOCATION}" ]; then
    LIB_LOCATION=/usr/lib/one
    TMCOMMON=/var/lib/one/remotes/tm/tm_common.sh
else
    LIB_LOCATION=$ONE_LOCATION/lib
    TMCOMMON=$ONE_LOCATION/var/remotes/tm/tm_common.sh
fi
. $LIB_LOCATION/sh/scripts_common.sh
. $TMCOMMON

DRIVER_PATH=${ROOT}/datastore
source ${DRIVER_PATH}/libfs.sh
if [ -z ${TEMP} ] ; then
    XPATH="${DRIVER_PATH}/xpath.rb -b $1"
else
    XPATH="${DRIVER_PATH}/xpath.rb -b $TEMP"
fi
unset i XPATH_ELEMENTS

function vdc_log {
    logger -t vdc-nebula "$1"
}

function execute {
        vdc_log "* exec @$1 $2"
        ssh_exec_and_log "$1" "$2" "$3"
}

function vdc_image_hash {
    echo "`date +%s%N|md5sum|cut -d" " -f1`"
}

function vdc_make_path
{
    SSH_EXEC_ERR=`$SSH $1 sh -s 2>&1 1>/dev/null <<EOF
    mkdir $2
EOF`
    SSH_EXEC_RC=$?

    if [ $? -ne 0 ]; then
        error_message "Error creating directory $2 at $1: $SSH_EXEC_ERR"
        exit $SSH_EXEC_RC
    fi
}
