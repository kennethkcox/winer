param (
    [string]$command
)

# Check if Docker is running
$dockerRunning = docker info > $null 2>&1
if (-not $dockerRunning) {
    Write-Host "Docker is not running. Please start Docker Desktop and try again." -ForegroundColor Red
    exit 1
}

switch ($command) {
    "up" {
        Write-Host "Starting the application with Docker Compose..."
        docker-compose up -d --build
        Write-Host "Application is running. Frontend: http://localhost:3000 | Backend: http://localhost:8000" -ForegroundColor Green
    }
    "down" {
        Write-Host "Stopping the application..."
        docker-compose down
        Write-Host "Application stopped." -ForegroundColor Green
    }
    default {
        Write-Host "Usage: ./run-windows.ps1 [up|down]"
        Write-Host "  up   : Builds and starts the application in detached mode."
        Write-Host "  down : Stops and removes the application containers."
    }
}
