# SPDX-FileCopyrightText: 2023 DJDevon3
# SPDX-License-Identifier: MIT
# Started as ESP32-S3 Feather Weather MQTT Touchscreen
# Coded for Circuit Python 8.2.x
# Modified for SoftKeyboard by Tim C

import time
import board
import displayio
import terminalio
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font
import adafruit_touchscreen
from soft_keyboard.soft_keyboard import SoftKeyboard, PRINTABLE_CHARACTERS

_now = time.monotonic()

DISPLAY_WIDTH = 480
DISPLAY_HEIGHT = 320

_touch_flip = (False, True)

# Initialize 3.5" TFT Featherwing Touchscreen
# ts_cs_pin = digitalio.DigitalInOut(board.D6)
# touchscreen = adafruit_stmpe610.Adafruit_STMPE610_SPI(
#     board.SPI(),
#     ts_cs_pin,
#     calibration=((231, 3703), (287, 3787)),
#     size=(display.width, display.height),
#     disp_rotation=display.rotation,
#     touch_flip=_touch_flip,
# )


print("Init touchscreen")
# pylint: disable=no-member
touchscreen = adafruit_touchscreen.Touchscreen(
    board.TOUCH_XL,
    board.TOUCH_XR,
    board.TOUCH_YD,
    board.TOUCH_YU,
    calibration=((6856, 60565), (9337, 56924)),
    size=(board.DISPLAY.width, board.DISPLAY.height),
)


def _format_date(datetime):
    return "{:02}/{:02}/{:02}".format(
        datetime.tm_year,
        datetime.tm_mon,
        datetime.tm_mday,
    )


def _format_time(datetime):
    return "{:02}:{:02}".format(
        datetime.tm_hour,
        datetime.tm_min,
        # datetime.tm_sec,
    )


# Quick Colors for Labels
TEXT_BLACK = 0x000000
TEXT_BLUE = 0x0000FF
TEXT_CYAN = 0x00FFFF
TEXT_GRAY = 0x8B8B8B
TEXT_GREEN = 0x00FF00
TEXT_LIGHTBLUE = 0x90C7FF
TEXT_MAGENTA = 0xFF00FF
TEXT_ORANGE = 0xFFA500
TEXT_PURPLE = 0x800080
TEXT_RED = 0xFF0000
TEXT_WHITE = 0xFFFFFF
TEXT_YELLOW = 0xFFFF00

forkawesome_font = bitmap_font.load_font("/fonts/forkawesome-12.pcf")

input_lbl = label.Label(
    terminalio.FONT, scale=2, text="", color=0xFFFFFF, background_color=0x00000
)
input_lbl.x = 10
input_lbl.y = 10

# Create subgroups
splash = displayio.Group()
text_group = displayio.Group()
main_group = displayio.Group()

main_group.append(input_lbl)
board.DISPLAY.root_group = main_group

soft_kbd = SoftKeyboard(
    2, 100, DISPLAY_WIDTH - 2, DISPLAY_HEIGHT - 100, terminalio.FONT, forkawesome_font
)

main_group.append(soft_kbd)

print(f"size: {soft_kbd.width}, {soft_kbd.height}")
print(f"cell size: {soft_kbd.layout.cell_size_pixels}")

while True:
    p = touchscreen.touch_point

    # print(p)
    key_value = soft_kbd.check_touches(p)
    if key_value in PRINTABLE_CHARACTERS:
        input_lbl.text += key_value
    elif key_value == 42:  # 0x2a backspace key
        input_lbl.text = input_lbl.text[:-1]
