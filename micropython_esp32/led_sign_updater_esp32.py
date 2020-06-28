"""
Update LED sign with formatted messages

Compatibility: MicroPython (Python 3.5)
"""

from __future__ import print_function
import json
from datetime import datetime
import sys

import ledsign_micro as ledsign2
from micropython_esp32.main import main
from tweet_stack import TweetStack

transitions_to_title = [
    ledsign2.EFFECT_SPLIT_OPEN,
    ledsign2.EFFECT_WIPE_DOWN,
    ledsign2.EFFECT_FALLING_LINES,
]

transitions_to_tweet = [
    ledsign2.EFFECT_SPLIT_OPEN,
    ledsign2.EFFECT_SPLIT_CLOSE,
    ledsign2.EFFECT_WIPE_OUT,
    ledsign2.EFFECT_WIPE_RIGHT,
    ledsign2.EFFECT_WIPE_IN,
    ledsign2.EFFECT_SPLIT_INTERLACED,
    ledsign2.EFFECT_WIPE_INTERLACED,
    ledsign2.EFFECT_WIPE_UP,
    ledsign2.EFFECT_EXPLODE,
    ledsign2.EFFECT_PACMAN,
    ledsign2.EFFECT_PACMAN,
    ledsign2.EFFECT_PACMAN,
    ledsign2.EFFECT_SHOOT,
    ledsign2.EFFECT_DISSOLVE,
    ledsign2.EFFECT_SLIDE_LETTERS,
]


class LEDSignUpdater(object):
    def __init__(self, config_path):
        print("Loading config")

        with open(config_path) as f:
            j_config = json.load(f)

        self.stack_size = j_config["stack_size"]
        self.tweet_path = j_config["tweet_path"]
        self.sign_port = j_config["sign_port"]
        self.twitter_address = j_config["twitter_address"]
        self.sign_scroll_wait = j_config["sign_scroll_wait"]
        self.update_time_min_sec = j_config["update_time_min_sec"]
        self.update_time_force_sec = j_config["update_time_force_sec"]
        self.message = j_config["message"]

        print("Loading latest {} cached tweets".format(self.stack_size))
        self.tweet_stack = TweetStack(
            size=self.stack_size,
            persistence_path=self.tweet_path,
            sign_port=self.sign_port,
            twitter_address=self.twitter_address,
            sign_scroll_wait=self.sign_scroll_wait,
            message=self.message,
        )
        print("{} tweets loaded".format(len(self.tweet_stack.tweets)))

        self.last_update = None

        self.update()

    def update(self):
        print("Updating sign")
        self.tweet_stack.update_sign()
        self.last_update = datetime.utcnow()

    def run(self):
        # Check for new files
        try:
            self.tweet_stack.check_for_update()
        except IOError as e:
            print("Error opening file, will try again later: {}".format(e))
            return

        now = datetime.utcnow()

        # If new, update sign (as long as not too recently updated)
        if self.tweet_stack.has_new and (now - self.last_update).total_seconds() > self.update_time_min_sec:
            # We have a new tweet and its not too soon since we last updated
            print("Displaying new tweet that arrived")
            self.update()

        # Update sign every 5 minutes (clears "new" message and cycles animations)
        if (now - self.last_update).total_seconds() > self.update_time_force_sec:
            print("Periodic sign update")
            self.update()


