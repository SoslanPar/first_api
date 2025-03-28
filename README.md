# first api

## create docker_image
docker build -t first_api_image .

## create run docker_container
docker create --name=first_api_container -p 1311:8000 first_api_image

## run docker_container
docker start first_api_container

## stop docker_container
docker stop first_api_container

## URL
http://localhost:1311

## host in code
host="0.0.0.0"