@echo off
REM ---------------------------------------------------------------
REM  Local backup of .workbuddy\memory  (mirror + timestamped snapshots)
REM  Log: %USERPROFILE%\.autotest-memory-backup\Autotest-monster\backup.log
REM
REM  No console window: "pyw" is the windowless launcher of "py".
REM  Trigger it from Windows Task Scheduler, or just double-click it.
REM  ASCII only on purpose -- keep it that way (cmd.exe encoding).
REM ---------------------------------------------------------------

setlocal
set "LOG=%USERPROFILE%\.autotest-memory-backup\Autotest-monster\backup.log"

pyw -3.9 "%~dp0backup_memory.py" --log "%LOG%" %*
set "RC=%ERRORLEVEL%"

if not "%RC%"=="0" echo [WARN] backup_memory.py exit code = %RC%  (see %LOG%)
endlocal & exit /b %RC%
