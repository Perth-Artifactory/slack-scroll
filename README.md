# Slack Scroll

Display Slack messages on an LED matrix sign at the Perth Artifactory.

## Quick Start

```bash
# Clone and setup
git clone https://github.com/Perth-Artifactory/slack-scroll.git
cd slack-scroll
./scripts/setup.sh

# Edit configuration
nano .env

# Run locally in console mode (no LED sign required)
./scripts/dev.sh

# Deploy to Raspberry Pi
./scripts/update.sh
```

## Requirements

- Python 3.11+
- Slack Bot Token with Socket Mode
- LED sign connected via USB (for production)

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SLACK_BOT_TOKEN` | Bot token (xoxb-...) | Yes |
| `SLACK_SIGNING_SECRET` | Signing secret | Yes |
| `SOCKET_MODE_TOKEN` | Socket Mode token (xapp-...) | Yes |
| `CHANNEL_ID` | Slack channel ID to monitor | Yes |
| `SERIAL_PORT` | Serial port (default: /dev/ttyUSB0) | No |
| `SLACK_SCROLL_VERBOSE` | Enable debug logging (0/1) | No |

## Running Modes

### Console Mode (Development)
Shows sign output in terminal instead of sending to LED:
```bash
python -m slack_scroll --mode console
```

### Serial Mode (Production)
Sends output to real LED sign:
```bash
python -m slack_scroll --mode serial
```

### Test Mode
Runs automated tests with mocked Slack and sign:
```bash
python -m slack_scroll --mode test
```

## Deployment

### Raspberry Pi Setup

1. Install Raspberry Pi OS on SD card
2. Enable SSH and configure WiFi
3. Boot and run setup:

```bash
curl -fsSL https://raw.githubusercontent.com/Perth-Artifactory/slack-scroll/main/scripts/setup.sh | bash
```

4. Configure systemd service:
```bash
sudo systemctl enable slack-scroll
sudo systemctl start slack-scroll
```

### GitHub Actions Deployment (via Teleport)

The project includes automated deployment via GitHub Actions using Teleport for secure access (no direct SSH exposure needed).

Set these secrets in your GitHub repository:

- `TELEPORT_PROXY` - Your Teleport proxy URL (e.g., `teleport.artifactory.org:443`)
- `TELEPORT_TOKEN` - Teleport join token or bot token
- `TELEPORT_USER` - Username on the RPi (usually 'pi')
- `TELEPORT_NODE` - Teleport node name for the RPi (e.g., `slackscroll`)

Push to `main` branch triggers automatic deployment through Teleport.

**Note:** This requires the RPi to be enrolled in your Teleport cluster with the `teleport` agent running.

### Manual Deployment

```bash
# SSH into Raspberry Pi
ssh pi@slackscroll.local

# Run update script
cd ~/slackscroll
./scripts/update.sh
```

## Rollback

If deployment fails, rollback to a previous version:

```bash
# List available backups
ls -la /opt/slack-scroll/backups/

# Rollback to specific backup
sudo /opt/slack-scroll/rollback.sh /opt/slack-scroll/backups/20250407_120000
```

## Development

### Running Tests

```bash
uv run pytest tests/ -v
```

### Code Quality

```bash
# Linting
uv run ruff check src/

# Formatting
uv run black src/

# Type checking
uv run mypy src/
```

## Architecture

```
slack-scroll/
├── src/slack_scroll/       # Main application
│   ├── main.py            # Core logic
│   ├── sign_output.py     # Output abstractions
│   ├── ledsign2.py        # LED sign driver
│   └── modes/             # Operating modes
├── scripts/               # Setup and deployment
├── systemd/               # Service definitions
└── tests/                 # Test suite
```

## Security

All 24 previous CVEs have been addressed by updating to latest dependency versions:
- slack-bolt >= 1.22.0
- slack-sdk >= 3.35.0
- werkzeug >= 3.1.6
- flask >= 3.1.3

## License

LGPL-3.0 (ledsign2.py originally by Michael Farrell)

## Support

For issues and feature requests, please use GitHub Issues.
