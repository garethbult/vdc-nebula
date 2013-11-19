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
else
    LIB_LOCATION=$ONE_LOCATION/lib
fi
. $LIB_LOCATION/sh/scripts_common.sh

DRIVER_PATH=$(dirname $(dirname $0))
source ${DRIVER_PATH}/libfs.sh
XPATH="${DRIVER_PATH}/xpath.rb -b $1"
unset i XPATH_ELEMENTS

function vdc_log {
    logger -t vdc-nebula "$1"
}

function execute {
        vdc_log "* exec @$1 $2"
        ssh_exec_and_log "$1" "$2" "$3"
}
