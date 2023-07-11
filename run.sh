#!/bin/bash

MODE=$1
ENTRY="${2:-src/app.py}"
OTHER=$3

CONTAINER_NAME="paper2video"

# Define cleanup procedure
cleanup() {
    echo "Stopping container..."
    docker stop $(docker ps -q --filter ancestor=$CONTAINER_NAME)
    # Add your cleanup logic here
}

# Trap the SIGINT signal (Ctrl+C) and call the cleanup function
trap cleanup SIGINT

if [ ! "$(docker image ls | grep $CONTAINER_NAME)" ]; then
    echo "Container does not exist. Creating now..."
    docker build . -t $CONTAINER_NAME
else
    echo "Container already exists. Proceeding to the next step..."
fi

if [ "$(docker ps -q --filter ancestor=$CONTAINER_NAME)" ]; then
    echo "Container is already running..."
    cleanup
fi


if [ "$MODE" == "prod" ]; then
    echo "Running the container in production mode..."
    docker run --sig-proxy=false -d -e ENTRY=$ENTR -e ENVIRONMENT=production $OTHER $CONTAINER_NAME
elif [ "$MODE" == "dev" ]; then
    echo "Running the container in development mode..."
    docker run --sig-proxy=false -e ENTRY=$ENTRY -e ENVIRONMENT=development -v .:/app $OTHER $CONTAINER_NAME
else
    echo "Please provide either 'prod' or 'dev' as a parameter to the script."
fi