#!/bin/bash

# 2D to 3D Converter - Startup Script
# This script starts the Flask backend server

echo "=========================================="
echo "2D to 3D Model Converter"
echo "Starting Backend Server..."
echo "=========================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating..."
    python3 -m venv venv
    echo "Virtual environment created."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if [ ! -f "backend/requirements.txt" ]; then
    echo "Error: requirements.txt not found!"
    exit 1
fi

echo "Checking dependencies..."
pip install -q -r backend/requirements.txt

# Start Flask server
echo "Starting Flask server..."
echo ""
cd backend
python app.py
