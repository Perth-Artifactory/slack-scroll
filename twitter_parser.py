"""
Script to read twitter API and dump tweets to disk for led sign and other services to pick up

Python 2.7. Should be python 3 compatible.
"""

from __future__ import print_function
import json
import sys
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
from tweet import Tweet
import requests
import time


class Listener(StreamListener):
    def __init__(self, tweet_path, block_list, replacement_list):
        super(Listener, self).__init__()
        self.block_list = block_list
        self.replacement_list = replacement_list
        self.tweet_path = tweet_path

    def on_data(self, data):
        # Load tweet using Tweet object
        tweet = Tweet.from_twitter(data_text=data, block_list=self.block_list, replacement_list=self.replacement_list)
        print("User: {tweet.user}, Screen Name: {tweet.screen_name}".format(tweet=tweet))
        print(" Created at: {tweet.created_at}, Timestamp_ms: {tweet.timestamp_ms}".format(tweet=tweet))
        print(" Text: {tweet.text}".format(tweet=tweet))

        # Now dump to disk for services to pick up
        tweet.save_to_file(self.tweet_path)

        return True

    def on_error(self, status):
        print(status)


def load_word_list(path):
    """Load the block or replace word lists. Line separated list of words"""
    with open(path) as f:
        word_list = f.readlines()

    word_list = map(lambda x: x.strip(' \n\r'), word_list)
    word_list = filter(lambda x: len(x) > 0, word_list)

    return word_list


def main(args):
    print("Artifactory Twittinator - Twitter Parser")

    if len(args) != 1:
        print("Requires exactly one argument as path to config")
        sys.exit(1)

    print("Loading config")
    config_path = args[0]
    with open(config_path) as f:
        j_config = json.load(f)

    tweet_path = j_config["tweet_path"]
    twitter_address = j_config["twitter_address"]
    twitter_api = j_config["twitter_api"]
    block_list_path = j_config["block_list_path"]
    replace_list_path = j_config["replace_list_path"]

    print("Setting auth")
    auth = OAuthHandler(twitter_api["ckey"], twitter_api["csecret"])
    auth.set_access_token(twitter_api["atoken"], twitter_api["asecret"])

    print("Loading block and replacement lists")
    block_list = load_word_list(block_list_path)
    replace_list = load_word_list(replace_list_path)

    print("Creating listener")
    listener = Listener(block_list=block_list, replacement_list=replace_list, tweet_path=tweet_path)

    print("Setting up stream tweets")
    twitter_stream = Stream(auth, listener)

    while True:
        try:
            twitter_stream.filter(track=twitter_address)
        except requests.exceptions.ConnectionError as e:
            print("ERROR: {}".format(e))
            time.sleep(5.0)


if __name__ == "__main__":
    main(sys.argv[1:])
