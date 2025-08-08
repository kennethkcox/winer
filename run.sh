#!/bin/bash

IMAGE_NAME="terroir-and-time"
CONTAINER_NAME="terroir-and-time-app"

# Check if Docker is running
DOCKER_INFO_OUTPUT=$(sudo docker info 2>&1)
if [ $? -ne 0 ]; then
    echo "Error: Could not connect to Docker." >&2
    echo "Please ensure Docker is running and you have the necessary permissions." >&2
    echo "Details:" >&2
    echo "$DOCKER_INFO_OUTPUT" >&2
    exit 1
fi

COMMAND="$1"

case "$COMMAND" in
    up)
        echo "Building the Docker image..."
        sudo docker build -t $IMAGE_NAME .

        echo "Starting the application container..."
        sudo docker run -d --rm \
            -p 3000:8000 \
            --name $CONTAINER_NAME \
            -v $(pwd)/data:/app/data \
            $IMAGE_NAME

        echo "Application is running. Access it at http://localhost:3000"
        ;;
    down)
        echo "Stopping the application container..."
        sudo docker stop $CONTAINER_NAME
        echo "Application stopped."
        ;;
    logs)
        echo "Showing logs for the application container..."
        sudo docker logs -f $CONTAINER_NAME
        ;;
    *)
        echo "Usage: ./run.sh [up|down|logs]"
        echo "  up   : Builds and starts the application in detached mode."
        echo "  down : Stops and removes the application container."
        echo "  logs : Follows the logs of the application container."
        ;;
esac
