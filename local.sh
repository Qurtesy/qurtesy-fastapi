#!/bin/bash
if [[ "$1" == "-f" ]]; then
    rm -rf db_static
    docker pull adminer
    docker pull postgres
    docker pull python:3.12
    docker pull amazon/aws-cli
    docker rmi $(docker images -q) -f
    docker rm $(docker ps -f status=exited -q) -f
    docker compose up
else
    docker rmi $(docker images -f 'label=com.qurtesy.finance' -q) -f
    docker rm $(docker ps -f status=exited -f 'label=com.qurtesy.finance' -q) -f
    docker compose up
fi