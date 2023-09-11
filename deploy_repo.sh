#!/bin/bash
CWD=$1
SERVICE=$2
PORT_INFO=$3
cd $CWD/$SERVICE
# Build Image
docker build -t $SERVICE  ./
#--no-cache
# Run container
docker stop $SERVICE
docker rm $SERVICE
echo 'docker run -it -v "$CWD/$SERVICE/resources:/resources" -p$PORT_INFO -d $SERVICE'
id=$(docker run -it -v "$CWD/$SERVICE/resources:/resources" -p$PORT_INFO -d $SERVICE)
docker rename $id $SERVICE
