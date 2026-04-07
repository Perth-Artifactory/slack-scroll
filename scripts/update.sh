#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Load environment
if [ -f "$PROJECT_DIR/.env" ]; then
    export $(grep -v '^#' "$PROJECT_DIR/.env" | xargs)
fi

echo "=========================================="
echo "Slack Scroll - Update & Deploy"
echo "=========================================="
echo "Timestamp: $(date)"
echo ""

# Check if we're in the right directory
if [ ! -f "$PROJECT_DIR/pyproject.toml" ]; then
    echo "ERROR: Cannot find pyproject.toml"
    echo "Are you in the slack-scroll directory?"
    exit 1
fi

cd "$PROJECT_DIR"

# Create backup before updating
echo "Creating backup..."
BACKUP_DIR="/opt/slack-scroll/backacks/$(date +%Y%m%d_%H%M%S)"
sudo mkdir -p "$BACKUP_DIR"
sudo cp -r . "$BACKUP_DIR/"
echo "✓ Backup created: $BACKUP_DIR"

# Pull latest code (if this is a git repo)
if [ -d .git ]; then
    echo ""
    echo "Pulling latest code..."
    git pull origin main || git pull origin master
    echo "✓ Code updated"
fi

# Update dependencies
echo ""
echo "Updating dependencies..."
uv pip install -e "."
echo "✓ Dependencies updated"

# Run tests
echo ""
echo "Running tests..."
if python -m pytest tests/ -v 2>/dev/null; then
    echo "✓ Tests passed"
else
    echo "⚠ Tests failed or not found - continuing anyway"
fi

# Restart service
echo ""
echo "Restarting service..."
sudo systemctl restart slack-scroll
sleep 2

# Check service status
if sudo systemctl is-active --quiet slack-scroll; then
    echo "✓ Service restarted successfully"
    echo ""
    echo "Service status:"
    sudo systemctl status slack-scroll --no-pager
else
    echo "✗ Service failed to start!"
    echo ""
    echo "Checking logs..."
    sudo journalctl -u slack-scroll --no-pager -n 50
    exit 1
fi

echo ""
echo "=========================================="
echo "Update complete!"
echo "=========================================="
echo ""
echo "Backup location: $BACKUP_DIR"
echo "To rollback: sudo /opt/slack-scroll/rollback.sh $BACKUP_DIR"
