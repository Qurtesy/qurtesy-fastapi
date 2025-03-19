# sudo rm -rf db_static
# docker compose down --volumes
docker rm $(sudo docker ps -f status=exited -f 'label=com.qurtesy.finance' -q) -f
docker rmi $(sudo docker images -f 'label=com.qurtesy.finance' -q) -f
sudo docker compose up