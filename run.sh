#!/bin/bash

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Docker is not running. Please start Docker and try again." >&2
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
