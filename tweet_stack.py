import glob
import random

from micropython_esp32 import ledsign_micro as ledsign2
from micropython_esp32.led_sign_updater_esp32 import transitions_to_title, transitions_to_tweet
from tweet import Tweet


class TweetStack(object):
    screen_width = 13

    def __init__(self, size, persistence_path, sign_port, twitter_address, sign_scroll_wait, message):
        self.size = size
        self.persistence_path = persistence_path
        self.sign_port = sign_port
        self.twitter_address = twitter_address
        self.sign_scroll_wait = sign_scroll_wait
        self.message = message

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
            else:
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
        if self.message is not None:
            sign.end_frame()
            sign.add_run_mode(ledsign2.EFFECT_SCROLL_UP)
            sign.add_text(" ")
            sign.end_frame()
            sign.add_special(ledsign2.FONT_5x7)
            sign.add_text(self.message)

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