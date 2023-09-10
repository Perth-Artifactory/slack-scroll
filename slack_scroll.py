import os
import time
import json
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import serial  # pip install pyserial

with open('config.json') as f:
    config = json.load(f)

# Initialize the app with your bot token and signing secret
app = App(token=config["slack_bot_token"], signing_secret=config["slack_signing_secret"])

# List to store messages by timestamp
messages = {}

def fetch_existing_messages():
    print()
    print("fetch_existing_messages")
    global messages
    response = app.client.conversations_history(
        token=config["slack_bot_token"],
        channel=config["channel_id"],
        limit=100  # You can adjust the limit as needed
    )
    if response["ok"]:
        messages = {message["ts"]: message["text"] for message in response["messages"]}
    write_to_serial()

@app.event("message")
def handle_message(event, say):
    print()
    print(f"handle_message: {event=}")
    changed = False
    # Check if the message is from the desired channel
    if event["channel"] == config["channel_id"]:
        if "subtype" not in event:
            # Add the message to the list
            messages[event["ts"]] = event["text"]
            changed = True
        elif event["subtype"] == "message_changed":
            messages[event["message"]["ts"]] = event["message"]["text"]
            changed = True
        elif event["subtype"] == "message_deleted":
            # Remove the message from the list
            if event["previous_message"]["ts"] in messages:
                messages.pop(event["previous_message"]["ts"])
                changed = True
    if changed:
        write_to_serial()

def write_to_serial():
    """Write messages to serial on change (and startup)"""
    print()
    print("OUTPUT:")
    for ts in sorted(messages):
        message = messages[ts]
        # Convert the message to your special format
        formatted_message = convert_to_special_format(message)
        # Write to serial
        # serial.write(formatted_message)
        print(f"{ts=} {formatted_message}")

# Convert message to a special format (pseudo-code)
def convert_to_special_format(message):
    # Implement your conversion logic here
    return message

if __name__ == "__main__":
    fetch_existing_messages()
    # Start the app in Socket Mode
    handler = SocketModeHandler(app, config["socket_mode_token"])
    handler.start()
