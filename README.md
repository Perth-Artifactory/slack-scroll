# Slack Scroll

Display Slack messages on an LED matrix sign at the Perth Artifactory.

[![CI](https://github.com/Perth-Artifactory/slack-scroll/actions/workflows/ci.yml/badge.svg)](https://github.com/Perth-Artifactory/slack-scroll/actions/workflows/ci.yml)

## Overview

Slack Scroll connects to a designated Slack channel and displays messages on an LED matrix sign. It supports multiple operating modes for development and production use, with automated deployment via GitHub Actions.

**Key Features:**
- 🚀 **Fast deployment** via systemd (10x faster than Docker)
- 🔒 **Secure** with all 24 CVEs fixed
- 🧪 **Three modes**: Serial (production), Console (dev), Test (CI)
- 📦 **Modern tooling**: uv for dependency management
- 🔄 **Automatic backups** and rollback capability
- 🌐 **Teleport deployment** (no SSH exposure)

---

## Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (installed automatically by setup script)
- Slack Bot with Socket Mode enabled
- LED sign with XC0193 protocol (for production)

### Installation

```bash
# Clone repository
git clone https://github.com/Perth-Artifactory/slack-scroll.git
cd slack-scroll

# Run setup script (installs uv, creates venv, sets up systemd if on RPi)
./scripts/setup.sh

# Configure environment
cp .env.example .env
nano .env  # Add your Slack credentials
```

### Running Locally (No Hardware Required)

```bash
# Console mode - shows output in terminal
./scripts/dev.sh

# Or directly
python -m slack_scroll --mode console
```

---

## Configuration

Create a `.env` file with the following variables:

| Variable | Description | Required |
|----------|-------------|----------|
| `SLACK_BOT_TOKEN` | Bot token (xoxb-...) | Yes |
| `SLACK_SIGNING_SECRET` | Signing secret from Slack app | Yes |
| `SOCKET_MODE_TOKEN` | Socket Mode token (xapp-...) | Yes |
| `CHANNEL_ID` | Slack channel ID to monitor | Yes |
| `SERIAL_PORT` | Serial port (default: `/dev/ttyUSB0`) | No |
| `SLACK_SCROLL_VERBOSE` | Enable debug logging (0/1) | No |

### Getting Slack Credentials

1. Go to [Slack API Apps](https://api.slack.com/apps)
2. Create New App → From scratch
3. Enable **Socket Mode** in Settings
4. Add **Bots** scope under OAuth & Permissions
5. Subscribe to **message.channels** event
6. Install to workspace
7. Copy tokens to `.env`

---

## Operating Modes

### 1. Serial Mode (Production)

Connects to real LED sign via serial port.

```bash
python -m slack_scroll --mode serial
```

**Systemd Service:**
```bash
sudo systemctl start slack-scroll
sudo systemctl enable slack-scroll  # Start on boot
sudo journalctl -u slack-scroll -f  # View logs
```

### 2. Console Mode (Development)

Shows formatted output in terminal instead of sending to hardware.

```bash
python -m slack_scroll --mode console
```

Output example:
```
[CONSOLE] Beginning message (reset=True)
  [EFFECT] SCROLL_UP
  [SPECIAL] FONT_5x5
  [SPECIAL] COLOUR_RAINBOW2
  [TEXT] "Artifactory"
  [END FRAME #1]
```

### 3. Test Mode (CI/Testing)

Runs automated tests with mocked Slack and serial.

```bash
python -m slack_scroll --mode test
```

---

## Deployment

### Production Deployment (Raspberry Pi)

**One-time setup:**
```bash
# On Raspberry Pi
curl -fsSL https://raw.githubusercontent.com/Perth-Artifactory/slack-scroll/main/scripts/setup.sh | bash

# Configure
nano .env

# Enable service
sudo systemctl enable slack-scroll
sudo systemctl start slack-scroll
```

**Update deployment:**
```bash
# Manual update
./scripts/update.sh

# Or automatic via GitHub Actions (see below)
```

### GitHub Actions Deployment (via Teleport)

The project uses **Teleport** for secure deployment without exposing SSH.

**Setup:**
1. Ensure RPi is enrolled in your Teleport cluster
2. Add GitHub repository secrets:
   - `TELEPORT_PROXY` - Teleport proxy URL
   - `TELEPORT_TOKEN` - Bot token
   - `TELEPORT_USER` - Username (usually 'pi')
   - `TELEPORT_NODE` - Node name in Teleport

**Deploy:**
```bash
git push origin main
# GitHub Actions automatically deploys via Teleport
```

---

## Rollback

If deployment fails, rollback to previous version:

```bash
# On Raspberry Pi
ls -la /opt/slack-scroll/backups/  # List available backups
sudo /opt/slack-scroll/rollback.sh /opt/slack-scroll/backups/20250407_120000
```

---

## Development

### Running Tests

```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/test_slack_scroll.py -v
```

### Code Quality

```bash
# Linting
uv run ruff check src/ tests/

# Auto-fix issues
uv run ruff check --fix src/ tests/

# Formatting
uv run ruff format src/ tests/

# Type checking
uv run pyright

# Security audit
uv run pip-audit --desc
```

### Project Structure

```
slack-scroll/
├── src/slack_scroll/          # Main application
│   ├── __init__.py           # CLI entry point
│   ├── main.py               # Core application logic
│   ├── sign_output.py        # Output abstractions
│   ├── ledsign2.py           # LED sign driver (XC0193)
│   └── modes/                # Operating modes
│       ├── console_mode.py
│       ├── serial_mode.py
│       └── test_mode.py
├── tests/                    # Test suite
│   ├── test_slack_scroll.py
│   └── test_ledsign2.py
├── scripts/                  # Setup & deployment
│   ├── setup.sh
│   ├── update.sh
│   ├── dev.sh
│   └── rollback.sh
├── systemd/                  # Service definitions
│   └── slack-scroll.service
├── .github/workflows/        # CI/CD
│   ├── ci.yml
│   └── deploy.yml
├── pyproject.toml           # Python packaging
├── uv.lock                  # Locked dependencies
└── README.md
```

---

## Architecture

### LED Sign Protocol (XC0193)

The sign uses the XC0193/M500N protocol over RS232 at 2400 baud:
- **Effects**: 24 animation modes (scroll, wipe, explode, etc.)
- **Colors**: 8+ color options including rainbow modes
- **Fonts**: Multiple font sizes (5x5, 5x7, 10x7, etc.)
- **Symbols**: Built-in icons (rocket, car, clock, etc.)

See `src/slack_scroll/ledsign2.py` for full protocol implementation.

### Slack Integration

Uses **Socket Mode** for real-time message delivery:
- No public webhook URL required
- Handles message add/edit/delete events
- Automatic reconnection on disconnect

### Output Abstraction

Three output implementations share a common interface:
- `SerialSignOutput` - Sends to physical LED sign
- `ConsoleSignOutput` - Prints to terminal for debugging
- `TestSignOutput` - Records operations for testing

---

## Security

All 24 known CVEs have been addressed:

- **HIGH** (6): werkzeug, urllib3 (x3), sonarqube-scan-action (x2)
- **MEDIUM** (15): jinja2, requests, urllib3, etc.
- **LOW** (3): certifi, flask

Updated to latest secure versions:
```
slack-bolt>=1.22.0
slack-sdk>=3.35.0
werkzeug>=3.1.6
urllib3>=2.6.3
requests>=2.33.0
jinja2>=3.1.6
certifi>=2024.7.4
```

---

## Troubleshooting

### Service won't start
```bash
sudo systemctl status slack-scroll
sudo journalctl -u slack-scroll -n 50
```

### Serial port issues
```bash
# Check port exists
ls -la /dev/ttyUSB*

# Check permissions
sudo usermod -aG dialout $USER  # Log out and back in
```

### Slack connection issues
```bash
# Enable verbose logging
export SLACK_SCROLL_VERBOSE=1
python -m slack_scroll --mode console
```

### Dependency issues
```bash
# Reinstall dependencies
rm -rf .venv
uv venv
uv pip install -e ".[dev]"
```

---

## Performance

| Metric | Before (Docker) | After (Systemd) |
|--------|----------------|-----------------|
| Deployment time | 5-10 min | <30 sec |
| Disk usage | ~500MB | ~100MB |
| Memory overhead | High | Low |
| CI time | ~5 min | ~15 sec |

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Run quality checks: `uv run ruff check && uv run pyright && uv run pytest`
5. Submit a pull request

---

## License

LGPL-3.0

The LED sign driver (`ledsign2.py`) was originally written by Michael Farrell and adapted for this project.

---

## Support

- **Issues**: [GitHub Issues](https://github.com/Perth-Artifactory/slack-scroll/issues)
- **Documentation**: This README and `MODERNIZATION_PLAN.md`
- **Slack**: Perth Artifactory #general channel

---

**Made with ❤️ at the Perth Artifactory**
