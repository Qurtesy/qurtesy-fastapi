kill -9 $(sudo lsof -t -i:5432)
docker-compose down --volumes
docker image prune -a --filter "until=$(date +'%Y-%m-%dT%H:%M:%S' --date='-30 days')"
docker rmi $(sudo docker images -f 'dangling=true' -q) -f
docker-compose -f docker-compose.yml up $1 $2