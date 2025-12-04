@echo off
REM Setup script for scheduling the Alta parking bot on Windows

echo ====================================
echo Alta Parking Bot - Windows Scheduler Setup
echo ====================================
echo.

REM Get the current directory
set SCRIPT_DIR=%~dp0
set SCRIPT_DIR=%SCRIPT_DIR:~0,-1%
echo Bot location: %SCRIPT_DIR%
echo.

REM Find Python path
for /f "tokens=*" %%i in ('where python') do set PYTHON_PATH=%%i
if "%PYTHON_PATH%"=="" (
    echo ERROR: Python not found in PATH
    echo Please install Python and make sure it's in your PATH
    pause
    exit /b 1
)
echo Python path: %PYTHON_PATH%
echo.

echo The bot should run every Sunday at 3pm MST (Mountain Standard Time).
echo.
echo Windows Task Scheduler will be configured to run the bot automatically.
echo.

echo Creating scheduled task...
echo.

REM Create the scheduled task
REM Runs every Sunday at 3:00 PM MST
REM Note: You'll need to adjust the time zone in Task Scheduler if you're not in MST

schtasks /Create /SC WEEKLY /D SUN /TN "Alta Parking Bot" /TR "\"%PYTHON_PATH%\" \"%SCRIPT_DIR%\alta_parking_bot.py\"" /ST 15:00 /F

if %ERRORLEVEL% EQU 0 (
    echo.
    echo SUCCESS! Scheduled task created.
    echo.
    echo The bot will run every Sunday at 3:00 PM.
    echo.
    echo To view/edit the task:
    echo 1. Open Task Scheduler (search in Start menu)
    echo 2. Look for "Alta Parking Bot" in the Task Scheduler Library
    echo 3. Right-click to Edit, Disable, or Delete
    echo.
    echo IMPORTANT: If you're not in MST timezone, you'll need to adjust the time:
    echo 1. Open Task Scheduler
    echo 2. Find "Alta Parking Bot"
    echo 3. Double-click to edit
    echo 4. Go to Triggers tab
    echo 5. Edit the trigger and adjust the time to match 3pm MST in your timezone
    echo.
) else (
    echo.
    echo ERROR: Failed to create scheduled task.
    echo You may need to run this script as Administrator.
    echo.
    echo To run as Administrator:
    echo 1. Right-click on setup_scheduler.bat
    echo 2. Select "Run as administrator"
    echo.
)

pause
