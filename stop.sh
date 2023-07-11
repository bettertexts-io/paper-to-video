#!/bin/bash

CONTAINER_NAME="paper-to-video"

containers_to_stop=$(docker ps -q --filter ancestor=$CONTAINER_NAME)
if [ -n "$containers_to_stop" ]; then
    echo "Stopping containers..."
    docker stop $containers_to_stop
fi

containers_to_remove=$(docker container ls -aq --filter ancestor=$CONTAINER_NAME)
if [ -n "$containers_to_remove" ]; then
    echo "Removing containers..."
    docker rm $containers_to_remove
fi