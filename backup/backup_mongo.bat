@echo off
chcp 65001 > nul

REM ====== CONFIG ======
set BACKUP_DIR=D:\chatbot_backup
set MONGODUMP="C:\Program Files\MongoDB\Server\7.0\bin\mongodump.exe"

set DB_NAME=chatbot_db
set DB_USER=chatbot_app
set DB_PASS=pass
REM ====================

REM ====== DATETIME SAFE ======
for /f %%i in ('powershell -command "Get-Date -Format yyyy-MM-dd_HH-mm-ss"') do set DATETIME=%%i

set TARGET=%BACKUP_DIR%\mongo_%DATETIME%
mkdir "%TARGET%"

echo Backup to: %TARGET%

%MONGODUMP% ^
  --host localhost ^
  --port 27017 ^
  --username %DB_USER% ^
  --password %DB_PASS% ^
  --authenticationDatabase %DB_NAME% ^
  --db %DB_NAME% ^
  --out "%TARGET%"

if %ERRORLEVEL% EQU 0 (
    echo Backup SUCCESS ?
) else (
    echo Backup FAILED ?
)

pause
