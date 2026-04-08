"""Tests for Slack Scroll application."""

from unittest.mock import Mock, patch

import pytest

from slack_scroll.main import Config, SlackScrollApp
from slack_scroll.sign_output import ConsoleSignOutput, TestSignOutput


class TestConfig:
    """Test configuration handling."""

    def test_config_from_environment(self, monkeypatch):
        """Test loading config from environment variables."""
        monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-test")
        monkeypatch.setenv("SLACK_SIGNING_SECRET", "secret")
        monkeypatch.setenv("CHANNEL_ID", "C123")
        monkeypatch.setenv("SOCKET_MODE_TOKEN", "xapp-test")

        config = Config()

        assert config.slack_bot_token == "xoxb-test"
        assert config.slack_signing_secret == "secret"
        assert config.channel_id == "C123"
        assert config.socket_mode_token == "xapp-test"

    def test_config_validation_missing_vars(self):
        """Test validation fails with missing variables."""
        config = Config()

        with pytest.raises(ValueError) as exc_info:
            config.validate()

        assert "Missing required environment variables" in str(exc_info.value)

    def test_config_defaults(self, monkeypatch):
        """Test default values for optional config."""
        monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-test")
        monkeypatch.setenv("SLACK_SIGNING_SECRET", "secret")
        monkeypatch.setenv("CHANNEL_ID", "C123")
        monkeypatch.setenv("SOCKET_MODE_TOKEN", "xapp-test")

        config = Config()

        assert config.serial_port == "/dev/ttyUSB0"
        assert config.verbose is False


class TestSlackScrollApp:
    """Test main application logic."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration."""
        config = Mock(spec=Config)
        config.slack_bot_token = "xoxb-test"
        config.slack_signing_secret = "secret"
        config.channel_id = "C123"
        config.socket_mode_token = "xapp-test"
        config.serial_port = "/dev/ttyTEST"
        config.verbose = False
        return config

    @pytest.fixture
    def test_sign(self):
        """Create a test sign output."""
        return TestSignOutput()

    def test_app_initialization(self, mock_config, test_sign):
        """Test app initializes correctly."""
        with patch("slack_scroll.main.App") as mock_app_class:
            mock_app = Mock()
            mock_app_class.return_value = mock_app

            app = SlackScrollApp(test_sign, mock_config)

            assert app.config == mock_config
            assert app.sign_output == test_sign
            assert app.messages == {}

    def test_update_sign_empty(self, mock_config, test_sign):
        """Test updating sign with no messages."""
        with patch("slack_scroll.main.App") as mock_app_class:
            mock_app = Mock()
            mock_app_class.return_value = mock_app

            app = SlackScrollApp(test_sign, mock_config)
            app.update_sign()

            operations = test_sign.get_operations()

            # Should have begin/end message and title
            assert any(op == "begin_message" for op, _ in operations)
            assert any(op == "end_message" for op, _ in operations)
            assert any(
                op == "add_text" and params.get("text") == "Artifactory"
                for op, params in operations
            )

    def test_update_sign_with_messages(self, mock_config, test_sign):
        """Test updating sign with messages."""
        with patch("slack_scroll.main.App") as mock_app_class:
            mock_app = Mock()
            mock_app_class.return_value = mock_app

            app = SlackScrollApp(test_sign, mock_config)
            app.messages = {
                "1234567890.000001": "Test message 1",
                "1234567890.000002": "Test message 2",
            }
            app.update_sign()

            operations = test_sign.get_operations()
            text_ops = [params["text"] for op, params in operations if op == "add_text"]

            assert "Test message 1" in text_ops
            assert "Test message 2" in text_ops


class TestSignOutputImpl:
    """Test sign output implementations."""

    def test_test_sign_output_records_operations(self):
        """Test that TestSignOutput records all operations."""
        sign = TestSignOutput()

        sign.begin_message()
        sign.add_text("Hello")
        sign.end_frame()
        sign.end_message()

        operations = sign.get_operations()

        assert len(operations) == 4
        assert operations[0][0] == "begin_message"
        assert operations[1] == ("add_text", {"text": "Hello"})
        assert operations[2][0] == "end_frame"
        assert operations[3] == ("end_message", {})

    def test_test_sign_output_clear(self):
        """Test clearing operations."""
        sign = TestSignOutput()

        sign.add_text("Test")
        sign.clear()

        assert sign.get_operations() == []
        assert sign.frame_count == 0

    def test_console_sign_output(self, capsys):
        """Test console output produces readable text."""
        sign = ConsoleSignOutput()

        sign.begin_message()
        sign.add_text("Hello World")
        sign.end_frame()
        sign.end_message()

        captured = capsys.readouterr()

        assert "Hello World" in captured.out
        assert "[CONSOLE]" in captured.out
        assert "[TEXT]" in captured.out


class TestMessageHandling:
    """Test Slack message event handling."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration."""
        config = Mock(spec=Config)
        config.slack_bot_token = "xoxb-test"
        config.slack_signing_secret = "secret"
        config.channel_id = "C123"
        config.socket_mode_token = "xapp-test"
        config.serial_port = "/dev/ttyTEST"
        config.verbose = False
        return config

    def test_handle_new_message(self, mock_config):
        """Test handling new message event."""
        test_sign = TestSignOutput()

        with patch("slack_scroll.main.App") as mock_app_class:
            mock_app = Mock()
            mock_app_class.return_value = mock_app

            app = SlackScrollApp(test_sign, mock_config)

            # Simulate message event
            event = {
                "channel": "C123",
                "ts": "1234567890.000001",
                "text": "New message",
            }

            # Get the handler and call it
            app.messages[event["ts"]] = event["text"]

            assert app.messages[event["ts"]] == "New message"

    def test_handle_message_wrong_channel(self, mock_config):
        """Test ignoring messages from wrong channel."""
        test_sign = TestSignOutput()

        with patch("slack_scroll.main.App") as mock_app_class:
            mock_app = Mock()
            mock_app_class.return_value = mock_app

            app = SlackScrollApp(test_sign, mock_config)
            app.messages = {}

            event = {
                "channel": "C999",  # Wrong channel
                "ts": "1234567890.000001",
                "text": "Wrong channel message",
            }

            # Message should not be added
            assert event["ts"] not in app.messages
