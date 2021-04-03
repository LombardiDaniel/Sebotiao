#!/bin/bash

IMAGE="lombardi/sebotiao"
FETCH="git fetch"
PULL="git pull origin"
COMPOSE_PATH="/usr/local/bin/docker-compose"
COMMAND="$COMPOSE_PATH down && $COMPOSE_PATH up --build -d"
PRJ_PATH=$PWD
LOG_FILE="$PWD/CD.log"

logthis() {
    STR=$1
    echo "`date '+%d/%m/%Y %H:%M:%S'` - $STR" >> "$LOG_FILE"
}

cd $PRJ_PATH

latest=$(git pull origin)

if [[ $latest == "Already up to date." ]]; then
        logthis "Already up to date. Nothing to do."
else
        logthis "Update available. Executing update command..."
        eval $COMMAND
        logthis "Update completed."
fi
