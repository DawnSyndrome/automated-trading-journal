#!/bin/bash

# Prompt user for input
read -p "Enter your Docker Compose service name (default: automated-trading-journal): " SERVICE_NAME
SERVICE_NAME=${SERVICE_NAME:-automated-trading-journal}

read -p "Enter your report directory (default: ./reports): " REPORTS_DIR
REPORTS_DIR=${REPORTS_DIR:-./reports}

read -p "Enter your API_KEY: " API_KEY
read -p "Enter your API_SECRET: " API_SECRET

# Write .env file
cat <<EOL > .env
API_KEY="$API_KEY"
API_SECRET="$API_SECRET"
REPORTS_DIR="$REPORTS_DIR"
EOL

echo ".env file created."

# Create docker-compose.yml file
cat <<EOL > docker-compose.yml
version: '3.8'

services:
  automated-trading-journal:
    build:
      context: .
    container_name: $SERVICE_NAME
    volumes:
      - ./logs:/app/logs
      - "$REPORTS_DIR:/app/reports"
    env_file:
      - .env
    command: >
      python app.py
      --timeframe=\${TIMEFRAME:-daily}
      --config_type=\${CONFIG_TYPE:-toml}
    restart: unless-stopped
EOL

echo "docker-compose.yml file created."

# Generate cron job file
cat <<EOL > schedule_cron_jobs_linux.sh
#!/bin/bash

# Example cron jobs for scheduling the container

# Weekdays at 11 PM with daily timeframe
echo "0 23 * * 1-5 docker-compose run -e TIMEFRAME=daily -e START_DATE=\$(date +\%Y-\%m-\%d) $SERVICE_NAME" | crontab -

# Sundays at 11 PM with weekly timeframe
echo "0 23 * * 0 docker-compose run -e TIMEFRAME=weekly -e START_DATE=\$(date -d 'last monday' +\%Y-\%m-\%d) $SERVICE_NAME" | crontab -

# Last day of the month at 11 PM with monthly timeframe
echo "0 23 28-31 * * [ \$(date -d tomorrow +\%d) -eq 1 ] && docker-compose run -e TIMEFRAME=monthly -e START_DATE=\$(date +\%Y-\%m) $SERVICE_NAME" | crontab -

echo "Crontab entries created successfully!"
EOL

chmod +x schedule_cron_jobs_linux.sh
echo "Cron job script generated: schedule_cron_jobs_linux.sh"
