#!/bin/bash
# Start the backend server for Quantum-Cryptography-Project (Linux)

echo "Starting Quantum-Safe Cryptography Platform Backend..."

echo ""
echo "Checking for virtual environment..."
if [ ! -d ".venv" ] || [ ! -f ".venv/bin/activate" ]; then
    if [ -d ".venv" ]; then
        echo "Virtual environment directory exists but is corrupted. Removing and recreating..."
        rm -rf .venv
    else
        echo "Virtual environment not found. Creating new virtual environment..."
    fi
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment. Please ensure Python is installed."
        exit 1
    fi
    echo "Virtual environment created successfully!"
else
    echo "Virtual environment found."
fi

echo ""
echo "Activating virtual environment..."
source .venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Failed to activate virtual environment."
    exit 1
fi

echo ""
echo "Checking and installing requirements..."
pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Failed to install requirements."
    exit 1
fi

echo ""
echo "Initializing database..."
cd backend
if [ ! -d "instance" ]; then
    mkdir instance
fi
python init_db.py
if [ $? -ne 0 ]; then
    echo "Failed to initialize database."
    exit 1
fi

echo ""
echo "Starting Flask server..."
python3 app.py
