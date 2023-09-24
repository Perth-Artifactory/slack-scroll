import os
import time
import json
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import ledsign2
import random

transitions_to_title = [
    ledsign2.EFFECT_SPLIT_OPEN,
    ledsign2.EFFECT_WIPE_DOWN,
    ledsign2.EFFECT_FALLING_LINES,
]

transitions_between_messages = [
    ledsign2.EFFECT_SPLIT_OPEN,
    ledsign2.EFFECT_SPLIT_CLOSE,
    ledsign2.EFFECT_WIPE_OUT,
    ledsign2.EFFECT_WIPE_RIGHT,
    ledsign2.EFFECT_WIPE_IN,
    ledsign2.EFFECT_SPLIT_INTERLACED,
    ledsign2.EFFECT_WIPE_INTERLACED,
    ledsign2.EFFECT_WIPE_UP,
    ledsign2.EFFECT_EXPLODE,
    ledsign2.EFFECT_PACMAN,
    ledsign2.EFFECT_PACMAN,
    ledsign2.EFFECT_PACMAN,
    ledsign2.EFFECT_SHOOT,
    ledsign2.EFFECT_DISSOLVE,
    ledsign2.EFFECT_SLIDE_LETTERS,
]

message_colours = [
    ledsign2.COLOUR_BRIGHT_RED,
    ledsign2.COLOUR_DIM_RED,
    ledsign2.COLOUR_AMBER,
    ledsign2.COLOUR_YELLOW,
    ledsign2.COLOUR_DIM_ORANGE,
    ledsign2.COLOUR_BRIGHT_ORANGE,
    ledsign2.COLOUR_DIM_GREEN,
    ledsign2.COLOUR_BRIGHT_GREEN,
]

class Config:
    def __init__(self):
        self.slack_bot_token = os.environ.get("SLACK_BOT_TOKEN")
        self.slack_signing_secret = os.environ.get("SLACK_SIGNING_SECRET")
        self.channel_id = os.environ.get("CHANNEL_ID")
        self.socket_mode_token = os.environ.get("SOCKET_MODE_TOKEN")
        self.serial_port = os.environ.get("SERIAL_PORT")

    def validate(self):
        attributes = vars(self)
        for attribute, value in attributes.items():
            if not value:
                raise ValueError(f"Environment variable for {attribute} not set!")

# Initialize the configuration
config = Config()
config.validate()

# Initialize the app with your bot token and signing secret
app = App(token=config.slack_bot_token, signing_secret=config.slack_signing_secret)

# List to store messages by timestamp
messages = {}

def fetch_existing_messages():
    print()
    print("fetch_existing_messages")
    global messages
    response = app.client.conversations_history(
        token=config.slack_bot_token,
        channel=config.channel_id,
        limit=100  # You can adjust the limit as needed
    )
    if response["ok"]:
        messages = {message["ts"]: message["text"] for message in response["messages"]}
    update_sign()

@app.event("message")
def handle_message(event, say):
    print()
    print(f"handle_message: {event=}")
    changed = False
    # Check if the message is from the desired channel
    if event["channel"] == config.channel_id:
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
        update_sign()

def update_sign():
    """Write messages to serial on change (and startup)"""
    print()
    print("Messages:")
    print("---")

    sign = ledsign2.LEDSign(config.serial_port)
    sign.begin_message(reset=True)
    sign.begin_file(1)

    draw_title(sign)

    for ts in sorted(messages):
        message = messages[ts]
        print(f"Message: {ts=} {message=}")
        draw_message(sign, message)
        print("---")

    # sign.end_frame()
    # sign.add_special(ledsign2.ANIMATION_HAPPY_EASTER)
    # sign.add_special(ledsign2.GRAPHIC_CARS)
    # sign.end_frame()
    # sign.add_special(ledsign2.GRAPHIC_VESSEL)
    # sign.end_frame()
    # sign.add_special(ledsign2.SYMBOL_SNAKE)

    sign.end_file()
    sign.end_message()

def draw_title(sign):
    sign.add_run_mode(ledsign2.EFFECT_SCROLL_UP)
    sign.add_special(ledsign2.FONT_5x5)
    sign.add_special(ledsign2.COLOUR_RAINBOW2)
    sign.add_text("Artifactory")

    sign.end_frame()
    sign.add_run_mode(random.choice(transitions_to_title))
    sign.add_special(ledsign2.FONT_5x5)
    sign.add_special(ledsign2.COLOUR_RAINBOW2)
    sign.add_text("SlackScroll")

def draw_message(sign, text):
    # Scroll the whole thing at once
    sign.end_frame()
    sign.add_run_mode(random.choice(transitions_between_messages))
    colour = random.choice(message_colours)
    first = True
    for line in text.split('\n'):
        if not first:
            sign.add_run_mode(random.choice(transitions_to_title))
        first = False
        sign.add_special(colour)
        sign.add_special(ledsign2.FONT_5x7)
        try:
            sign.add_text(line)
        except Exception as e:
            print("Exception: " + str(e))
            sign.add_text("-InvalidChar-")

if __name__ == "__main__":
    fetch_existing_messages()
    # Start the app in Socket Mode
    handler = SocketModeHandler(app, config.socket_mode_token)
    handler.start()
