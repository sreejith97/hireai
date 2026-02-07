#!/bin/bash

# Ensure we are in the script's directory
cd "$(dirname "$0")"

# Check if venv exists, if not create it
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt

# Run the application
echo "Starting FastAPI server..."
python3 main.py
