@echo off
title RITU BACKEND - DO NOT CLOSE THIS WINDOW
cd /d "%~dp0backend"

echo.
echo   ============================================
echo      R I T U   -   B A C K E N D
echo      Team THEPLAYERS - recHERsion 2026
echo   ============================================
echo.

REM ---- Find Python (tries python, py launcher, then common folders) ----
echo [STEP 1 of 4] Looking for Python...

set "PYEXE="

python --version >nul 2>&1
if not errorlevel 1 set "PYEXE=python" & goto :found

py --version >nul 2>&1
if not errorlevel 1 set "PYEXE=py" & goto :found

for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python3*") do (
    if exist "%%D\python.exe" set "PYEXE=%%D\python.exe" & goto :found
)

if exist "C:\Python313\python.exe" set "PYEXE=C:\Python313\python.exe" & goto :found
if exist "C:\Python312\python.exe" set "PYEXE=C:\Python312\python.exe" & goto :found
if exist "C:\Python311\python.exe" set "PYEXE=C:\Python311\python.exe" & goto :found

echo.
echo   XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
echo   ERROR: Python not found on this computer.
echo.
echo   Do this:
echo     1. Go to  https://www.python.org/downloads/
echo     2. Download Python
echo     3. Run the installer
echo     4. TICK the box "Add python.exe to PATH"
echo     5. Click Install Now
echo     6. Double-click START-BACKEND.bat again
echo   XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
echo.
pause
exit /b

:found
echo   Found Python:
%PYEXE% --version
echo.

REM ---- Create virtual environment ----
if not exist ".venv" (
    echo [STEP 2 of 4] Creating virtual environment...
    "%PYEXE%" -m venv .venv
    if errorlevel 1 (
        echo   ERROR: could not create virtual environment.
        pause
        exit /b
    )
) else (
    echo [STEP 2 of 4] Virtual environment already exists, skipping.
)
echo.

REM ---- Install packages ----
echo [STEP 3 of 4] Installing packages.
echo   First time takes 1-3 minutes. Please wait...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip -q
pip install -q -r requirements.txt
if errorlevel 1 (
    echo   Retrying with the minimal package set...
    pip install -q fastapi uvicorn pydantic python-dotenv python-multipart
)
if errorlevel 1 (
    echo.
    echo   ERROR: Could not install packages.
    echo   Check your internet connection, then try again.
    echo.
    pause
    exit /b
)
echo   Packages installed.
echo.

REM ---- Seed data and run ----
echo [STEP 4 of 4] Loading demo data and starting the server...
echo.
python seed.py pcos
echo.
echo   ============================================
echo     BACKEND IS RUNNING
echo     http://localhost:8000
echo     API docs: http://localhost:8000/docs
echo.
echo     >>> KEEP THIS WINDOW OPEN <<<
echo     Minimize it if you like, do not close it.
echo   ============================================
echo.
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
pause
