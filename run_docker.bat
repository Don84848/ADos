@echo off
REM Helper script to run ADos builder inside Docker on Windows

set IMAGE_NAME=ados-builder:latest
set CURRENT_DIR=%~dp0

docker image inspect %IMAGE_NAME% >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [*] Building ADos Docker builder image...
    docker build -t %IMAGE_NAME% "%CURRENT_DIR%"
)

echo [*] Launching ADos builder container...
docker run --rm -it -v "%CURRENT_DIR%:/build" %IMAGE_NAME% %*
