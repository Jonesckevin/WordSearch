@echo off
REM WordSearch GUI Launcher (Windows)

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed
    pause
    exit /b 1
)

REM Check if PyQt6 is installed
python -c "import PyQt6" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing PyQt6...
    pip install -r requirements.txt
)

REM Launch the GUI
python search_gui.py
pause
