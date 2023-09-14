
"""
Use wget to download tweets and run frequently
"""

import time
import logging
import subprocess

#command = r"wget -r -nc -nH --cut-dirs=2 http://util/twittinator/tweets/"
command = r"ping google.com"

WAIT = 15.0


def grab_files():
    # Setup logging
    # TODO: Rotating logging handler
    logger = logging.getLogger('tweet_download')
    logger.setLevel(logging.DEBUG)

    fh = logging.FileHandler('dl.log')
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)

    logger.info("Starting")

    while True:
        logger.info("Running: {}".format(command))
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        logger.info("Result: {}".format(result.returncode))

        logger.debug("##### Stdout #####")
        logger.debug(result.stdout.decode())
        logger.debug("##### Stderr #####")
        logger.debug(result.stderr.decode())

        logger.debug("Waiting {}s...".format(WAIT))

        time.sleep(WAIT)


def main():
    grab_files()


if __name__ == "__main__":
    main()

