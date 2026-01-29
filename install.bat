@echo off
echo ========================================
echo  Installing Dependencies
echo ========================================
echo.

echo [1/2] Installing Backend Dependencies...
cd backend
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
echo Backend dependencies installed!
echo.

echo [2/2] Installing Frontend Dependencies...
cd ..\frontend
call npm install
echo Frontend dependencies installed!
echo.

echo ========================================
echo  Installation Complete!
echo ========================================
echo.
echo To start the application, run: start.bat
echo.
pause
