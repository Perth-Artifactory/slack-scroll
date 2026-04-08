"""Test mode with mocked Slack and sign for automated testing."""

from __future__ import annotations

import os
from typing import Any
from unittest.mock import Mock, patch

from slack_scroll.main import Config, SlackScrollApp
from slack_scroll.sign_output import TestSignOutput


class MockSlackClient:
    """Mock Slack client for testing."""

    def __init__(self) -> None:
        self.messages: list[dict[str, Any]] = []
        self.event_handlers: dict[str, Any] = {}

    def conversations_history(self, **kwargs: Any) -> Mock:
        response = Mock()
        response.data = {
            "ok": True,
            "messages": self.messages,
        }
        response.__getitem__ = lambda self, key: self.data[key]
        return response

    def add_message(self, ts: str, text: str, channel: str = "C05R9591KFH") -> None:
        self.messages.append(
            {
                "ts": ts,
                "text": text,
                "channel": channel,
            }
        )

    def trigger_event(self, event_type: str, event_data: dict[str, Any]) -> None:
        if event_type in self.event_handlers:
            self.event_handlers[event_type](event_data, None)


def run() -> int:
    print("=" * 60)
    print("SLACK SCROLL - TEST MODE")
    print("=" * 60)

    os.environ.setdefault("SLACK_BOT_TOKEN", "xoxb-test-token")
    os.environ.setdefault("SLACK_SIGNING_SECRET", "test-secret")
    os.environ.setdefault("CHANNEL_ID", "C05R9591KFH")
    os.environ.setdefault("SOCKET_MODE_TOKEN", "xapp-test-token")
    os.environ.setdefault("SERIAL_PORT", "/dev/ttyTEST")

    config = Config()
    sign_output = TestSignOutput()

    with (
        patch("slack_scroll.main.App") as mock_app_class,
        patch("slack_scroll.main.SocketModeHandler"),
    ):
        mock_app = Mock()
        mock_app.client = MockSlackClient()
        mock_app_class.return_value = mock_app

        app = SlackScrollApp(sign_output, config)

        test_messages = [
            ("1234567890.000001", "Hello Artifactory!"),
            ("1234567890.000002", "This is a test message"),
            ("1234567890.000003", "Multi-line\ntext here"),
        ]

        for ts, text in test_messages:
            app.messages[ts] = text

        print("\nTest 1: Update sign with test messages")
        app.update_sign()

        operations = sign_output.get_operations()
        print(f"\nSign operations recorded: {len(operations)}")

        for op, params in operations[:10]:
            print(f"  {op}: {params}")

        if len(operations) > 10:
            print(f"  ... and {len(operations) - 10} more operations")

        print("\nTest 2: Simulate incoming message")
        sign_output.clear()

        test_event = {
            "channel": "C05R9591KFH",
            "ts": "1234567890.000004",
            "text": "New incoming message!",
        }

        app.messages[test_event["ts"]] = test_event["text"]
        app.update_sign()

        operations = sign_output.get_operations()
        text_ops = [op for op, params in operations if op == "add_text"]
        print(f"  Message added: {len(text_ops)} text operations")

        print("\nTest 3: Simulate message deletion")
        sign_output.clear()

        del app.messages["1234567890.000002"]
        app.update_sign()

        operations = sign_output.get_operations()
        text_ops = [params for op, params in operations if op == "add_text"]
        texts = [p["text"] for p in text_ops]

        if "This is a test message" not in texts:
            print("  ✓ Deleted message not in output")
        else:
            print("  ✗ Deleted message still appears!")

        print("\n" + "=" * 60)
        print("TEST COMPLETE")
        print("=" * 60)

    return 0
