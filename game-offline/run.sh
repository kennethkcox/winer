#!/bin/bash

# This script automates the setup and execution of the Terroir & Time offline game.
# It ensures a virtual environment is created and all dependencies are installed.

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

VENV_DIR="venv"

# Check if the virtual environment directory exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv $VENV_DIR
    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment. Please ensure you have Python 3 and venv installed."
        exit 1
    fi
fi

# Activate the virtual environment
source "$VENV_DIR/bin/activate"

# Install dependencies
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

# Run the game
echo "Starting the game..."
python main_cli.py

# Deactivate the virtual environment upon exiting the game
deactivate
echo "Game closed."
