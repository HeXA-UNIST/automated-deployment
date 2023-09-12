#!/bin/bash
CWD=$1
SERVICE=$2
PORT_INFO=$3
VOLUME_ARG=$4
cd $CWD/$SERVICE
# Build Image
docker build -t $SERVICE  ./
#--no-cache
# Run container
docker stop $SERVICE
docker rm $SERVICE
docker run -it $VOLUME_ARG -p$PORT_INFO -d --name $SERVICE $SERVICE