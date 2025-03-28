# first api

## create docker_image
docker build -t first_api_image .

## run docker_container
docker run --name=first_api_container -p 1311:8000 first_api_image

## URL
http://localhost:1311

## host in code
host="0.0.0.0"