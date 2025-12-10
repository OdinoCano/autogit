@echo off
setlocal enabledelayedexpansion

:: Create log directory
set LOG_DIR=%USERPROFILE%\git_auto_pull_logs
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

:: Get the full path to the Python script
set SCRIPT_PATH=%~dp0git_auto_pull.py

:: Create scheduled tasks for each run time
for %%T in ("09:00" "14:00" "18:00") do (
    schtasks /create /tn "Git Auto Pull %%T" ^
            /tr "\"%PYTHON_HOME%\python.exe\" \"%SCRIPT_PATH%\"" ^
            /sc daily /st %%~T ^
            /rl highest ^
            /f
    
    if !ERRORLEVEL! EQU 0 (
        echo Created scheduled task for %%~T
    ) else (
        echo Failed to create task for %%~T
    )
)

echo.
echo Git auto-pull tasks have been set up.
echo Logs will be saved to: %LOG_DIR%
echo To run manually: python "%SCRIPT_PATH%" --force
pause
