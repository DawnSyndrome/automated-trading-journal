@echo off
:: Prompt user for input
set /p SERVICE_NAME="Enter your Docker Compose service name (default: automated-trading-journal): "
if "%SERVICE_NAME%"=="" set SERVICE_NAME=automated-trading-journal

set /p REPORTS_DIR="Enter your report directory (default: ./reports): "
if "%REPORTS_DIR%"=="" set REPORTS_DIR=./reports

set /p API_KEY="Enter your API_KEY: "
set /p API_SECRET="Enter your API_SECRET: "

:: Create .env file
(
    echo API_KEY="%API_KEY%"
    echo API_SECRET="%API_SECRET%"
    echo REPORTS_DIR="%REPORTS_DIR%"
) > .env
echo .env file created.

:: Create docker-compose.yml file
(
    echo version: '3.8'
    echo.
    echo services:
    echo   "%SERVICE_NAME%":
    echo     build:
    echo       context: .
    echo     container_name: "%SERVICE_NAME%"
    echo     volumes:
    echo       - ./logs:/app/logs
    echo       - "%REPORTS_DIR%:/app/reports"
    echo     env_file:
    echo       - .env
    echo     command: ^>
    echo       python app.py
    echo       --timeframe=${TIMEFRAME:-daily}
    echo       --config_type=${CONFIG_TYPE:-toml}
    echo     restart: unless-stopped
) > docker-compose.yml
echo docker-compose.yml file created.