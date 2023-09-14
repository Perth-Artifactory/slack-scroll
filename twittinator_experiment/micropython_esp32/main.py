import time

from twittinator import LEDSignUpdater

CONFIG = "config.json"


def main():
    print("Artifactory Twittinator - LED Sign Updater on ESP32 MicroPython")

    updater = LEDSignUpdater(config_path=CONFIG)

    # Main processing loop
    while True:
        updater.run()
        time.sleep(0.1)


if __name__ == "__main__":
    main()
