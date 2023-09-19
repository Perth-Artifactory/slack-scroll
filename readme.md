# Slack Scroll

A python application to take messages from Slack channel #slackscroll and show them on an an LED matrix display.

## Usage
description of how to update/change messages

## Installation
How to install and run slack scroll.

1. Take a Rasperry Pi Zero W and install Raspberry Pi OS: https://www.raspberrypi.com/software/
2. Follow docker install guide: https://docs.docker.com/engine/install/raspberry-pi-os/
3. Create `.env` and `docker-compose.yml` files from template below. Put them in `~/slackscroll`.
4. Install and run slack scroll with docker compose: `sudo docker compose up -d`
5. Check logs with `sudo docker compose logs`

`.env` template:

```
SLACK_BOT_TOKEN=FILLME
SLACK_SIGNING_SECRET=FILLME
SOCKET_MODE_TOKEN=FILLME
CHANNEL_ID=C05R9591KFH
SERIAL_PORT=/dev/ttyUSB0
```

`docker-compose.yml` template:

```
version: '3.8'

services:
  slack-scroll:
    image: tazard/slack-scroll:latest
    restart: always
    init: true
    environment:
      SLACK_BOT_TOKEN: ${SLACK_BOT_TOKEN}
      SLACK_SIGNING_SECRET: ${SLACK_SIGNING_SECRET}
      CHANNEL_ID: ${CHANNEL_ID}
      SOCKET_MODE_TOKEN: ${SOCKET_MODE_TOKEN}
      SERIAL_PORT: ${SERIAL_PORT}
    devices:
      - "/dev/ttyUSB0:/dev/ttyUSB0"
```






Setting Up SlackScroll on Raspberry Pi OS
Prerequisites
Raspberry Pi with Raspberry Pi OS installed.
Internet connection.
A Slack account with admin privileges to create and manage apps.
1. Setting up your Raspberry Pi:
If you haven't set up Raspberry Pi OS on your Raspberry Pi yet:

Download the latest version of Raspberry Pi OS from the official Raspberry Pi website.
Write the image to an SD card using software like Balena Etcher.
Insert the SD card into the Raspberry Pi and power it on.
2. Install Docker on Raspberry Pi:
bash
Copy code
# Update and upgrade the system
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
curl -sSL https://get.docker.com | sh

# Add pi user to docker group
sudo usermod -aG docker pi
Reboot your Raspberry Pi:

bash
Copy code
sudo reboot
After reboot, verify Docker is installed:

bash
Copy code
docker --version
3. Install Docker Compose:
bash
Copy code
sudo apt-get install -y libffi-dev libssl-dev
sudo apt-get install -y python3 python3-pip
sudo apt-get remove python-configparser
sudo pip3 install docker-compose
Verify the installation:

bash
Copy code
docker-compose --version
4. Clone the SlackScroll Repository:
Choose a directory and clone your slackscroll repository:

bash
Copy code
git clone [your-repo-url]
cd slackscroll
5. Set Up Environment Variables:
Rename .env.sample to .env.
Open .env and fill in the appropriate values for each variable.
6. Building and Running SlackScroll:
In the slackscroll directory:

bash
Copy code
docker-compose up --build -d
This will build and start the SlackScroll service in detached mode.

7. Setting Up Slack:
Head to the Slack API portal and create a new app.
Assign necessary permissions, generate tokens, and set up events as required by SlackScroll.
Update the .env file with the appropriate Slack tokens and secrets.
Restart the Docker service:
bash
Copy code
docker-compose down
docker-compose up -d
8. Monitoring Logs:
To monitor the logs of SlackScroll:

bash
Copy code
docker-compose logs -f
Conclusion:
SlackScroll should now be set up and running on your Raspberry Pi! You can now interact with Slack and see messages displayed via the connected LED sign.