@echo off
echo Starting Quantum-Safe Cryptography Platform Backend...

echo.
echo Activating virtual environment...
call ..\.venv\Scripts\activate.bat

echo.
echo Initializing database...
python init_db.py

echo.
echo Starting Flask server...
python app.py
