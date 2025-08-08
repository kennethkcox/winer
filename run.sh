#!/bin/bash

# Check if Docker is running
DOCKER_INFO_OUTPUT=$(docker info 2>&1)
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
        echo "Starting the application with Docker Compose..."
        docker-compose up -d --build
        echo "Application is running. Frontend: http://localhost:3000 | Backend: http://localhost:8000"
        ;;
    down)
        echo "Stopping the application..."
        docker-compose down
        echo "Application stopped."
        ;;
    *)
        echo "Usage: ./run.sh [up|down]"
        echo "  up   : Builds and starts the application in detached mode."
        echo "  down : Stops and removes the application containers."
        ;;
esac
