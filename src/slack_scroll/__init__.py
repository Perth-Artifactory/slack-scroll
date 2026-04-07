#!/usr/bin/env python3
"""
Slack Scroll - Display Slack messages on LED matrix sign

Main entry point supporting multiple modes:
- serial: Production mode with real serial output
- console: Development mode with console output instead of serial
- test: Test mode with mocked Slack and serial
"""

import os
import sys
import argparse
from typing import Optional


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Display Slack messages on LED matrix sign",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Run in serial mode (production)
  %(prog)s --mode console          # Run with console output (development)
  %(prog)s --mode test             # Run in test mode with mocks
  %(prog)s --port /dev/ttyUSB0     # Specify serial port
        """,
    )

    parser.add_argument(
        "--mode",
        choices=["serial", "console", "test"],
        default=os.environ.get("SLACK_SCROLL_MODE", "serial"),
        help="Operating mode: serial (production), console (dev), or test (default: serial)",
    )

    parser.add_argument(
        "--port",
        default=os.environ.get("SERIAL_PORT", "/dev/ttyUSB0"),
        help="Serial port for LED sign (default: /dev/ttyUSB0)",
    )

    parser.add_argument(
        "--channel",
        default=os.environ.get("CHANNEL_ID"),
        help="Slack channel ID to monitor",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output",
    )

    args = parser.parse_args()

    # Set environment variables from args
    if args.port:
        os.environ["SERIAL_PORT"] = args.port
    if args.channel:
        os.environ["CHANNEL_ID"] = args.channel
    if args.verbose:
        os.environ["SLACK_SCROLL_VERBOSE"] = "1"

    # Import and run appropriate mode
    if args.mode == "test":
        from slack_scroll.modes import test_mode

        return test_mode.run()
    elif args.mode == "console":
        from slack_scroll.modes import console_mode

        return console_mode.run()
    else:  # serial mode (default)
        from slack_scroll.modes import serial_mode

        return serial_mode.run()


if __name__ == "__main__":
    sys.exit(main())
