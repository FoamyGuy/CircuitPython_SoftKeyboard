# SPDX-FileCopyrightText: 2023 DJDevon3
# SPDX-License-Identifier: MIT
import board
import displayio
import digitalio
import terminalio
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font
from adafruit_hx8357 import HX8357
import adafruit_stmpe610
from soft_keyboard.soft_keyboard import SoftKeyboard, PRINTABLE_CHARACTERS

# 3.5" TFT Featherwing V1 is 480x320
displayio.release_displays()
DISPLAY_WIDTH = 480
DISPLAY_HEIGHT = 320

# Initialize TFT Display
spi = board.SPI()
tft_cs = board.D9
tft_dc = board.D10
display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs)
display = HX8357(display_bus, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT)
display.rotation = 0
_touch_flip = (False, True)

# Initialize 3.5" TFT Featherwing Touchscreen
ts_cs_pin = digitalio.DigitalInOut(board.D6)
touchscreen = adafruit_stmpe610.Adafruit_STMPE610_SPI(
    board.SPI(),
    ts_cs_pin,
    calibration=((231, 3703), (287, 3787)),
    size=(display.width, display.height),
    disp_rotation=display.rotation,
    touch_flip=_touch_flip,
)

forkawesome_font = bitmap_font.load_font("/fonts/forkawesome-12.pcf")

input_lbl = label.Label(
    terminalio.FONT, scale=2, text="", color=0xFFFFFF, background_color=0x00000
)
input_lbl.x = 10
input_lbl.y = 10

# Create groups
main_group = displayio.Group()
main_group.append(input_lbl)

display.root_group = main_group
soft_kbd = SoftKeyboard(
    2,
    100,
    DISPLAY_WIDTH - 2,
    DISPLAY_HEIGHT - 100,
    terminalio.FONT,
    forkawesome_font,
    layout_config="mobile_layout.json",
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
