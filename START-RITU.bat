@echo off
title RITU - Starting
cd /d "%~dp0"

echo.
echo   ============================================
echo      R I T U   -   recHERsion 2026
echo      Team THEPLAYERS - PS1 Women's Healthcare
echo   ============================================
echo.
echo   Starting backend and frontend...
echo   Two black windows will open. DO NOT CLOSE THEM.
echo.
echo   First time: takes 2-4 minutes to download packages.
echo   After that: takes 10 seconds.
echo.

start "RITU BACKEND - DO NOT CLOSE" cmd /k "%~dp0START-BACKEND.bat"
timeout /t 5 /nobreak >nul
start "RITU FRONTEND - DO NOT CLOSE" cmd /k "%~dp0START-FRONTEND.bat"

timeout /t 25 /nobreak >nul

echo.
echo   Opening your browser...
start "" http://localhost:5173
echo.
echo   ============================================
echo     If the page shows "backend connected"
echo     in green at the top right - YOU ARE DONE!
echo   ============================================
echo.
echo   If you see an error instead, take a screenshot
echo   of the black windows and ask for help.
echo.
pause
