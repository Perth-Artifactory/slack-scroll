#!/usr/bin/env python
"""
Driver for the Bestlink Optoelectronics M500N-7X50R1 / M500N-7X80RG2
Copyright 2010 Michael Farrell <http://micolous.id.au/>

This sign is also sometimes known as XC-0191, XC-0193 or XC-0198 (as sold by
Jaycar and Procon Technology in AU).

Requires pyserial library in order to interface.

This library is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

Tazard 2020-06-14: Modified for micropython running on ESP32.
"""
# from struct import pack
from machine import UART

# Both open and close effects
# cycle through all effects
EFFECT_CYCLIC = 1
EFFECT_IMMEDIATE = 2
EFFECT_SCROLL_LEFT = 3
EFFECT_SCROLL_RIGHT = 4
EFFECT_SPLIT_OPEN = 5
EFFECT_SPLIT_CLOSE = 6
EFFECT_WIPE_OUT = 7
EFFECT_WIPE_LEFT = 8
EFFECT_WIPE_RIGHT = 9
EFFECT_WIPE_IN = 10
EFFECT_SCROLL_UP = 11
EFFECT_SCROLL_DOWN = 12
EFFECT_SPLIT_INTERLACED = 13
EFFECT_WIPE_INTERLACED = 14
EFFECT_WIPE_UP = 15
EFFECT_WIPE_DOWN = 16
EFFECT_WIPE_LINE = 17
EFFECT_EXPLODE = 18
EFFECT_PACMAN = 19
EFFECT_FALLING_LINES = 20
EFFECT_SHOOT = 21
EFFECT_BLINK = 22
EFFECT_DISSOLVE = 23
EFFECT_SLIDE_LETTERS = 24

SYMBOL_STARBURST = b'\x60'
SYMBOL_SNAKE = b'\x61'
SYMBOL_UMBRELLA = b'\x62'
SYMBOL_CLOCK = b'\x63'
SYMBOL_TELEPHONE = b'\x64'
SYMBOL_GLASSES = b'\x65'
SYMBOL_TAP = b'\x66'
SYMBOL_ROCKET = b'\x67'
SYMBOL_CRAB = b'\x68'
SYMBOL_KEY = b'\x69'
SYMBOL_SHIRT = b'\x6A'
SYMBOL_HELECOPTER = b'\x6B'
SYMBOL_CAR = b'\x6C'
SYMBOL_TANK = b'\x6D'
SYMBOL_HOUSE = b'\x6E'
SYMBOL_LANTERN = b'\x6F'
SYMBOL_TREES = b'\x70'
SYMBOL_DUCK = b'\x71'
SYMBOL_SCOOTER = b'\x72'
SYMBOL_BIKE = b'\x73'
SYMBOL_CROWN = b'\x74'
SYMBOL_BUTTERFLY = b'\x75'
SYMBOL_RIGHT = b'\x76'
SYMBOL_LEFT = b'\x77'
SYMBOL_DOWN_LEFT = b'\x78'
SYMBOL_UP_LEFT = b'\x79'
SYMBOL_CUP = b'\x7A'
SYMBOL_CHAIR = b'\x7B'
SYMBOL_SHOE = b'\x7C'
SYMBOL_MARTINI = b'\x7D'

SPECIAL_TIME = b'\x80'
SPECIAL_DATE = b'\x81'

# requires the larger version of the sign to display properly
# still exists in the small version.
ANIMATION_MERRY_XMAS = b'\x90'
ANIMATION_HAPPY_NEW_YEAR = b'\x91'
ANIMATION_4TH_JULY = b'\x92'
ANIMATION_HAPPY_EASTER = b'\x93'
ANIMATION_HAPPY_HALLOWEEN = b'\x94'
ANIMATION_DONT_DRINK_DRIVE = b'\x95'
ANIMATION_NO_SMOKING = b'\x96'
ANIMATION_WELCOME = b'\x97'
# extra undocumented copy of the graphics here, \x98 - \x9F

FONT_5x5 = b'\xA0'
FONT_10x5 = b'\xA1'
FONT_5x7 = b'\xA2'
FONT_10x7 = b'\xA3'
FONT_8x7 = b'\xA4'
FONT_16x7 = b'\xA5'
FONT_SMALL_FONTS = b'\xA6'
# broken extra fonts
FONT_3x7 = b'\xAC'

COLOUR_BRIGHT_RED = b'\xB0'
COLOUR_DIM_RED = b'\xB1'
# additional colours for M500N-7X80RG2 (Red/Green 2-LED version)
# thanks to Martin Hill <martin at eshock.com>
COLOUR_AMBER = b'\xB2'
COLOUR_YELLOW = b'\xB3'
COLOUR_DIM_ORANGE = b'\xB4'
COLOUR_BRIGHT_ORANGE = b'\xB5'
COLOUR_DIM_GREEN = b'\xB6'
COLOUR_BRIGHT_GREEN = b'\xB7'
COLOUR_RAINBOW1 = b'\xB8'
COLOUR_RAINBOW2 = b'\xB9'
COLOUR_RAINBOW3 = b'\xBA'
COLOUR_RAINBOW4 = b'\xBB'
COLOUR_RAINBOW5 = b'\xBC'
COLOUR_RAINBOW6 = b'\xBD'
COLOUR_RAINBOW7 = b'\xBE'
COLOUR_RAINBOW8 = b'\xBF'

# fastest speed is 1, slowest is 8
SPEED_1 = b'\xC0'
SPEED_2 = b'\xC1'
SPEED_3 = b'\xC2'
SPEED_4 = b'\xC3'
SPEED_5 = b'\xC4'
SPEED_6 = b'\xC5'
SPEED_7 = b'\xC6'
SPEED_8 = b'\xC7'

# fastest pause time is 1, slowest is 8
PAUSE_1 = b'\xC8'
PAUSE_2 = b'\xC9'
PAUSE_3 = b'\xCA'
PAUSE_4 = b'\xCB'
PAUSE_5 = b'\xCC'
PAUSE_6 = b'\xCD'
PAUSE_7 = b'\xCE'
PAUSE_8 = b'\xCF'

# TODO: implement programming custom graphics
GRAPHIC_CUSTOM_1 = b'\xD0'
GRAPHIC_CUSTOM_2 = b'\xD1'
GRAPHIC_CUSTOM_3 = b'\xD2'
GRAPHIC_CUSTOM_4 = b'\xD3'
GRAPHIC_CUSTOM_5 = b'\xD4'
GRAPHIC_CUSTOM_6 = b'\xD5'
GRAPHIC_CUSTOM_7 = b'\xD6'
GRAPHIC_CUSTOM_8 = b'\xD7'
# Multiple interpretations of the graphics here.
# Trains, teacups, beach and mouse is what I thought they were.
# I've updated it so it has the "official names" of these graphics from the
# manual as well, but not break the API.
GRAPHIC_CITY = GRAPHIC_TRAINS = b'\xD8'
GRAPHIC_CARS = b'\xD9'
GRAPHIC_VESSEL = GRAPHIC_TEACUPS = b'\xDA'
GRAPHIC_TELEPHONE = b'\xDB'
GRAPHIC_NATURE = GRAPHIC_BEACH = b'\xDC'
GRAPHIC_SHIP = b'\xDD'
GRAPHIC_SWIM = b'\xDE'
GRAPHIC_CAT = GRAPHIC_MOUSE = b'\xDF'

SOUND_BEEP_3 = b'\xE0'
SOUND_BEEP_5 = b'\xE1'
SOUND_BEEP_1 = b'\xE2'


class LEDSign:
    """Implementation of the XC0193 LED Matrix Sign protocol"""
    SIGN_UART = 2
    BAUD_RATE = 2400
    # UART_SIGNAL_TXD_INV = (0x1 << 5)

    def __init__(self, tx_pin):
        # self.s = serial.Serial(port, 2400)
        self.tx_pin = tx_pin
        self.s = UART(self.SIGN_UART)
        self.s.init(baudrate=self.BAUD_RATE, tx=self.tx_pin, invert=UART.INV_TX)
        self.file_id = None
        self.message_open = False
        print("Opening UART {} with TX on pin {}".format(self.SIGN_UART, self.tx_pin))

    def send_to_sign(self, msg):
        byte_string = " ".join("{:02x}".format(c) for c in msg)
        print('Send: {} = "{}"'.format(msg, byte_string))
        # print(bytes(msg)[0])
        self.s.write(msg)

    def begin_message(self, sign=list(range(0, 128)), reset=False):
        """Begins a message for a sign.  defaults to all signs."""
        if self.message_open:
            raise Exception("A message is already open")

        try:
            if len(sign) == 1:
                sign = sign[0]
        except TypeError:
            pass

        if type(sign) == int:
            # we're only programming a single sign.
            # we can optimise!
            if sign < 0 or sign > 127:
                raise Exception("cannot send to sign ID outside of range 0-127, you sent to sign %s" % sign)

            # TODO: check whether this should be little or big endian properly.
            # the manual isn't really clear on this.  so lets take a stab in the dark.

            self.send_to_sign(b"\x00" + bytes(sign) + bytes(sign))

            if reset:
                self.send_to_sign(b"\x01")
            else:
                self.send_to_sign(b"\x00")

        # we're done...

        else:
            # this is a list with multiple members:
            for x in sign:
                if x < 0 or x > 127:
                    raise Exception("cannot send to sign ID outside of range 0-127, you sent to sign %s" % x)

            # this is a special thing, doesn't have the \xFF terminator
            # start programming the sign, do not reset memory
            self.send_to_sign(b"\x00\xFF\xFF")
            if reset:
                self.send_to_sign(b"\x01")
            else:
                self.send_to_sign(b"\x00")

            # # data is for sign list
            # self.send_to_sign("\x0B")
            #
            # if sign == range(0, 128):
            #     # we're sending data to everyone.
            #     # TODO: test that this actually works
            #     self.send_to_sign('\xFF')
            # else:
            #     for x in sign:
            #         self.send_to_sign(chr(x))
            # self.send_to_sign('\xFF')

        self.message_open = True

    def add_run_mode(self, mode=1):
        if mode < 0 or mode > 24:
            raise Exception("run mode must be 0-24")

        self.send_to_sign(bytes(mode))

    def add_text(self, msg):
        """Add text given as unicode string (sign can only render ascii characters)"""
        # The sign can take ascii text
        msg = msg.encode('ascii')
        for x in msg:
            y = x
            if y < 32 or y > 237:
                raise Exception("You shouldn't be using the character %s (#%x)." % (x, x))
        self.send_to_sign(msg)

    def add_special(self, special):
        self.send_to_sign(b"\xEF" + bytes(special))

    def end_frame(self):
        self.send_to_sign(b'\xff')

    def end_message(self):
        if not self.message_open:
            raise Exception("A message isn't open")
        # this is a special thing, doesn't have the \xFF terminator
        self.send_to_sign(b"\x00")
        self.message_open = False

    def begin_file(self, file_id):
        if self.file_id is not None:
            raise Exception("A file, %s, is already open" % self.file_id)
        file_id = int(file_id)
        if file_id < 0 or file_id > 99:
            raise Exception("file_id must be between 0 and 99.")

        self.send_to_sign(b"\x01%02d" % file_id)
        self.file_id = file_id

    def end_file(self):
        if self.file_id is None:
            raise Exception("No file is open")
        self.send_to_sign(b"\xFF\xFF")
        self.file_id = None

    def display_page(self, pageid):
        pass

    def playlist(self, page_order):
        pass

    def close(self):
        self.s.close()
