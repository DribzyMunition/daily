@echo off
REM ============================================================
REM  setup_scheduler.bat — One-time Windows Task Scheduler setup
REM  Run this ONCE (right-click > Run as Administrator).
REM
REM  Change the /st value below to set the daily run time.
REM  Format: HH:MM  (24-hour clock)
REM ============================================================

set RUN_TIME=07:30
set TASK_NAME=DailyFeedBot
set SCRIPT_PATH=%~dp0run_feed.bat

echo Creating scheduled task "%TASK_NAME%"...
echo Run time: %RUN_TIME% daily
echo Script:   %SCRIPT_PATH%
echo.

schtasks /create ^
  /tn "%TASK_NAME%" ^
  /tr "\"%SCRIPT_PATH%\"" ^
  /sc DAILY ^
  /st %RUN_TIME% ^
  /rl HIGHEST ^
  /f

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Success! The task will run every day at %RUN_TIME%.
    echo.
    echo To verify:  open Task Scheduler and look for "%TASK_NAME%"
    echo To remove:  schtasks /delete /tn "%TASK_NAME%" /f
    echo To run now: schtasks /run /tn "%TASK_NAME%"
) else (
    echo.
    echo Something went wrong. Try running this file as Administrator.
)

echo.
pause
