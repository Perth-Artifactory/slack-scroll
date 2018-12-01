import json
import os
import random
from datetime import datetime
import re


class Tweet(object):
    def __init__(self, j, user, screen_name, text, created_at, timestamp_ms):
        self.j = j
        self.user = self.clean_ascii(user)
        self.screen_name = self.clean_ascii(screen_name)
        self.text = self.clean_ascii(text)
        self.created_at = self.clean_ascii(created_at)
        self.timestamp_ms = self.clean_ascii(timestamp_ms)

    @staticmethod
    def clean_ascii(text):
        return ''.join([i if ord(i) < 128 else '_' for i in text])

    @classmethod
    def from_twitter(cls, data_text, block_list, replacement_list):
        """Create Tweet object from twitter json text"""
        j = json.loads(data_text)

        user = j["user"]["name"]
        screen_name = j["user"]["screen_name"]
        text = j["text"]
        created_at = j["created_at"]
        timestamp_ms = j["timestamp_ms"]

        def get_replacement_word(bad_word):
            """Try to return a replacement word that matches first letter of block word, otherwise return any"""
            # See if any replacement words match the first letter of block word
            matching = filter(lambda x: x[0] == bad_word[0], replacement_list)

            if len(matching) == 0:
                # No match, so widen search back to all replacement works
                matching = replacement_list

            # Pick a random word from list
            return random.choice(matching)

        # Apply block word list to produce clean text
        for block_word in block_list:
            if block_word in text.lower().split(" "):
                # text = text.replace(block_word, get_replacement_word(block_word))
                # text = text.replace(block_word, ";)")

                # Replace case insensitive
                # https://stackoverflow.com/questions/919056/case-insensitive-replace
                replace_word = get_replacement_word(block_word)
                replace_re = re.compile(re.escape(block_word), re.IGNORECASE)
                text = replace_re.sub(replace_word, text)

        # TODO: Replace any other special characters

        # Create the tweet
        return Tweet(j=j, user=user, screen_name=screen_name, text=text,
                     created_at=created_at, timestamp_ms=timestamp_ms)

    @classmethod
    def from_file(cls, file_name):
        """Create Tweet object from JSON file"""
        with open(file_name) as f:
            j = json.load(f)

        return cls(j=j["twitter_json"], user=j["user"], screen_name=j["screen_name"], text=j["text"],
                   created_at=j["created_at"], timestamp_ms=j["timestamp_ms"])

    def save_to_file(self, file_name):
        """Write this tweet object to file as a JSON"""
        j = {
            'twitter_json': self.j,
            'user': self.user,
            'screen_name': self.screen_name,
            'text': self.text,
            'created_at': self.created_at,
            'timestamp_ms': self.timestamp_ms,
        }

        # Put datetime in filename
        ts_seconds = float(self.timestamp_ms) / 1000.0
        file_name = file_name.format(datetime.fromtimestamp(ts_seconds).strftime('%Y%m%d_%H%M%S.%f'))
        print("Saving tweet to: {}".format(file_name))
        dir_name = os.path.dirname(file_name)
        if not os.path.exists(dir_name):
            print("Creating directory: {}".format(dir_name))
            os.makedirs(dir_name)
        with open(file_name, 'w') as f:
            # Pretty dump it to file
            json.dump(j, f, sort_keys=True, indent=4, separators=(',', ': '))

    def __str__(self):
        json.dumps(self.j, sort_keys=True, indent=4, separators=(',', ': '))
