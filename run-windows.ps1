param (
    [string]$command
)

# Check if Docker is running
$dockerInfoOutput = docker info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Could not connect to Docker." -ForegroundColor Red
    Write-Host "Please ensure Docker is running and you have the necessary permissions." -ForegroundColor Red
    Write-Host "Details:" -ForegroundColor Red
    Write-Host $dockerInfoOutput -ForegroundColor Red
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
