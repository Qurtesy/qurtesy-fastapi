#!/bin/bash
if [[ "$1" == "-f" ]]; then
    sudo rm -rf db_static
    docker pull adminer
    docker pull postgres
    docker pull python:3.12
fi
docker rmi $(sudo docker images -f 'label=com.qurtesy.finance' -q) -f
docker rm $(sudo docker ps -f status=exited -f 'label=com.qurtesy.finance' -q) -f
sudo docker compose up