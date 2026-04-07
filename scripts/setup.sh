#!/bin/bash
set -e

echo "=========================================="
echo "Slack Scroll - Setup Script"
echo "=========================================="

# Detect architecture
ARCH=$(uname -m)
echo "Detected architecture: $ARCH"

# Check if running on Raspberry Pi
IS_RPI=false
if [[ -f /proc/device-tree/model ]] && grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null; then
    IS_RPI=true
    echo "Running on Raspberry Pi"
fi

# Install uv if not present
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Verify uv installation
if ! command -v uv &> /dev/null; then
    echo "ERROR: uv installation failed"
    exit 1
fi

echo "uv version: $(uv --version)"

# Create virtual environment
echo "Creating virtual environment..."
uv venv

# Install dependencies
echo "Installing dependencies..."
uv pip install -e "."

# Create .env from template if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cat > .env << 'EOF'
# Slack Bot Token (xoxb-...)
SLACK_BOT_TOKEN=

# Slack Signing Secret
SLACK_SIGNING_SECRET=

# Socket Mode Token (xapp-...)
SOCKET_MODE_TOKEN=

# Slack Channel ID to monitor
CHANNEL_ID=C05R9591KFH

# Serial port for LED sign
SERIAL_PORT=/dev/ttyUSB0

# Enable verbose logging (set to 1 for debug output)
SLACK_SCROLL_VERBOSE=0
EOF
    echo "✓ Created .env - please edit with your credentials"
else
    echo "✓ .env already exists"
fi

# Install systemd services if on RPi
if [ "$IS_RPI" = true ]; then
    echo ""
    echo "Installing systemd services..."
    
    # Create backup directory
    sudo mkdir -p /opt/slack-scroll/backups
    sudo chown -R pi:pi /opt/slack-scroll
    
    # Copy service files
    sudo cp systemd/slack-scroll.service /etc/systemd/system/
    
    # Reload systemd
    sudo systemctl daemon-reload
    
    echo "✓ Systemd services installed"
    echo ""
    echo "To start the service:"
    echo "  sudo systemctl enable slack-scroll"
    echo "  sudo systemctl start slack-scroll"
else
    echo ""
    echo "Not on Raspberry Pi - skipping systemd installation"
    echo "To run locally:"
    echo "  source .venv/bin/activate"
    echo "  python -m slack_scroll --mode console"
fi

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env with your Slack credentials"
echo "2. Test with: python -m slack_scroll --mode console"
echo "3. Deploy with: sudo systemctl start slack-scroll"
echo ""
