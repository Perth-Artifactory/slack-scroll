"""Tests for LED sign driver."""

from unittest.mock import Mock, patch

import pytest

from slack_scroll.ledsign2 import COLOUR_BRIGHT_RED, EFFECT_SCROLL_LEFT, LEDSign


class TestLEDSign:
    """Test LED sign driver."""

    @pytest.fixture
    def mock_serial(self):
        """Create a mock serial connection."""
        with patch("slack_scroll.ledsign2.serial.Serial") as mock_serial_class:
            mock = Mock()
            mock_serial_class.return_value = mock
            yield mock_serial_class

    def test_init_opens_serial(self, mock_serial):
        """Test that initialization opens serial port."""
        LEDSign("/dev/ttyUSB0")
        mock_serial.assert_called_once_with("/dev/ttyUSB0", 2400)

    def test_begin_message_single_sign(self, mock_serial):
        """Test beginning message for single sign."""
        sign = LEDSign("/dev/ttyUSB0")
        sign.send_to_sign = Mock()

        sign.begin_message(sign=5, reset=True)

        assert sign.message_open is True

    def test_add_run_mode_valid(self, mock_serial):
        """Test adding valid run mode."""
        sign = LEDSign("/dev/ttyUSB0")
        sign.send_to_sign = Mock()

        sign.add_run_mode(EFFECT_SCROLL_LEFT)

        sign.send_to_sign.assert_called_once_with(bytes([EFFECT_SCROLL_LEFT]))

    def test_add_run_mode_invalid(self, mock_serial):
        """Test adding invalid run mode raises error."""
        sign = LEDSign("/dev/ttyUSB0")

        with pytest.raises(ValueError) as exc_info:
            sign.add_run_mode(99)

        assert "Run mode must be 0-24" in str(exc_info.value)

    def test_add_text_valid_ascii(self, mock_serial):
        """Test adding valid ASCII text."""
        sign = LEDSign("/dev/ttyUSB0")
        sign.send_to_sign = Mock()

        sign.add_text("Hello")

        sign.send_to_sign.assert_called_once_with(b"Hello")

    def test_add_text_invalid_character(self, mock_serial):
        """Test adding text with invalid character raises error."""
        sign = LEDSign("/dev/ttyUSB0")

        with pytest.raises(ValueError) as exc_info:
            sign.add_text("Hello\x01World")  # Control character

        assert "Invalid character" in str(exc_info.value)

    def test_add_special(self, mock_serial):
        """Test adding special command."""
        sign = LEDSign("/dev/ttyUSB0")
        sign.send_to_sign = Mock()

        sign.add_special(COLOUR_BRIGHT_RED)

        sign.send_to_sign.assert_called_once_with(b"\xef" + COLOUR_BRIGHT_RED)

    def test_end_frame(self, mock_serial):
        """Test ending frame."""
        sign = LEDSign("/dev/ttyUSB0")
        sign.send_to_sign = Mock()

        sign.end_frame()

        sign.send_to_sign.assert_called_once_with(b"\xff")

    def test_begin_file(self, mock_serial):
        """Test beginning file."""
        sign = LEDSign("/dev/ttyUSB0")
        sign.send_to_sign = Mock()

        sign.begin_file(1)

        assert sign.file_id == 1
        sign.send_to_sign.assert_called_once_with(b"\x0101")

    def test_begin_file_invalid_id(self, mock_serial):
        """Test beginning file with invalid ID."""
        sign = LEDSign("/dev/ttyUSB0")

        with pytest.raises(ValueError) as exc_info:
            sign.begin_file(100)

        assert "File ID must be 0-99" in str(exc_info.value)

    def test_end_file(self, mock_serial):
        """Test ending file."""
        sign = LEDSign("/dev/ttyUSB0")
        sign.send_to_sign = Mock()
        sign.file_id = 1

        sign.end_file()

        assert sign.file_id is None
        sign.send_to_sign.assert_called_once_with(b"\xff\xff")

    def test_end_file_no_file_open(self, mock_serial):
        """Test ending file when none is open."""
        sign = LEDSign("/dev/ttyUSB0")

        with pytest.raises(RuntimeError) as exc_info:
            sign.end_file()

        assert "No file is open" in str(exc_info.value)

    def test_end_message(self, mock_serial):
        """Test ending message."""
        sign = LEDSign("/dev/ttyUSB0")
        sign.send_to_sign = Mock()
        sign.message_open = True

        sign.end_message()

        assert sign.message_open is False
        sign.send_to_sign.assert_called_once_with(b"\x00")

    def test_end_message_not_open(self, mock_serial):
        """Test ending message when none is open."""
        sign = LEDSign("/dev/ttyUSB0")

        with pytest.raises(RuntimeError) as exc_info:
            sign.end_message()

        assert "No message is open" in str(exc_info.value)
