import random
import ledsign2 as sign_lib

PORT = "COM13"

print("LED Sign Test")

# Open a connection to the sign.  you'll need to change the device node
# here if you're not using a USB-Serial converter.  If you have an
# actual serial port, use /dev/ttyS0 instead for COM1.  If you're on Windows,
# use "COM1" or whatever the port's name is.  You can also set it to a
# numeric value starting at 0 (ie: open the first serial port).
#
sign = sign_lib.LEDSign(PORT)

# Begin talking to the sign.  By default, it will be sent to all signs, and
# not do a factory reset on the sign.
#
# You could also set it to send to specific sign by supplying a tuple
# parameter 'sign' (eg:  sign=(1, 2) to send to signs 1 and 2.
#
# A sign will blank out while it is being programmed.
sign.begin_message(reset=True)

# Set the device's clock to the computer's time.  You can also use the
# parameter 'n' to set it to an arbitrary time (in a datetime.datetime object).
#
# The hour24 parameter indicates whether to use 24 hour time.
# Defaults to True.
# sign.set_clock()

# Begin data for file 1.  File numbers are between 1 and 99.
# While you are writing a file, you can only add data to that file.  Some
# special commands (like setting the clock) are not available while a file
# is being sent.
sign.begin_file(1)

# A file structure consists of a run mode (optionally), followed by some text.
# You can also end a "frame" and add another run mode and add some more text.
# So you could have it go:
#
#  1) Add Run mode EFFECT_IMMEDIATE
#  2) Add Special  SPEED_8
#  3) Add Special  SPECIAL_TIME
#  4) End frame
#  5) Add Run mode EFFECT_SCROLL_LEFT
#  6) Add Text     "Sunny, 24C"
#
# This would make the sign display the time for a few seconds, then "Sunny,
# 24C".  In reality you would make it get the weather from another data
# source though.

transitions_to_title = [
    sign_lib.EFFECT_SPLIT_OPEN,
    sign_lib.EFFECT_WIPE_DOWN,
    sign_lib.EFFECT_FALLING_LINES,
]

sign.add_run_mode(sign_lib.EFFECT_SCROLL_UP)
sign.add_special(sign_lib.FONT_5x5)
sign.add_special(sign_lib.COLOUR_RAINBOW2)
sign.add_text("Artifactory")

sign.end_frame()

sign.add_run_mode(random.choice(transitions_to_title))
sign.add_special(sign_lib.FONT_5x5)
sign.add_special(sign_lib.COLOUR_RAINBOW1)
sign.add_text("Twittinator")

# sign.end_frame()

# sign.add_run_mode(sign_lib.EFFECT_SCROLL_LEFT)
# sign.add_special(sign_lib.COLOUR_BRIGHT_GREEN)
# sign.add_special(sign_lib.FONT_5x7)
# # sign.add_special(sign_lib.SPEED_2)
# sign.add_text("@tazillian says: ")
# sign.add_special(sign_lib.PAUSE_1)
# # sign.add_run_mode(sign_lib.EFFECT_SCROLL_LEFT)
# sign.add_special(sign_lib.COLOUR_BRIGHT_RED)
# # sign.add_special(sign_lib.SPEED_8)
# sign.add_text("@artifactorytest tweeting tester")


transitions_to_tweet = [
    sign_lib.EFFECT_SPLIT_OPEN,
    sign_lib.EFFECT_SPLIT_CLOSE,
    sign_lib.EFFECT_WIPE_OUT,
    sign_lib.EFFECT_WIPE_RIGHT,
    sign_lib.EFFECT_WIPE_IN,
    sign_lib.EFFECT_SPLIT_INTERLACED,
    sign_lib.EFFECT_WIPE_INTERLACED,
    sign_lib.EFFECT_WIPE_UP,
    sign_lib.EFFECT_EXPLODE,
    sign_lib.EFFECT_PACMAN,
    sign_lib.EFFECT_PACMAN,
    sign_lib.EFFECT_PACMAN,
    sign_lib.EFFECT_SHOOT,
    sign_lib.EFFECT_DISSOLVE,
    sign_lib.EFFECT_SLIDE_LETTERS,
]

for _ in range(2):
    sign.end_frame()

    sign.add_run_mode(sign_lib.EFFECT_SCROLL_UP)
    sign.add_special(sign_lib.FONT_5x7)

    sign.add_special(sign_lib.COLOUR_RAINBOW4)
    sign.add_special(sign_lib.SYMBOL_STARBURST)

    sign.add_special(sign_lib.COLOUR_BRIGHT_ORANGE)
    sign.add_text("Tweet")

    sign.add_special(sign_lib.COLOUR_RAINBOW4)
    sign.add_special(sign_lib.SYMBOL_STARBURST)

    sign.end_frame()

    sign.add_run_mode(random.choice(transitions_to_tweet))
    sign.add_special(sign_lib.COLOUR_BRIGHT_GREEN)
    sign.add_special(sign_lib.FONT_5x7)
    sign.add_text("@tazillian:  ")

    sign.end_frame()

    sign.add_run_mode(sign_lib.EFFECT_SCROLL_LEFT)
    sign.add_special(sign_lib.COLOUR_BRIGHT_RED)
    sign.add_special(sign_lib.FONT_5x7)
    sign.add_text("the tweet  ! ")




# sign.add_run_mode(sign_lib.EFFECT_SCROLL_UP)
# sign.add_special(sign_lib.COLOUR_BRIGHT_GREEN)
# sign.add_special(sign_lib.FONT_5x7)
# # sign.add_special(sign_lib.SPEED_2)
# sign.add_text("@tazillian:  ")
#
# sign.add_special(sign_lib.PAUSE_1)
# # sign.end_frame()
#
# sign.add_run_mode(sign_lib.EFFECT_SCROLL_LEFT)
# sign.add_special(sign_lib.COLOUR_BRIGHT_RED)
# # sign.add_special(sign_lib.SPEED_8)
# sign.add_text("@artifactory ")
#
# sign.end_frame()
#
# sign.add_run_mode(sign_lib.EFFECT_SCROLL_LEFT)
# sign.add_text("test tweeting")
#
# sign.end_frame()
#
# sign.add_run_mode(sign_lib.EFFECT_SCROLL_LEFT)
# sign.add_text("tester       ")



# sign.add_run_mode(sign_lib.EFFECT_IMMEDIATE)
# sign.add_special(sign_lib.SYMBOL_STARBURST)
# sign.add_special(sign_lib.SYMBOL_SNAKE)
# sign.add_special(sign_lib.SYMBOL_UMBRELLA)
# sign.add_special(sign_lib.SYMBOL_CLOCK)
#
# sign.end_frame()

# sign.add_run_mode(sign_lib.EFFECT_IMMEDIATE)
# sign.add_special(sign_lib.SYMBOL_TELEPHONE)
# sign.add_special(sign_lib.SYMBOL_GLASSES)
# sign.add_special(sign_lib.SYMBOL_TAP)
# sign.add_special(sign_lib.SYMBOL_ROCKET)

# sign.end_frame()
#
# sign.add_run_mode(sign_lib.EFFECT_IMMEDIATE)
# sign.add_special(sign_lib.SYMBOL_CRAB)
# sign.add_special(sign_lib.SYMBOL_KEY)
# sign.add_special(sign_lib.SYMBOL_SHIRT)
# sign.add_special(sign_lib.SYMBOL_HELECOPTER)

# sign.end_frame()
#
# sign.add_run_mode(sign_lib.EFFECT_IMMEDIATE)
# sign.add_special(sign_lib.SYMBOL_TANK)
# sign.add_special(sign_lib.SYMBOL_HOUSE)
# sign.add_special(sign_lib.SYMBOL_LANTERN)
# sign.add_special(sign_lib.SYMBOL_TREES)

# sign.end_frame()
#
# sign.add_run_mode(sign_lib.EFFECT_IMMEDIATE)
# sign.add_special(sign_lib.SYMBOL_DUCK)
# sign.add_special(sign_lib.SYMBOL_SCOOTER)
# sign.add_special(sign_lib.SYMBOL_BIKE)
# sign.add_special(sign_lib.SYMBOL_CROWN)

# sign.end_frame()
#
# sign.add_run_mode(sign_lib.EFFECT_IMMEDIATE)
# sign.add_special(sign_lib.SYMBOL_BUTTERFLY)
# sign.add_special(sign_lib.SYMBOL_RIGHT)
# sign.add_special(sign_lib.SYMBOL_LEFT)
# sign.add_special(sign_lib.SYMBOL_DOWN_LEFT)

# sign.end_frame()
#
# sign.add_run_mode(sign_lib.EFFECT_IMMEDIATE)
# sign.add_special(sign_lib.SYMBOL_UP_LEFT)
# sign.add_special(sign_lib.SYMBOL_CUP)
# sign.add_special(sign_lib.SYMBOL_CHAIR)
# sign.add_special(sign_lib.SYMBOL_SHOE)

# sign.end_frame()
#
# sign.add_run_mode(sign_lib.EFFECT_IMMEDIATE)
# sign.add_special(sign_lib.SYMBOL_MARTINI)
# sign.add_special(sign_lib.SPECIAL_TIME)
# sign.add_special(sign_lib.SPECIAL_DATE)
#
# sign.end_frame()

# sign.add_special(sign_lib.ANIMATION_WELCOME)

# sign.add_run_mode(sign_lib.EFFECT_IMMEDIATE)
# sign.add_special(sign_lib.GRAPHIC_CAT)
# sign.add_special(sign_lib.SOUND_BEEP_1)

# End of file.
sign.end_file()

# End message to the signs.  The file will then be "played".
sign.end_message()
