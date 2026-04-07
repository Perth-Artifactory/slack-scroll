#!/usr/bin/env python3
"""
Slack Scroll - Main application logic
"""

import os
import json
import random
from typing import Dict, Optional, Callable
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from slack_scroll.sign_output import SignOutput


# Animation configurations
TRANSITIONS_TO_TITLE = [
    "SPLIT_OPEN",
    "WIPE_DOWN",
    "FALLING_LINES",
]

TRANSITIONS_BETWEEN_MESSAGES = [
    "SPLIT_OPEN",
    "SPLIT_CLOSE",
    "WIPE_OUT",
    "WIPE_RIGHT",
    "WIPE_IN",
    "SPLIT_INTERLACED",
    "WIPE_INTERLACED",
    "WIPE_UP",
    "EXPLODE",
    "PACMAN",
    "SHOOT",
    "DISSOLVE",
    "SLIDE_LETTERS",
]

MESSAGE_COLOURS = [
    "BRIGHT_RED",
    "DIM_RED",
    "AMBER",
    "YELLOW",
    "DIM_ORANGE",
    "BRIGHT_ORANGE",
    "DIM_GREEN",
    "BRIGHT_GREEN",
]


class Config:
    """Application configuration from environment variables."""

    def __init__(self):
        self.slack_bot_token = os.environ.get("SLACK_BOT_TOKEN")
        self.slack_signing_secret = os.environ.get("SLACK_SIGNING_SECRET")
        self.channel_id = os.environ.get("CHANNEL_ID")
        self.socket_mode_token = os.environ.get("SOCKET_MODE_TOKEN")
        self.serial_port = os.environ.get("SERIAL_PORT", "/dev/ttyUSB0")
        self.verbose = os.environ.get("SLACK_SCROLL_VERBOSE", "0") == "1"

    def validate(self) -> None:
        """Validate that all required configuration is present."""
        required = [
            ("slack_bot_token", "SLACK_BOT_TOKEN"),
            ("slack_signing_secret", "SLACK_SIGNING_SECRET"),
            ("channel_id", "CHANNEL_ID"),
            ("socket_mode_token", "SOCKET_MODE_TOKEN"),
        ]

        missing = []
        for attr, env_var in required:
            if not getattr(self, attr):
                missing.append(env_var)

        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")


class SlackScrollApp:
    """Main Slack Scroll application."""

    def __init__(self, sign_output: SignOutput, config: Optional[Config] = None):
        self.config = config or Config()
        self.config.validate()
        self.sign_output = sign_output
        self.messages: Dict[str, str] = {}
        self.app = App(
            token=self.config.slack_bot_token,
            signing_secret=self.config.slack_signing_secret,
        )
        self._setup_handlers()

    def _setup_handlers(self) -> None:
        """Set up Slack event handlers."""

        @self.app.event("message")
        def handle_message(event, say):
            """Handle incoming Slack messages."""
            if self.config.verbose:
                print(f"\nReceived message event: {json.dumps(event, indent=2)}")

            changed = False

            # Check if message is from our channel
            if event.get("channel") == self.config.channel_id:
                subtype = event.get("subtype")

                if subtype is None:
                    # Regular message
                    self.messages[event["ts"]] = event["text"]
                    changed = True
                    if self.config.verbose:
                        print(f"Added message: {event['ts']} = {event['text'][:50]}...")

                elif subtype == "message_changed":
                    # Message was edited
                    self.messages[event["message"]["ts"]] = event["message"]["text"]
                    changed = True
                    if self.config.verbose:
                        print(f"Updated message: {event['message']['ts']}")

                elif subtype == "message_deleted":
                    # Message was deleted
                    ts = event["previous_message"]["ts"]
                    if ts in self.messages:
                        del self.messages[ts]
                        changed = True
                        if self.config.verbose:
                            print(f"Deleted message: {ts}")

                elif self.config.verbose:
                    print(f"Ignored subtype: {subtype}")

            if changed:
                self.update_sign()

    def fetch_existing_messages(self) -> None:
        """Fetch existing messages from Slack channel."""
        print("\nFetching existing messages...")

        try:
            response = self.app.client.conversations_history(
                token=self.config.slack_bot_token,
                channel=self.config.channel_id,
                limit=100,
            )

            if response["ok"]:
                self.messages = {}
                for message in response["messages"]:
                    if "subtype" not in message:
                        self.messages[message["ts"]] = message["text"]
                    elif self.config.verbose:
                        print(
                            f"Ignored existing: {message.get('subtype')} = {message.get('text', '')[:30]}"
                        )

                print(f"Loaded {len(self.messages)} messages")
                self.update_sign()
            else:
                print(f"Error fetching messages: {response.get('error')}")

        except Exception as e:
            print(f"Exception fetching messages: {e}")

    def update_sign(self) -> None:
        """Update the LED sign with current messages."""
        print("\n" + "=" * 50)
        print("UPDATING SIGN")
        print("=" * 50)

        # Start message
        self.sign_output.begin_message(reset=True)
        self.sign_output.begin_file(1)

        # Draw title
        self._draw_title()

        # Draw messages
        for ts in sorted(self.messages.keys()):
            message = self.messages[ts]
            print(f"\nMessage [{ts}]: {message[:60]}{'...' if len(message) > 60 else ''}")
            self._draw_message(message)

        # End message
        self.sign_output.end_file()
        self.sign_output.end_message()

        print("\n" + "=" * 50)
        print("SIGN UPDATE COMPLETE")
        print("=" * 50)

    def _draw_title(self) -> None:
        """Draw the title on the sign."""
        # First line
        self.sign_output.add_run_mode("SCROLL_UP")
        self.sign_output.add_special("FONT_5x5")
        self.sign_output.add_special("COLOUR_RAINBOW2")
        self.sign_output.add_text("Artifactory")
        self.sign_output.end_frame()

        # Second line
        self.sign_output.add_run_mode(random.choice(TRANSITIONS_TO_TITLE))
        self.sign_output.add_special("FONT_5x5")
        self.sign_output.add_special("COLOUR_RAINBOW2")
        self.sign_output.add_text("SlackScroll")
        self.sign_output.end_frame()

    def _draw_message(self, text: str) -> None:
        """Draw a message on the sign."""
        first = True
        run_mode_block = random.choice(TRANSITIONS_BETWEEN_MESSAGES)
        run_mode_line = random.choice(TRANSITIONS_TO_TITLE)
        colour = random.choice(MESSAGE_COLOURS)

        for line in text.split("\n"):
            if not line.strip():
                continue

            self.sign_output.end_frame()

            if first:
                self.sign_output.add_run_mode(run_mode_block)
            else:
                self.sign_output.add_run_mode(run_mode_line)

            first = False
            self.sign_output.add_special(colour)
            self.sign_output.add_special("FONT_5x7")

            try:
                self.sign_output.add_text(line)
            except Exception as e:
                print(f"Error adding text: {e}")
                self.sign_output.add_text("-InvalidChar-")

    def run(self) -> None:
        """Run the application."""
        print("\n" + "=" * 50)
        print("SLACK SCROLL STARTING")
        print("=" * 50)
        print(f"Mode: {self.sign_output.__class__.__name__}")
        print(f"Channel: {self.config.channel_id}")
        print(f"Port: {self.config.serial_port}")
        print("=" * 50 + "\n")

        # Fetch existing messages
        self.fetch_existing_messages()

        # Start Socket Mode handler
        print("\nStarting Socket Mode handler...")
        print("Press Ctrl+C to exit\n")

        handler = SocketModeHandler(self.app, self.config.socket_mode_token)
        handler.start()


def main(sign_output: Optional[SignOutput] = None) -> int:
    """Main entry point."""
    try:
        config = Config()
        config.validate()

        if sign_output is None:
            # Default to serial output
            from slack_scroll.sign_output import SerialSignOutput

            sign_output = SerialSignOutput(config.serial_port)

        app = SlackScrollApp(sign_output, config)
        app.run()
        return 0

    except KeyboardInterrupt:
        print("\n\nShutting down...")
        return 0
    except Exception as e:
        print(f"\nError: {e}")
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
