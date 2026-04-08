"""Console mode - shows sign output in terminal instead of serial."""

from slack_scroll.main import Config, SlackScrollApp
from slack_scroll.sign_output import ConsoleSignOutput


def run() -> int:
    config = Config()
    config.validate()

    sign_output = ConsoleSignOutput(config.serial_port)
    app = SlackScrollApp(sign_output, config)

    try:
        app.run()
        return 0
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        return 0
    except Exception as e:
        print(f"\nError: {e}")
        return 1
