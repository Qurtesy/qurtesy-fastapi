Build and run docker images

Master
```bash
docker build -f ./dockerfiles/Dockerfile -t fastapi-basicapp-ms1 . && docker run -it --name fastapi-basicapp-ms1 -p 8002:8002 fastapi-basicapp-ms1
```

Run micro service 1
```bash
docker build -f ./dockerfiles/Dockerfile.ms1 -t fastapi-basicapp-ms1 . && docker run -it --name fastapi-basicapp-ms1 -p 8001:8001 fastapi-basicapp-ms1

docker tag fastapi-basicapp-ms1:latest 295920452208.dkr.ecr.ap-south-1.amazonaws.com/fastapi-basicapp-ms1:latest

docker push 295920452208.dkr.ecr.ap-south-1.amazonaws.com/fastapi-basicapp-ms1:latest
```

Run micro service 2
```bash
docker build -f ./dockerfiles/Dockerfile.ms2 -t fastapi-basicapp-ms2 . && docker run -it --name fastapi-basicapp-ms2 -p 8002:8002 fastapi-basicapp-ms2
```

Run micro service 3
```bash
docker build -f ./dockerfiles/Dockerfile.ms3 -t fastapi-basicapp-ms3 . && docker run -it --name fastapi-basicapp-ms3 -p 8003:8003 fastapi-basicapp-ms3
```
