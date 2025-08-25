# This script automates the setup and execution of the Terroir & Time offline game on Windows.
# It ensures a virtual environment is created and all dependencies are installed.

# Get the directory where the script is located
$ScriptPath = $PSScriptRoot

# Set the path for the virtual environment
$VenvPath = Join-Path -Path $ScriptPath -ChildPath "venv"

# Check if the virtual environment directory exists
if (-not (Test-Path -Path $VenvPath -PathType Container)) {
    Write-Host "Virtual environment not found. Creating one..."
    python -m venv $VenvPath
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to create virtual environment. Please ensure you have Python 3 and venv installed."
        exit 1
    }
}

# Activate the virtual environment
. (Join-Path -Path $VenvPath -ChildPath "Scripts\activate.ps1")

# Install dependencies
Write-Host "Installing dependencies from requirements.txt..."
pip install -r (Join-Path -Path $ScriptPath -ChildPath "requirements.txt")

# Run the game
Write-Host "Starting the game..."
python (Join-Path -Path $ScriptPath -ChildPath "main_cli.py")

# Deactivate the virtual environment upon exiting the game
deactivate
Write-Host "Game closed."
