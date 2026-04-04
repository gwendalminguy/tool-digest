#!/bin/bash

set -e

# Checking Requirements
if ! command -v python3 >/dev/null 2>&1; then
  echo "Failure: python3 required but not found."
  exit 1
fi

if ! command -v crontab >/dev/null 2>&1; then
  echo "Failure: crontab required but not found."
  exit 1
fi

# Setting Paths
ROOT_DIRECTORY="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAIN=$(realpath "$ROOT_DIRECTORY/main.py")
ENV_FILE="$ROOT_DIRECTORY/.env"
PYTHON=$(command -v python3)
INTERVAL=7

read -p "OPML URL: " OPML_URL
read -p "Gemini API Key: " GEMINI_API_KEY

# Creating .env File
cat > "$ENV_FILE" <<EOF
OPML_URL=$OPML_URL
GEMINI_API_KEY=$GEMINI_API_KEY
INTERVAL=$INTERVAL
EOF

mkdir -p "$ROOT_DIRECTORY/news"

# Setting Cron Automations (Every 6 Hours on Sunday)
(crontab -l 2>/dev/null | grep -v "$MAIN"; \
echo "0 */6 * * 0 $PYTHON $MAIN") | crontab -

echo "Success: installation complete."
