"""Test mode with mocked Slack and sign for automated testing."""

import json
import time
from typing import Dict, List
from unittest.mock import Mock, MagicMock, patch

from slack_scroll.main import SlackScrollApp, Config
from slack_scroll.sign_output import TestSignOutput


class MockSlackClient:
    """Mock Slack client for testing."""

    def __init__(self):
        self.messages: List[Dict] = []
        self.event_handlers: Dict[str, callable] = {}

    def conversations_history(self, **kwargs) -> Mock:
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

    def trigger_event(self, event_type: str, event_data: Dict) -> None:
        if event_type in self.event_handlers:
            self.event_handlers[event_type](event_data, None)


def run() -> int:
    print("=" * 60)
    print("SLACK SCROLL - TEST MODE")
    print("=" * 60)

    # Set up test environment
    import os

    os.environ.setdefault("SLACK_BOT_TOKEN", "xoxb-test-token")
    os.environ.setdefault("SLACK_SIGNING_SECRET", "test-secret")
    os.environ.setdefault("CHANNEL_ID", "C05R9591KFH")
    os.environ.setdefault("SOCKET_MODE_TOKEN", "xapp-test-token")
    os.environ.setdefault("SERIAL_PORT", "/dev/ttyTEST")

    config = Config()

    sign_output = TestSignOutput()

    # Mock the Slack app
    with (
        patch("slack_scroll.main.App") as MockApp,
        patch("slack_scroll.main.SocketModeHandler") as MockHandler,
    ):
        mock_app = Mock()
        mock_app.client = MockSlackClient()
        MockApp.return_value = mock_app

        # Create app
        app = SlackScrollApp(sign_output, config)

        # Add test messages
        test_messages = [
            ("1234567890.000001", "Hello Artifactory!"),
            ("1234567890.000002", "This is a test message"),
            ("1234567890.000003", "Multi-line\ntext here"),
        ]

        for ts, text in test_messages:
            app.messages[ts] = text

        # Update sign
        print("\nTest 1: Update sign with test messages")
        app.update_sign()

        operations = sign_output.get_operations()
        print(f"\nSign operations recorded: {len(operations)}")

        for op, params in operations[:10]:  # Show first 10
            print(f"  {op}: {params}")

        if len(operations) > 10:
            print(f"  ... and {len(operations) - 10} more operations")

        # Test message handling
        print("\nTest 2: Simulate incoming message")
        sign_output.clear()

        test_event = {
            "channel": "C05R9591KFH",
            "ts": "1234567890.000004",
            "text": "New incoming message!",
        }

        # Manually add message
        app.messages[test_event["ts"]] = test_event["text"]
        app.update_sign()

        operations = sign_output.get_operations()
        text_ops = [op for op, params in operations if op == "add_text"]
        print(f"  Message added: {len(text_ops)} text operations")

        # Test message deletion
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
