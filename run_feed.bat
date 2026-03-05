@echo off
REM ============================================================
REM  run_feed.bat — Daily Feed Runner
REM  Called by Windows Task Scheduler each day.
REM  Logs output to logs\feed.log (last 1000 lines kept).
REM ============================================================

cd /d "%~dp0"

REM Create logs folder if it doesn't exist
if not exist logs mkdir logs

REM Run the feed script and append output to the log file
echo. >> logs\feed.log
echo ======================================================== >> logs\feed.log
echo Run started: %DATE% %TIME% >> logs\feed.log
echo ======================================================== >> logs\feed.log

python fetch_feed.py >> logs\feed.log 2>&1

echo Run finished: %DATE% %TIME% >> logs\feed.log
