@echo off
echo Starting Quantum-Safe Cryptography Platform Backend...

echo.
echo Checking for virtual environment...
if not exist .venv (
    echo Virtual environment not found. Creating new virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo Failed to create virtual environment. Please ensure Python is installed.
        pause
        exit /b 1
    )
    echo Virtual environment created successfully!
) else (
    echo Virtual environment found.
)

echo.
echo Activating virtual environment...
call .venv\Scripts\activate
if errorlevel 1 (
    echo Failed to activate virtual environment.
    pause
    exit /b 1
)

echo.
echo Checking and installing requirements...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo Failed to install requirements.
    pause
    exit /b 1
)

echo.
echo Initializing database...
cd backend
if not exist instance mkdir instance
python init_db.py
if errorlevel 1 (
    echo Failed to initialize database.
    pause
    exit /b 1
)

echo.
echo Starting Flask server...
python app.py
