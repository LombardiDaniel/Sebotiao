#!/bin/bash


for arg in "$@"
do
    case $arg in
        -w|--wipe)
        WIPE_VOLUME=1
        shift # Remove from processing
        ;;
        -h|--help)
        echo "-h, --help    the help command"
        echo "-w, --wipe    wipes the development volume (recreates it)"
        exit 0
        ;;
    esac
done


docker-compose -f docker-compose.development.yml down

if [[ WIPE_VOLUME ]]; then
    docker volume rm "$(basename $PWD)_dev_bot_db"
fi

docker-compose -f docker-compose.development.yml up --build
