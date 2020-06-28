# Twittinator
Displays tweets on an LED sign.

Uses a XC0193 LED matrix sign (with RS232 serial interface) to display tweets 
directed at the Perth Artifactory (`@PerthArtifact`). It also can display other
messages and automatically varies the transitions and animations to keep
things interesting.

It originally ran on a Raspberry Pi. There were two scripts:
* `twitter_parser.py`: to watch for tweets with `tweepy` and write them to file
* ``
