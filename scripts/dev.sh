#!/bin/bash

# Run Slack Scroll in console mode for local development

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

# Load environment
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

echo "Starting Slack Scroll in console mode..."
echo ""
python -m slack_scroll --mode console "$@"
