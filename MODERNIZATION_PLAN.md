# Slack Scroll Modernization Plan

## Executive Summary

This document provides a comprehensive analysis and modernization roadmap for the Slack Scroll project. The project is a well-functioning Raspberry Pi-based LED sign display system that shows messages from a designated Slack channel on an LED matrix display at the Perth Artifactory.

**Key Pain Points:**
- 24 open security CVEs across dependencies (HIGH priority)
- Slow Docker image downloads on RPi Zero v1 (ARM v6)
- No automated deployment pipeline
- Outdated dependency management with pipenv
- Complex Docker setup for simple Python application

**Proposed Solutions:**
- Migrate to `uv` for fast dependency management and scripting
- Implement GitHub Actions deployment pipeline
- Pin specific ARM architecture for Docker images
- Security-first dependency updates
- Simplified local development with setup scripts

---

## 1. Current State Analysis

### 1.1 Project Architecture

**Core Components:**

1. **slack_scroll/** - Main application that connects to Slack and controls the LED sign
   - `src/slack_scroll.py` - Main entry point (173 lines)
   - `src/ledsign2.py` - LED sign driver library (313 lines)
   - Connects via Socket Mode to Slack API
   - Communicates with LED sign via serial (RS232 @ 2400 baud)

2. **web_interface/** - Simple Flask service for container restart
   - `src/web_interface.py` - REST endpoint at `/reset` (17 lines)
   - Uses Docker SDK to restart the slack-scroll container
   - Runs on port 8080

3. **twittinator_experiment/** - Legacy Twitter integration (deprecated)
   - MicroPython ESP32 code
   - Not currently in use

4. **experiments/** - Test scripts for LED sign

### 1.2 Technology Stack

| Component | Current | Issues |
|-----------|---------|--------|
| Python | 3.11 | Good, supported |
| Dependency Manager | Pipenv | Slow, less popular now |
| Container | Docker | Slow on RPi Zero, ARM v6 specific |
| Slack SDK | 3.21.3 | Outdated |
| Flask | Unknown | CVE-2026-27205 (Low) |
| Serial | pyserial 3.5 | Stable, no issues |

### 1.3 Current Deployment

```
Raspberry Pi Zero W v1 (ARM v6)
├── Docker Engine (root)
├── docker-compose.yml
├── .env file with secrets
└── Cron job: restart every 3 hours
```

**Deployment Commands:**
```bash
sudo docker compose up -d
sudo docker compose logs
```

**Docker Images:**
- `tazard/slack-scroll:latest` (linux/arm/v6)
- `tazard/slack-scroll-web-interface:latest` (linux/arm/v6)

### 1.4 Security Vulnerabilities (CRITICAL)

**24 Open CVEs identified:**

| CVE | Dependency | Severity | Fixed Version |
|-----|------------|----------|---------------|
| CVE-2024-34069 | werkzeug | HIGH | 3.0.3 |
| CVE-2024-21441 | urllib3 | HIGH | 2.6.3 |
| CVE-2025-66471 | urllib3 | HIGH | 2.6.0 |
| CVE-2025-66418 | urllib3 | HIGH | 2.6.0 |
| CVE-2025-59844 | sonarqube-scan-action | HIGH | 6.0.0 |
| CVE-2025-58178 | sonarqube-scan-action | HIGH | 5.3.1 |
| CVE-2024-3651 | idna | MEDIUM | 3.7 |
| CVE-2024-22195 | jinja2 | MEDIUM | 3.1.3 |
| CVE-2024-34064 | jinja2 | MEDIUM | 3.1.4 |
| CVE-2024-56201 | jinja2 | MEDIUM | 3.1.5 |
| CVE-2024-56326 | jinja2 | MEDIUM | 3.1.5 |
| CVE-2025-27516 | jinja2 | MEDIUM | 3.1.6 |
| CVE-2024-35195 | requests | MEDIUM | 2.32.0 |
| CVE-2024-47081 | requests | MEDIUM | 2.32.4 |
| CVE-2026-25645 | requests | MEDIUM | 2.33.0 |
| CVE-2024-37891 | urllib3 | MEDIUM | 2.2.2 |
| CVE-2025-50181 | urllib3 | MEDIUM | 2.5.0 |
| CVE-2024-49766 | werkzeug | MEDIUM | 3.0.6 |
| CVE-2024-49767 | werkzeug | MEDIUM | 3.0.6 |
| CVE-2025-66221 | werkzeug | MEDIUM | 3.1.4 |
| CVE-2026-21860 | werkzeug | MEDIUM | 3.1.5 |
| CVE-2026-27199 | werkzeug | MEDIUM | 3.1.6 |
| CVE-2024-39689 | certifi | LOW | 2024.7.4 |
| CVE-2026-27205 | flask | LOW | 3.1.3 |

**Impact Assessment:**
- HIGH severity: 6 CVEs (remote code execution, credential leaks, resource exhaustion)
- MEDIUM severity: 15 CVEs (sandbox breakouts, header injection, DoS)
- LOW severity: 3 CVEs (certificate issues, session handling)

---

## 2. Proposed Modernization Strategy

### 2.1 Phase 1: Security First (Immediate)

**Goal:** Fix all HIGH severity CVEs within 1 week

**Actions:**
1. Update all dependencies to latest secure versions
2. Pin specific versions in requirements
3. Update GitHub Actions (SonarSource action has 2 HIGH CVEs)
4. Test on staging RPi

**Updated Dependencies:**
```
slack-bolt>=1.22.0
slack-sdk>=3.35.0
pyserial>=3.5
Flask>=3.1.3
Werkzeug>=3.1.6
requests>=2.33.0
urllib3>=2.6.3
Jinja2>=3.1.6
certifi>=2024.7.4
idna>=3.7
docker>=7.0.0
```

### 2.2 Phase 2: Dependency Management Modernization

**Goal:** Replace pipenv with `uv` for speed and simplicity

**Why uv?**
- 10-100x faster than pip/pipenv
- Single binary, no Python dependencies
- Built-in virtual environment management
- Compatible with requirements.txt and pyproject.toml
- Industry standard (Astral, makers of ruff)

**Migration Plan:**

1. **Remove Pipenv artifacts:**
   - Delete `Pipfile`
   - Delete `Pipfile.lock`

2. **Create `pyproject.toml`:**
   ```toml
   [project]
   name = "slack-scroll"
   version = "2.0.0"
   description = "Display Slack messages on LED matrix sign"
   requires-python = ">=3.11"
   dependencies = [
       "slack-bolt>=1.22.0",
       "slack-sdk>=3.35.0",
       "pyserial>=3.5",
   ]
   
   [project.optional-dependencies]
   web = ["Flask>=3.1.3", "docker>=7.0.0"]
   dev = ["pytest", "black", "ruff"]
   ```

3. **Create `setup.sh` script:**
   ```bash
   #!/bin/bash
   # Setup script for RPi Zero
   
   # Install uv
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Create virtual environment
   uv venv
   
   # Install dependencies
   uv pip install -e ".[web]"
   
   # Create .env from template
   if [ ! -f .env ]; then
       cp .env.example .env
       echo "Created .env - please edit with your credentials"
   fi
   ```

### 2.3 Phase 3: Deployment Pipeline

**Goal:** GitHub-driven automated deployment to Raspberry Pi

**Current Flow:**
```
Local Change → Push to master → Build Docker image (GitHub Actions) 
→ Pull on RPi → Restart container
```

**Problems:**
- Docker image is 100MB+ even for simple Python app
- ARM v6 builds are slow
- No automated deployment to RPi
- Manual pull and restart required

**Proposed Flow:**
```
Local Change → PR → Merge to main → GitHub Actions
→ Deploy via SSH to RPi → Restart service
```

**Implementation:**

1. **GitHub Actions Workflow (`deploy.yml`):**
   ```yaml
   name: Deploy to Raspberry Pi
   
   on:
     push:
       branches: [main]
   
   jobs:
     deploy:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         
         - name: Deploy to RPi via SSH
           uses: appleboy/ssh-action@v1
           with:
             host: ${{ secrets.RPI_HOST }}
             username: ${{ secrets.RPI_USER }}
             key: ${{ secrets.RPI_SSH_KEY }}
             script: |
               cd ~/slackscroll
               git pull origin main
               ./scripts/update.sh
   ```

2. **RPi Update Script (`scripts/update.sh`):**
   ```bash
   #!/bin/bash
   set -e
   
   echo "Updating Slack Scroll..."
   
   # Pull latest code
   git pull origin main
   
   # Install/update dependencies with uv
   uv pip install -e ".[web]"
   
   # Restart services via systemd
   sudo systemctl restart slack-scroll
   sudo systemctl restart slack-scroll-web
   
   echo "Update complete!"
   ```

3. **Systemd Services:**
   Replace Docker with systemd services for better RPi Zero performance.

   `/etc/systemd/system/slack-scroll.service`:
   ```ini
   [Unit]
   Description=Slack Scroll LED Display
   After=network.target
   
   [Service]
   Type=simple
   User=pi
   WorkingDirectory=/home/pi/slackscroll
   EnvironmentFile=/home/pi/slackscroll/.env
   ExecStart=/home/pi/slackscroll/.venv/bin/python -m slack_scroll
   Restart=always
   RestartSec=10
   
   [Install]
   WantedBy=multi-user.target
   ```

### 2.4 Phase 4: Optional Docker Improvements

**If keeping Docker is preferred:**

1. **Optimize Dockerfile:**
   - Use multi-stage builds to reduce image size
   - Pin to specific Debian version (bookworm-slim)
   - Use BuildKit for faster builds

2. **Docker Compose improvements:**
   ```yaml
   services:
     slack-scroll:
       build:
         context: .
         dockerfile: Dockerfile
         platforms:
           - linux/arm/v6
       image: tazard/slack-scroll:${VERSION:-latest}
       restart: unless-stopped
       init: true
       env_file: .env
       devices:
         - "/dev/ttyUSB0:/dev/ttyUSB0"
       logging:
         driver: json-file
         options:
           max-size: "10m"
           max-file: "3"
   ```

3. **Image registry optimization:**
   - Use GitHub Container Registry (ghcr.io) instead of Docker Hub
   - Enable layer caching
   - Build multi-arch images (ARM v6, v7, v8, AMD64)

### 2.5 Phase 5: Development Experience

**Local Development Setup:**

1. **`scripts/dev.sh`** - Start development environment:
   ```bash
   #!/bin/bash
   # Mock LED sign for local testing
   export MOCK_SIGN=true
   uv run python -m slack_scroll
   ```

2. **`scripts/test.sh`** - Run tests:
   ```bash
   #!/bin/bash
   uv run pytest tests/ -v
   ```

3. **`scripts/lint.sh`** - Code quality:
   ```bash
   #!/bin/bash
   uv run ruff check .
   uv run black --check .
   ```

4. **Mock Serial Device:**
   Create a mock `ledsign2.py` for testing without hardware:
   ```python
   # Mock implementation for development
   class LEDSign:
       def __init__(self, port):
           print(f"[MOCK] LEDSign initialized on {port}")
       def send_to_sign(self, msg):
           print(f"[MOCK] Would send: {msg}")
       # ... other methods
   ```

---

## 3. Implementation Roadmap

### Week 1: Security & Dependency Updates
- [ ] Update all dependencies to fix CVEs
- [ ] Test on staging RPi
- [ ] Update GitHub Actions workflows
- [ ] Security scan verification

### Week 2: uv Migration
- [ ] Remove pipenv
- [ ] Create pyproject.toml
- [ ] Write setup.sh script
- [ ] Test installation on fresh RPi OS

### Week 3: Deployment Pipeline
- [ ] Create systemd service files
- [ ] Set up SSH deployment keys
- [ ] Write update.sh script
- [ ] Configure GitHub Actions deploy workflow
- [ ] Test end-to-end deployment

### Week 4: Documentation & Polish
- [ ] Update README with new installation instructions
- [ ] Document troubleshooting
- [ ] Add development guide
- [ ] Create architecture diagram

---

## 4. File Structure Changes

### Current Structure:
```
slack-scroll/
├── slack_scroll/
│   ├── src/
│   │   ├── slack_scroll.py
│   │   ├── ledsign2.py
│   │   └── Dockerfile (redundant)
│   ├── Dockerfile
│   ├── Pipfile
│   ├── Pipfile.lock
│   ├── requirements.txt
│   └── manifest.json
├── web_interface/
│   ├── src/
│   │   └── web_interface.py
│   ├── Dockerfile
│   ├── Pipfile
│   ├── Pipfile.lock
│   └── requirements.txt
├── .github/workflows/
│   ├── docker_image_build.yml
│   └── check.yml
└── twittinator_experiment/
    └── ...
```

### Proposed Structure:
```
slack-scroll/
├── pyproject.toml              # Unified dependency management
├── uv.lock                     # uv lock file (replaces Pipfile.lock)
├── .env.example                # Environment template
├── README.md                   # Updated documentation
├── src/
│   └── slack_scroll/
│       ├── __init__.py
│       ├── main.py             # Entry point
│       ├── slack_client.py     # Slack integration
│       ├── sign_controller.py  # LED sign control
│       └── ledsign2.py         # LED driver
├── web_interface/
│   ├── __init__.py
│   └── app.py                  # Flask app
├── scripts/
│   ├── setup.sh                # Initial setup
│   ├── update.sh               # Deployment script
│   ├── dev.sh                  # Local development
│   ├── test.sh                 # Run tests
│   └── lint.sh                 # Code quality
├── systemd/
│   ├── slack-scroll.service
│   └── slack-scroll-web.service
├── tests/
│   ├── test_slack_client.py
│   └── test_sign_controller.py
├── mocks/
│   └── ledsign2.py             # Mock for testing
└── .github/workflows/
    ├── ci.yml                  # Lint, test, security scan
    └── deploy.yml              # Deploy to RPi
```

---

## 5. Risk Assessment

### High Risk:
1. **Breaking Changes in Dependencies**
   - Mitigation: Test thoroughly on staging RPi
   - Keep old Docker setup as fallback

2. **Systemd Service Failures**
   - Mitigation: Keep Docker as backup option
   - Document rollback procedure

### Medium Risk:
1. **SSH Key Management**
   - Mitigation: Use GitHub secrets, rotate keys regularly
   - Limit RPi user permissions

2. **uv Compatibility**
   - Mitigation: Test on ARM v6 architecture
   - Fall back to pip if needed

### Low Risk:
1. **Development Workflow Changes**
   - Mitigation: Good documentation
   - Team training

---

## 6. Benefits Summary

| Metric | Current | After Modernization |
|--------|---------|---------------------|
| Security CVEs | 24 open | 0 open |
| Deployment time | 5-10 min (Docker pull) | <30 sec (git pull + restart) |
| Disk usage | ~500MB (Docker images) | ~100MB (venv) |
| Memory usage | Higher (Docker overhead) | Lower (native systemd) |
| Update process | Manual | Automated via GitHub |
| Developer setup | 15 min (Docker) | 2 min (uv + setup.sh) |
| CI/CD time | 10 min (ARM v6 build) | 2 min (lint + deploy) |

---

## 7. Next Steps

1. **Immediate (This Week):**
   - [ ] Review and approve this plan
   - [ ] Create feature branch
   - [ ] Update dependencies to fix CVEs

2. **Short Term (Next 2 Weeks):**
   - [ ] Migrate to uv
   - [ ] Create systemd services
   - [ ] Set up deployment pipeline

3. **Medium Term (Next Month):**
   - [ ] Remove Docker dependencies
   - [ ] Update documentation
   - [ ] Archive old experiment code

---

## 8. Questions & Decisions Needed

1. **Docker vs Systemd:** Do we want to keep Docker as an option, or fully migrate to systemd?
   - Recommendation: Migrate to systemd for RPi Zero performance

2. **GitHub Container Registry:** Should we migrate from Docker Hub to GHCR?
   - Recommendation: Yes, if keeping Docker option

3. **Staging Environment:** Do we have a spare RPi for testing?
   - Recommendation: Essential for safe deployment

4. **Backup Strategy:** How do we handle rollback if deployment fails?
   - Recommendation: Keep systemd service disabled until verified working

---

**Document Version:** 1.0  
**Last Updated:** 2025-04-07  
**Author:** Sisyphus (OpenCode AI Assistant)  
**Status:** Draft - Pending Review
