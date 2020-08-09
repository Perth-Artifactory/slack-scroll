from ledsign_micro import *


print("Starting micropython example")

sign = LEDSign(tx_pin=32)

# Begin talking to the sign.  By default, it will be sent to all signs, and
# not do a factory reset on the sign.
#
# You could also set it to send to specific sign by supplying a tuple
# parameter 'sign' (eg:  sign=(1, 2) to send to signs 1 and 2.
#
# A sign will blank out while it is being programmed.
sign.begin_message()

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

# Make the text display immediately
sign.add_run_mode(EFFECT_IMMEDIATE)

# Add the text
sign.add_text("micropython TAZARD")

# End of file.
sign.end_file()

# End message to the signs.  The file will then be "played".
sign.end_message()


