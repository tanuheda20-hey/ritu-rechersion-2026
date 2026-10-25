@echo off
title RITU FRONTEND - DO NOT CLOSE THIS WINDOW
cd /d "%~dp0frontend"

echo.
echo [STEP 1 of 3] Checking Node.js...
node --version
if errorlevel 1 (
    echo.
    echo   XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    echo   ERROR: Node.js is not installed.
    echo.
    echo   Go to  https://nodejs.org/
    echo   Download the LTS version, run the installer.
    echo   Then double-click START-RITU.bat again.
    echo   XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    echo.
    pause
    exit /b
)
echo   Node OK.
echo.

if not exist "node_modules" (
    echo [STEP 2 of 3] Installing packages...
    echo   (first time takes 1-3 minutes, please wait)
    call npm install
    if errorlevel 1 (
        echo.
        echo   ERROR: npm install failed.
        echo   Check your internet connection and try again.
        echo.
        pause
        exit /b
    )
) else (
    echo [STEP 2 of 3] Packages already installed, skipping.
)
echo.

echo [STEP 3 of 3] Starting the app...
echo.
echo   ============================================
echo     FRONTEND IS RUNNING
echo     http://localhost:5173
echo.
echo     KEEP THIS WINDOW OPEN
echo   ============================================
echo.
call npm run dev
pause
