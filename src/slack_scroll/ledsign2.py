"""
LED Sign Driver - XC0193/M500N Protocol

Original implementation by Michael Farrell (LGPL-3.0)
Adapted for Slack Scroll project.
"""

import serial
from datetime import datetime
from struct import pack

# Effects
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

# Symbols
SYMBOL_STARBURST = b"\x60"
SYMBOL_SNAKE = b"\x61"
SYMBOL_UMBRELLA = b"\x62"
SYMBOL_CLOCK = b"\x63"
SYMBOL_TELEPHONE = b"\x64"
SYMBOL_GLASSES = b"\x65"
SYMBOL_TAP = b"\x66"
SYMBOL_ROCKET = b"\x67"
SYMBOL_CRAB = b"\x68"
SYMBOL_KEY = b"\x69"
SYMBOL_SHIRT = b"\x6a"
SYMBOL_HELECOPTER = b"\x6b"
SYMBOL_CAR = b"\x6c"
SYMBOL_TANK = b"\x6d"
SYMBOL_HOUSE = b"\x6e"
SYMBOL_LANTERN = b"\x6f"
SYMBOL_TREES = b"\x70"
SYMBOL_DUCK = b"\x71"
SYMBOL_SCOOTER = b"\x72"
SYMBOL_BIKE = b"\x73"
SYMBOL_CROWN = b"\x74"
SYMBOL_BUTTERFLY = b"\x75"
SYMBOL_RIGHT = b"\x76"
SYMBOL_LEFT = b"\x77"
SYMBOL_DOWN_LEFT = b"\x78"
SYMBOL_UP_LEFT = b"\x79"
SYMBOL_CUP = b"\x7a"
SYMBOL_CHAIR = b"\x7b"
SYMBOL_SHOE = b"\x7c"
SYMBOL_MARTINI = b"\x7d"

SPECIAL_TIME = b"\x80"
SPECIAL_DATE = b"\x81"

# Animations
ANIMATION_MERRY_XMAS = b"\x90"
ANIMATION_HAPPY_NEW_YEAR = b"\x91"
ANIMATION_4TH_JULY = b"\x92"
ANIMATION_HAPPY_EASTER = b"\x93"
ANIMATION_HAPPY_HALLOWEEN = b"\x94"
ANIMATION_DONT_DRINK_DRIVE = b"\x95"
ANIMATION_NO_SMOKING = b"\x96"
ANIMATION_WELCOME = b"\x97"

# Fonts
FONT_5x5 = b"\xa0"
FONT_10x5 = b"\xa1"
FONT_5x7 = b"\xa2"
FONT_10x7 = b"\xa3"
FONT_8x7 = b"\xa4"
FONT_16x7 = b"\xa5"
FONT_SMALL_FONTS = b"\xa6"
FONT_3x7 = b"\xac"

# Colors
COLOUR_BRIGHT_RED = b"\xb0"
COLOUR_DIM_RED = b"\xb1"
COLOUR_AMBER = b"\xb2"
COLOUR_YELLOW = b"\xb3"
COLOUR_DIM_ORANGE = b"\xb4"
COLOUR_BRIGHT_ORANGE = b"\xb5"
COLOUR_DIM_GREEN = b"\xb6"
COLOUR_BRIGHT_GREEN = b"\xb7"
COLOUR_RAINBOW1 = b"\xb8"
COLOUR_RAINBOW2 = b"\xb9"
COLOUR_RAINBOW3 = b"\xba"
COLOUR_RAINBOW4 = b"\xbb"
COLOUR_RAINBOW5 = b"\xbc"
COLOUR_RAINBOW6 = b"\xbd"
COLOUR_RAINBOW7 = b"\xbe"
COLOUR_RAINBOW8 = b"\xbf"

# Speeds
SPEED_1 = b"\xc0"
SPEED_2 = b"\xc1"
SPEED_3 = b"\xc2"
SPEED_4 = b"\xc3"
SPEED_5 = b"\xc4"
SPEED_6 = b"\xc5"
SPEED_7 = b"\xc6"
SPEED_8 = b"\xc7"

# Pauses
PAUSE_1 = b"\xc8"
PAUSE_2 = b"\xc9"
PAUSE_3 = b"\xca"
PAUSE_4 = b"\xcb"
PAUSE_5 = b"\xcc"
PAUSE_6 = b"\xcd"
PAUSE_7 = b"\xce"
PAUSE_8 = b"\xcf"

# Graphics
GRAPHIC_CUSTOM_1 = b"\xd0"
GRAPHIC_CUSTOM_2 = b"\xd1"
GRAPHIC_CUSTOM_3 = b"\xd2"
GRAPHIC_CUSTOM_4 = b"\xd3"
GRAPHIC_CUSTOM_5 = b"\xd4"
GRAPHIC_CUSTOM_6 = b"\xd5"
GRAPHIC_CUSTOM_7 = b"\xd6"
GRAPHIC_CUSTOM_8 = b"\xd7"
GRAPHIC_CITY = GRAPHIC_TRAINS = b"\xd8"
GRAPHIC_CARS = b"\xd9"
GRAPHIC_VESSEL = GRAPHIC_TEACUPS = b"\xda"
GRAPHIC_TELEPHONE = b"\xdb"
GRAPHIC_NATURE = GRAPHIC_BEACH = b"\xdc"
GRAPHIC_SHIP = b"\xdd"
GRAPHIC_SWIM = b"\xde"
GRAPHIC_CAT = GRAPHIC_MOUSE = b"\xdf"

# Sounds
SOUND_BEEP_3 = b"\xe0"
SOUND_BEEP_5 = b"\xe1"
SOUND_BEEP_1 = b"\xe2"


class LEDSign:
    """LED Sign controller for XC0193 protocol."""

    def __init__(self, port: str):
        self.s = serial.Serial(port, 2400)
        self.file_id = None
        self.message_open = False

    def send_to_sign(self, msg: bytes) -> None:
        byte_string = " ".join("{:02x}".format(c) for c in msg)
        print(f'Send: {msg} = "{byte_string}"')
        self.s.write(msg)

    def begin_message(self, sign: list = None, reset: bool = False) -> None:
        if sign is None:
            sign = list(range(0, 128))

        if self.message_open:
            raise RuntimeError("A message is already open")

        if isinstance(sign, int):
            if sign < 0 or sign > 127:
                raise ValueError(f"Sign ID must be 0-127, got {sign}")

            self.send_to_sign(b"\x00" + bytes([sign]) + bytes([sign]))
            self.send_to_sign(b"\x01" if reset else b"\x00")
        else:
            for x in sign:
                if x < 0 or x > 127:
                    raise ValueError(f"Sign ID must be 0-127, got {x}")

            self.send_to_sign(b"\x00\xff\xff")
            self.send_to_sign(b"\x01" if reset else b"\x00")

        self.message_open = True

    def add_run_mode(self, mode: int = 1) -> None:
        if mode < 0 or mode > 24:
            raise ValueError(f"Run mode must be 0-24, got {mode}")
        self.send_to_sign(bytes([mode]))

    def add_text(self, msg: str) -> None:
        encoded = msg.encode("ascii")
        for x in encoded:
            if x < 32 or x > 237:
                raise ValueError(f"Invalid character: {chr(x)} (#{x})")
        self.send_to_sign(encoded)

    def add_special(self, special: bytes) -> None:
        self.send_to_sign(b"\xef" + special)

    def end_frame(self) -> None:
        self.send_to_sign(b"\xff")

    def end_message(self) -> None:
        if not self.message_open:
            raise RuntimeError("No message is open")
        self.send_to_sign(b"\x00")
        self.message_open = False

    def set_clock(self, n: datetime = None, hour24: bool = True) -> None:
        if self.file_id is not None:
            raise RuntimeError("Cannot set clock while file is open")

        if n is None:
            n = datetime.now()

        hour_byte = b"\x00" if hour24 else b"\x01"
        args = (
            pack("!B", n.isoweekday() % 7),
            hour_byte,
            n.year % 100,
            n.month,
            n.day,
            n.hour,
            n.minute,
            n.second,
        )
        self.send_to_sign((b"\x08%s%s" + (b"%02d" * 6) + b"\xff") % args)

    def begin_file(self, file_id: int) -> None:
        if self.file_id is not None:
            raise RuntimeError(f"File {self.file_id} is already open")

        file_id = int(file_id)
        if file_id < 0 or file_id > 99:
            raise ValueError(f"File ID must be 0-99, got {file_id}")

        self.send_to_sign(b"\x01%02d" % file_id)
        self.file_id = file_id

    def end_file(self) -> None:
        if self.file_id is None:
            raise RuntimeError("No file is open")
        self.send_to_sign(b"\xff\xff")
        self.file_id = None

    def display_page(self, pageid: int) -> None:
        pass

    def playlist(self, page_order: list) -> None:
        pass

    def close(self) -> None:
        self.s.close()
