"""
Script to poll for new tweet files and update LED sign as required

Python 2.7 only
"""

from __future__ import print_function
import glob
import random
import json
from datetime import datetime
import sys
import time
import ledsign2
from tweet import Tweet

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


class TweetStack(object):
    screen_width = 13

    def __init__(self, size, persistence_path, sign_port, twitter_address, sign_scroll_wait):
        self.size = size
        self.persistence_path = persistence_path
        self.sign_port = sign_port
        self.twitter_address = twitter_address
        self.sign_scroll_wait = sign_scroll_wait

        self.tweets = []
        self.has_new = False

        self.check_for_update()

    def check_for_update(self):
        # List all tweets in directory in filename order (date time order)
        file_paths = sorted(glob.glob(self.persistence_path.format('*')))

        # We are interested in only the last "self.size" tweets
        file_paths = file_paths[-self.size:]

        # Check if there are more or fewer tweets that should be displayed
        different = not (len(self.tweets) == len(file_paths))

        if not different:
            # Check through the paths
            for (tweet_path, _), file_path in zip(self.tweets, file_paths):
                if tweet_path != file_path:
                    different = True
                    break

        if different:
            # Reload the tweets since there is a difference
            print("Found difference in tweets on disk")
            self.load_from_disk(file_paths)

    def load_from_disk(self, file_paths):
        # Dump existing tweets
        self.tweets = []

        # Load last 5 tweets (or less if fewer)
        for path in file_paths[-5:]:
            # If there is a problem loading tweet file, skip over it
            try:
                tweet = Tweet.from_file(path)
            except ValueError as e:
                print("Cannot decode tweet file '{}': {}".format(path, e))
            finally:
                self.tweets.append([path, tweet])

                # Flag that at least one tweet is new
                # (only flag when actually loading tweet)
                self.has_new = True

    # def add_tweet(self, tweet):
    #     tweet.save_to_file(self.persistence_path)
    #     self.tweets.append(tweet)
    #     if len(self.tweets) > self.size:
    #         self.tweets.pop(0)

    def split_text(self, text):
        length = len(text)

        # Want to round up
        panels = float(length) / float(self.screen_width)
        if int(panels) != panels:
            panels += 1
        panels = int(panels)

        for idx in range(panels):
            yield "{:<13}".format(text[idx * self.screen_width: (idx + 1) * self.screen_width])

    def update_sign(self):
        sign = ledsign2.LEDSign(self.sign_port)
        sign.begin_message(reset=True)
        sign.begin_file(1)

        # Newest tweet first
        tweets_to_show = self.tweets[::-1]

        if self.has_new:
            self.has_new = False
            # Show newest tweet with special "just in" headline first
            if len(tweets_to_show) > 0:
                # Pop it off so not included below only when this runs
                _, tweet = tweets_to_show.pop(0)
                self.draw_tweet_just_in(sign)
                self.draw_username(sign, tweet)
                self.draw_message(sign, tweet)
                sign.end_frame()

        # Now show title
        self.draw_title(sign)

        # Promote twitter address for this sign
        self.draw_call_for_tweets(sign)

        # Back to the rest of the tweets
        for _, tweet in tweets_to_show:
            self.draw_tweet_headline(sign)
            self.draw_username(sign, tweet)
            self.draw_message(sign, tweet)

        # if len(self.tweets) == 0:
        #     # No tweets, encourage some
        #     self.draw_call_for_tweets(sign)

        sign.end_file()
        sign.end_message()

    def draw_title(self, sign):
        sign.add_run_mode(ledsign2.EFFECT_SCROLL_UP)
        sign.add_special(ledsign2.FONT_5x5)
        sign.add_special(ledsign2.COLOUR_RAINBOW2)
        sign.add_text("Artifactory")
        sign.end_frame()
        sign.add_run_mode(random.choice(transitions_to_title))
        sign.add_special(ledsign2.FONT_5x5)
        sign.add_special(ledsign2.COLOUR_RAINBOW1)
        sign.add_text("Twittinator")

    def draw_tweet_headline(self, sign):
        sign.end_frame()

        sign.add_run_mode(ledsign2.EFFECT_SCROLL_UP)
        sign.add_special(ledsign2.FONT_5x7)

        sign.add_special(ledsign2.COLOUR_RAINBOW4)
        sign.add_special(ledsign2.SYMBOL_STARBURST)

        sign.add_special(ledsign2.COLOUR_BRIGHT_ORANGE)
        sign.add_text("Tweet")

        sign.add_special(ledsign2.COLOUR_RAINBOW4)
        sign.add_special(ledsign2.SYMBOL_STARBURST)

    def draw_call_for_tweets(self, sign):
        sign.end_frame()

        sign.add_run_mode(ledsign2.EFFECT_SCROLL_UP)
        sign.add_special(ledsign2.FONT_5x7)
        sign.add_special(ledsign2.COLOUR_BRIGHT_ORANGE)
        sign.add_text(" Tweet to: ")

        text = "@{}".format(self.twitter_address[0])
        if self.sign_scroll_wait:
            for bit in self.split_text(text):
                sign.end_frame()
                sign.add_run_mode(ledsign2.EFFECT_SCROLL_LEFT)
                sign.add_special(ledsign2.FONT_5x7)
                sign.add_special(ledsign2.COLOUR_BRIGHT_GREEN)
                sign.add_text(bit)
        else:
            sign.end_frame()
            sign.add_run_mode(ledsign2.EFFECT_SCROLL_LEFT)
            sign.add_special(ledsign2.FONT_5x7)
            sign.add_special(ledsign2.COLOUR_BRIGHT_GREEN)
            sign.add_text(text)

    def draw_tweet_just_in(self, sign):
        sign.add_run_mode(ledsign2.EFFECT_SCROLL_UP)
        sign.add_special(ledsign2.FONT_5x7)

        sign.add_special(ledsign2.COLOUR_RAINBOW3)
        sign.add_special(ledsign2.SYMBOL_STARBURST)

        sign.add_special(ledsign2.COLOUR_YELLOW)
        sign.add_text("Just In")

        sign.add_special(ledsign2.COLOUR_RAINBOW3)
        sign.add_special(ledsign2.SYMBOL_STARBURST)

    def draw_username(self, sign, tweet):
        text = "@" + tweet.screen_name + ": "
        # text = "@" + tweet.user + ": "
        first = True
        for bit in self.split_text(text):
            sign.end_frame()

            if first:
                sign.add_run_mode(random.choice(transitions_to_tweet))
                first = False
            else:
                sign.add_run_mode(ledsign2.EFFECT_SCROLL_LEFT)

            sign.add_special(ledsign2.COLOUR_BRIGHT_GREEN)
            sign.add_special(ledsign2.FONT_5x7)
            sign.add_text(bit)

    def draw_message(self, sign, tweet):
        text = tweet.text

        if self.sign_scroll_wait:
            # Scroll one 13 character frame at a time
            for bit in self.split_text(text):
                sign.end_frame()

                sign.add_run_mode(ledsign2.EFFECT_SCROLL_LEFT)
                sign.add_special(ledsign2.COLOUR_BRIGHT_RED)
                sign.add_special(ledsign2.FONT_5x7)
                sign.add_text(bit)
        else:
            # Scroll the whole thing at once
            sign.end_frame()
            sign.add_run_mode(ledsign2.EFFECT_SCROLL_LEFT)
            sign.add_special(ledsign2.COLOUR_BRIGHT_RED)
            sign.add_special(ledsign2.FONT_5x7)
            sign.add_text(text)


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

        print("Loading latest {} cached tweets".format(self.stack_size))
        self.tweet_stack = TweetStack(
            size=self.stack_size,
            persistence_path=self.tweet_path,
            sign_port=self.sign_port,
            twitter_address=self.twitter_address,
            sign_scroll_wait=self.sign_scroll_wait,
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
