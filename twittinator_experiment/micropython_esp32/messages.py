"""
Message stack
"""
import random
import ledsign_micro as ledsign


class MessageStack(object):
    def __init__(self, sign_pin, size, persistence_path):
        self.sign_pin = sign_pin
        self.size = size
        self.persistence_path = persistence_path

        self.messages = []

    def update_sign(self):
        sign = ledsign.LEDSign(self.sign_pin)
        sign.begin_message(reset=True)
        sign.begin_file(1)

        # Newest tweet first
        tweets_to_show = self.messages[::-1]

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
        sign.add_run_mode(ledsign.EFFECT_SCROLL_UP)
        sign.add_special(ledsign.FONT_5x5)
        sign.add_special(ledsign.COLOUR_RAINBOW2)
        sign.add_text("Artifactory")
        sign.end_frame()
        sign.add_run_mode(random.choice(transitions_to_title))
        sign.add_special(ledsign.FONT_5x5)
        sign.add_special(ledsign.COLOUR_RAINBOW1)
        sign.add_text("Twittinator")
        if self.message is not None:
            sign.end_frame()
            sign.add_run_mode(ledsign.EFFECT_SCROLL_UP)
            sign.add_text(" ")
            sign.end_frame()
            sign.add_special(ledsign.FONT_5x7)
            sign.add_text(self.message)

    def draw_tweet_headline(self, sign):
        sign.end_frame()

        sign.add_run_mode(ledsign.EFFECT_SCROLL_UP)
        sign.add_special(ledsign.FONT_5x7)

        sign.add_special(ledsign.COLOUR_RAINBOW4)
        sign.add_special(ledsign.SYMBOL_STARBURST)

        sign.add_special(ledsign.COLOUR_BRIGHT_ORANGE)
        sign.add_text("Tweet")

        sign.add_special(ledsign.COLOUR_RAINBOW4)
        sign.add_special(ledsign.SYMBOL_STARBURST)

    def draw_call_for_tweets(self, sign):
        sign.end_frame()

        sign.add_run_mode(ledsign.EFFECT_SCROLL_UP)
        sign.add_special(ledsign.FONT_5x7)
        sign.add_special(ledsign.COLOUR_BRIGHT_ORANGE)
        sign.add_text(" Tweet to: ")

        text = "@{}".format(self.twitter_address[0])
        if self.sign_scroll_wait:
            for bit in self.split_text(text):
                sign.end_frame()
                sign.add_run_mode(ledsign.EFFECT_SCROLL_LEFT)
                sign.add_special(ledsign.FONT_5x7)
                sign.add_special(ledsign.COLOUR_BRIGHT_GREEN)
                sign.add_text(bit)
        else:
            sign.end_frame()
            sign.add_run_mode(ledsign.EFFECT_SCROLL_LEFT)
            sign.add_special(ledsign.FONT_5x7)
            sign.add_special(ledsign.COLOUR_BRIGHT_GREEN)
            sign.add_text(text)

    def draw_tweet_just_in(self, sign):
        sign.add_run_mode(ledsign.EFFECT_SCROLL_UP)
        sign.add_special(ledsign.FONT_5x7)

        sign.add_special(ledsign.COLOUR_RAINBOW3)
        sign.add_special(ledsign.SYMBOL_STARBURST)

        sign.add_special(ledsign.COLOUR_YELLOW)
        sign.add_text("Just In")

        sign.add_special(ledsign.COLOUR_RAINBOW3)
        sign.add_special(ledsign.SYMBOL_STARBURST)

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
                sign.add_run_mode(ledsign.EFFECT_SCROLL_LEFT)

            sign.add_special(ledsign.COLOUR_BRIGHT_GREEN)
            sign.add_special(ledsign.FONT_5x7)
            sign.add_text(bit)

    def draw_message(self, sign, tweet):
        text = tweet.text

        if self.sign_scroll_wait:
            # Scroll one 13 character frame at a time
            for bit in self.split_text(text):
                sign.end_frame()

                sign.add_run_mode(ledsign.EFFECT_SCROLL_LEFT)
                sign.add_special(ledsign.COLOUR_BRIGHT_RED)
                sign.add_special(ledsign.FONT_5x7)
                sign.add_text(bit)
        else:
            # Scroll the whole thing at once
            sign.end_frame()
            sign.add_run_mode(ledsign.EFFECT_SCROLL_LEFT)
            sign.add_special(ledsign.COLOUR_BRIGHT_RED)
            sign.add_special(ledsign.FONT_5x7)
            sign.add_text(text)