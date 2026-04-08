#!/usr/bin/env python3
"""
Slack Scroll - Main application logic
"""

from __future__ import annotations

import json
import os
import random
from typing import TYPE_CHECKING, Any

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from slack_scroll.sign_output import SerialSignOutput, SignOutput

if TYPE_CHECKING:
    from collections.abc import Callable

# Animation configurations
TRANSITIONS_TO_TITLE: list[str] = [
    "SPLIT_OPEN",
    "WIPE_DOWN",
    "FALLING_LINES",
]

TRANSITIONS_BETWEEN_MESSAGES: list[str] = [
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

MESSAGE_COLOURS: list[str] = [
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

    def __init__(self) -> None:
        self.slack_bot_token: str | None = os.environ.get("SLACK_BOT_TOKEN")
        self.slack_signing_secret: str | None = os.environ.get("SLACK_SIGNING_SECRET")
        self.channel_id: str | None = os.environ.get("CHANNEL_ID")
        self.socket_mode_token: str | None = os.environ.get("SOCKET_MODE_TOKEN")
        self.serial_port: str = os.environ.get("SERIAL_PORT", "/dev/ttyUSB0")
        self.verbose: bool = os.environ.get("SLACK_SCROLL_VERBOSE", "0") == "1"

    def validate(self) -> None:
        """Validate that all required configuration is present."""
        required: list[tuple[str, str]] = [
            ("slack_bot_token", "SLACK_BOT_TOKEN"),
            ("slack_signing_secret", "SLACK_SIGNING_SECRET"),
            ("channel_id", "CHANNEL_ID"),
            ("socket_mode_token", "SOCKET_MODE_TOKEN"),
        ]

        missing: list[str] = []
        for attr, env_var in required:
            if not getattr(self, attr):
                missing.append(env_var)

        if missing:
            msg = f"Missing required environment variables: {', '.join(missing)}"
            raise ValueError(msg)


class SlackScrollApp:
    """Main Slack Scroll application."""

    def __init__(
        self,
        sign_output: SignOutput,
        config: Config | None = None,
    ) -> None:
        self.config = config or Config()
        self.config.validate()
        self.sign_output = sign_output
        self.messages: dict[str, str] = {}
        self.app = App(
            token=self.config.slack_bot_token,
            signing_secret=self.config.slack_signing_secret,
        )
        self._setup_handlers()

    def _setup_handlers(self) -> None:
        """Set up Slack event handlers."""

        @self.app.event("message")
        def handle_message(event: dict[str, Any], say: Callable[..., Any]) -> None:
            """Handle incoming Slack messages."""
            if self.config.verbose:
                print(f"\nReceived message event: {json.dumps(event, indent=2)}")

            changed = False

            if event.get("channel") == self.config.channel_id:
                subtype = event.get("subtype")

                if subtype is None:
                    self.messages[event["ts"]] = event["text"]
                    changed = True
                    if self.config.verbose:
                        preview = event["text"][:50]
                        print(f"Added message: {event['ts']} = {preview}...")

                elif subtype == "message_changed":
                    msg = event["message"]
                    self.messages[msg["ts"]] = msg["text"]
                    changed = True
                    if self.config.verbose:
                        print(f"Updated message: {msg['ts']}")

                elif subtype == "message_deleted":
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
            # Config is validated in __init__, so channel_id is not None
            assert self.config.channel_id is not None
            response = self.app.client.conversations_history(
                token=self.config.slack_bot_token,
                channel=self.config.channel_id,
                limit=100,
            )

            if response["ok"]:
                self.messages = {}
                messages = response.get("messages", [])
                for message in messages:
                    if "subtype" not in message:
                        self.messages[message["ts"]] = message["text"]
                    elif self.config.verbose:
                        subtype = message.get("subtype", "unknown")
                        text = message.get("text", "")[:30]
                        print(f"Ignored existing: {subtype} = {text}")

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

        self.sign_output.begin_message(reset=True)
        self.sign_output.begin_file(1)
        self._draw_title()

        for ts in sorted(self.messages.keys()):
            message = self.messages[ts]
            preview = message[:60]
            suffix = "..." if len(message) > 60 else ""
            print(f"\nMessage [{ts}]: {preview}{suffix}")
            self._draw_message(message)

        self.sign_output.end_file()
        self.sign_output.end_message()

        print("\n" + "=" * 50)
        print("SIGN UPDATE COMPLETE")
        print("=" * 50)

    def _draw_title(self) -> None:
        """Draw the title on the sign."""
        self.sign_output.add_run_mode("SCROLL_UP")
        self.sign_output.add_special("FONT_5x5")
        self.sign_output.add_special("COLOUR_RAINBOW2")
        self.sign_output.add_text("Artifactory")
        self.sign_output.end_frame()

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

        self.fetch_existing_messages()

        print("\nStarting Socket Mode handler...")
        print("Press Ctrl+C to exit\n")

        handler = SocketModeHandler(self.app, self.config.socket_mode_token)
        handler.start()


def main(sign_output: SignOutput | None = None) -> int:
    """Main entry point."""
    try:
        config = Config()
        config.validate()

        if sign_output is None:
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
