#!/bin/bash

if [ $# -ne 1 ]; then
    echo "Usage: $0 <backup_directory>"
    echo ""
    echo "Available backups:"
    ls -1dt /opt/slack-scroll/backups/*/ 2>/dev/null | head -10 || echo "  No backups found"
    exit 1
fi

BACKUP_DIR="$1"
PROJECT_DIR="/home/pi/slackscroll"

echo "=========================================="
echo "Slack Scroll - Rollback"
echo "=========================================="
echo "Rolling back to: $BACKUP_DIR"
echo ""

if [ ! -d "$BACKUP_DIR" ]; then
    echo "ERROR: Backup directory not found: $BACKUP_DIR"
    exit 1
fi

# Stop service
echo "Stopping service..."
sudo systemctl stop slack-scroll

# Create backup of current state (just in case)
CURRENT_BACKUP="/opt/slack-scroll/backups/pre-rollback-$(date +%Y%m%d_%H%M%S)"
echo "Creating safety backup of current state: $CURRENT_BACKUP"
sudo mkdir -p "$CURRENT_BACKUP"
sudo cp -r "$PROJECT_DIR" "$CURRENT_BACKUP/"

# Restore from backup
echo "Restoring from backup..."
sudo rm -rf "$PROJECT_DIR"
sudo cp -r "$BACKUP_DIR" "$PROJECT_DIR"
sudo chown -R pi:pi "$PROJECT_DIR"
echo "✓ Files restored"

# Reinstall dependencies
echo ""
echo "Reinstalling dependencies..."
cd "$PROJECT_DIR"
uv pip install -e "."
echo "✓ Dependencies installed"

# Start service
echo ""
echo "Starting service..."
sudo systemctl start slack-scroll
sleep 2

if sudo systemctl is-active --quiet slack-scroll; then
    echo "✓ Service started successfully"
    echo ""
    sudo systemctl status slack-scroll --no-pager
else
    echo "✗ Service failed to start"
    echo ""
    sudo journalctl -u slack-scroll --no-pager -n 50
    exit 1
fi

echo ""
echo "=========================================="
echo "Rollback complete!"
echo "=========================================="
