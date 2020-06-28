import sys
import time


def main(args):
    print("Artifactory Twittinator - LED Sign Updater")

    if len(args) != 1:
        print("Requires exactly one argument as path to config")
        sys.exit(1)

    updater = LEDSignUpdater(config_path=args[0])

    # Main processing loop
    while True:
        updater.run()
        time.sleep(1.0)

if __name__ == "__main__":
    main(sys.argv[1:])
