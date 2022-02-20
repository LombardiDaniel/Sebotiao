#!/bin/bash

SCRIPT=$(readlink -f $0)
PRJ_PATH=`dirname $SCRIPT`

cd $PRJ_PATH

IMAGE="lombardi/reddbot"
FETCH="git fetch"
PULL="git pull origin"
COMPOSE_PATH="/usr/local/bin/docker-compose"
COMMAND="docker build . && $COMPOSE_PATH down && $COMPOSE_PATH up --build -d"
LOG_FILE="$PRJ_PATH/logs/CD.log"

logthis() {
    STR=$1
    echo "`date '+%d/%m/%Y %H:%M:%S'`; $STR;" >> "$LOG_FILE"
}

latest=$(git pull origin)

if [[ $latest == "Already up to date." ]]; then
    # logthis "Already up to date. Nothing to do;"
    :
else
    logthis "Update available. Executing update command;"
    eval $COMMAND
    logthis "Update completed;"
fi
