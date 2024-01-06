import json
import time

from displayio import Group
from adafruit_display_text import label
from adafruit_displayio_layout.layouts.grid_layout import GridLayout
from adafruit_bitmap_font import bitmap_font

PRINTABLE_CHARACTERS = (
    "`", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "=",
    "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "",
    "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "a", "b", "c", "d", "e",
    "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "",
    "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", ",", ".", "/", "\\", "'",
    "[", "]", ";", " "
)


# Function for minimizing labels to 1 liners
# Attribution: Anecdata (thanks!)
def make_my_label(font, anchor_point, anchored_position, scale, color):
    func_label = label.Label(font)
    func_label.anchor_point = anchor_point
    func_label.anchored_position = anchored_position
    func_label.scale = scale
    func_label.color = color
    return func_label


class SoftKeyboard(Group):
    DEFAULT_HIGHLIGHT_TIME = 0.2
    DEFAULT_KEYPRESS_COOLDOWN = 0.2

    def __init__(self, x, y, width, height,
                 character_font, symbol_font,
                 keypress_cooldown=DEFAULT_KEYPRESS_COOLDOWN,
                 highlight_duration=DEFAULT_HIGHLIGHT_TIME,
                 allow_sticky_repeat=False, layout_config=None):
        super().__init__()
        self.shift_mode = False
        self.layout_config = layout_config
        if self.layout_config is None:
            lib_path = __file__
            lib_path = lib_path.split("/")[:-1]
            f = open(f"{'/'.join(lib_path)}/default_layout.json", "r")
            self.layout_config = json.loads(f.read())

        layout = GridLayout(
            x=x,  # layout x
            y=y,  # layout y
            width=width,
            height=height,
            grid_size=tuple(self.layout_config['base_grid_size']),  # Grid Layout width,height
            cell_padding=2,
            divider_lines=True,  # divider lines around every cell
            cell_anchor_point=(0.5, 0.5)
        )
        self.highlight_duration = highlight_duration
        self.keypress_cooldown = keypress_cooldown
        self._highlighted_views = []
        self.last_keypressed_time = -1
        self.keypress_debounced = None
        self.allow_sticky_repeat = allow_sticky_repeat
        self.shift_key_view = None
        # Grid Layout Labels. Cell invisible with no text label

        _labels = []
        keyboard_input = []

        for row_idx, row in enumerate(self.layout_config["rows"]):
            cur_span_offset = 0
            for col_idx, key in enumerate(row["keys"]):
                _font = character_font
                if "font" in key:
                    if key["font"] == "symbol_font":
                        _font = symbol_font
                _scale = 2
                if "scale" in key:
                    _scale = key["scale"]
                l = label.Label(_font, scale=_scale, text=key["label"])
                l.key_config = key
                size = (1, 1)
                if "col_span" in key:
                    size = (key["col_span"], 1)

                position = (col_idx + cur_span_offset, row_idx)
                layout.add_content(l, grid_position=position, cell_size=size, layout_cells=False)
                if "col_span" in key:
                    cur_span_offset += key["col_span"] - 1
        layout.layout_cells()
        # _labels.append(label.Label(character_font, scale=2, x=0, y=0, text="`"))
        # layout.add_content(_labels[0], grid_position=(0, 0), cell_size=(1, 1))
        # _labels.append(label.Label(character_font, scale=2, x=0, y=0, text="1"))
        # layout.add_content(_labels[1], grid_position=(1, 0), cell_size=(1, 1))
        # _labels.append(label.Label(character_font, scale=2, x=0, y=0, text="2"))
        # layout.add_content(_labels[2], grid_position=(2, 0), cell_size=(1, 1))
        # _labels.append(label.Label(character_font, scale=2, x=0, y=0, text="3"))
        # layout.add_content(_labels[3], grid_position=(3, 0), cell_size=(1, 1))
        # _labels.append(label.Label(character_font, scale=2, x=0, y=0, text="4"))
        # layout.add_content(_labels[4], grid_position=(4, 0), cell_size=(1, 1))
        # _labels.append(label.Label(character_font, scale=2, x=0, y=0, text="5"))
        # layout.add_content(_labels[5], grid_position=(5, 0), cell_size=(1, 1))
        # _labels.append(label.Label(character_font, scale=2, x=0, y=0, text="6"))
        # layout.add_content(_labels[6], grid_position=(6, 0), cell_size=(1, 1))
        # _labels.append(label.Label(character_font, scale=2, x=0, y=0, text="7"))
        # layout.add_content(_labels[7], grid_position=(7, 0), cell_size=(1, 1))
        # _labels.append(label.Label(character_font, scale=2, x=0, y=0, text="8"))
        # layout.add_content(_labels[8], grid_position=(8, 0), cell_size=(1, 1))
        # _labels.append(label.Label(character_font, scale=2, x=0, y=0, text="9"))
        # layout.add_content(_labels[9], grid_position=(9, 0), cell_size=(1, 1))
        # _labels.append(label.Label(character_font, scale=2, x=0, y=0, text="0"))
        # layout.add_content(_labels[10], grid_position=(10, 0), cell_size=(1, 1))
        # _labels.append(label.Label(character_font, scale=2, x=0, y=0, text="-"))
        # layout.add_content(_labels[11], grid_position=(11, 0), cell_size=(1, 1))
        # _labels.append(label.Label(character_font, scale=2, x=0, y=0, text="="))
        # layout.add_content(_labels[12], grid_position=(12, 0), cell_size=(1, 1))
        # _labels.append(label.Label(symbol_font, scale=1, x=0, y=0, text="\uf0e2"))
        # layout.add_content(_labels[13], grid_position=(13, 0), cell_size=(1, 1))
        # 
        # _labels.append(label.Label(character_font, scale=2, x=0, y=0, text="Q"))
        # layout.add_content(_labels[14], grid_position=(0, 1), cell_size=(1, 1))
        # _labels.append(label.Label(character_font, scale=2, x=0, y=0, text="W"))
        # layout.add_content(_labels[15], grid_position=(1, 1), cell_size=(1, 1))
        # _labels.append(label.Label(character_font, scale=2, x=0, y=0, text="E"))
        # layout.add_content(_labels[16], grid_position=(2, 1), cell_size=(1, 1))
        # _labels.append(label.Label(character_font, scale=2, x=0, y=0, text="R"))
        # layout.add_content(_labels[17], grid_position=(3, 1), cell_size=(1, 1))
        # _labels.append(label.Label(character_font, scale=2, x=0, y=0, text="T"))
        # layout.add_content(_labels[18], grid_position=(4, 1), cell_size=(1, 1))
        # _labels.append(label.Label(character_font, scale=2, x=0, y=0, text="Y"))
        # layout.add_content(_labels[19], grid_position=(5, 1), cell_size=(1, 1))
        # _labels.append(label.Label(character_font, scale=2, x=0, y=0, text="U"))
        # layout.add_content(_labels[20], grid_position=(6, 1), cell_size=(1, 1))
        # _labels.append(label.Label(character_font, scale=2, x=0, y=0, text="I"))
        # layout.add_content(_labels[21], grid_position=(7, 1), cell_size=(1, 1))
        # _labels.append(label.Label(character_font, scale=2, x=0, y=0, text="O"))
        # layout.add_content(_labels[22], grid_position=(8, 1), cell_size=(1, 1))
        # _labels.append(label.Label(character_font, scale=2, x=0, y=0, text="P"))
        # layout.add_content(_labels[23], grid_position=(9, 1), cell_size=(1, 1))
        # _labels.append(label.Label(character_font, scale=2, x=0, y=0, text="["))
        # layout.add_content(_labels[24], grid_position=(10, 1), cell_size=(1, 1))
        # _labels.append(label.Label(character_font, scale=2, x=0, y=0, text="]"))
        # layout.add_content(_labels[25], grid_position=(11, 1), cell_size=(1, 1))
        # _labels.append(label.Label(character_font, scale=2, x=0, y=0, text="\\"))
        # layout.add_content(_labels[26], grid_position=(12, 1), cell_size=(2, 1))
        # 
        # _labels.append(label.Label(character_font, scale=2, x=0, y=0, text="A"))
        # layout.add_content(_labels[27], grid_position=(0, 2), cell_size=(1, 1))
        # _labels.append(label.Label(character_font, scale=2, x=0, y=0, text="S"))
        # layout.add_content(_labels[28], grid_position=(1, 2), cell_size=(1, 1))
        # _labels.append(label.Label(character_font, scale=2, x=0, y=0, text="D"))
        # layout.add_content(_labels[29], grid_position=(2, 2), cell_size=(1, 1))
        # _labels.append(label.Label(character_font, scale=2, x=0, y=0, text="F"))
        # layout.add_content(_labels[30], grid_position=(3, 2), cell_size=(1, 1))
        # _labels.append(label.Label(character_font, scale=2, x=0, y=0, text="G"))
        # layout.add_content(_labels[31], grid_position=(4, 2), cell_size=(1, 1))
        # _labels.append(label.Label(character_font, scale=2, x=0, y=0, text="H"))
        # layout.add_content(_labels[32], grid_position=(5, 2), cell_size=(1, 1))
        # _labels.append(label.Label(character_font, scale=2, x=0, y=0, text="J"))
        # layout.add_content(_labels[33], grid_position=(6, 2), cell_size=(1, 1))
        # _labels.append(label.Label(character_font, scale=2, x=0, y=0, text="K"))
        # layout.add_content(_labels[34], grid_position=(7, 2), cell_size=(1, 1))
        # _labels.append(label.Label(character_font, scale=2, x=0, y=0, text="L"))
        # layout.add_content(_labels[35], grid_position=(8, 2), cell_size=(1, 1))
        # _labels.append(label.Label(character_font, scale=2, x=0, y=0, text=";"))
        # layout.add_content(_labels[36], grid_position=(9, 2), cell_size=(1, 1))
        # _labels.append(label.Label(character_font, scale=2, x=0, y=0, text="'"))
        # layout.add_content(_labels[37], grid_position=(10, 2), cell_size=(1, 1))
        # _labels.append(label.Label(character_font, scale=2, x=0, y=0, text="ENTER"))
        # layout.add_content(_labels[38], grid_position=(11, 2), cell_size=(3, 1))
        # 
        # _labels.append(label.Label(character_font, scale=2, x=0, y=0, text="Z"))
        # layout.add_content(_labels[39], grid_position=(0, 3), cell_size=(1, 1))
        # _labels.append(label.Label(character_font, scale=2, x=0, y=0, text="X"))
        # layout.add_content(_labels[40], grid_position=(1, 3), cell_size=(1, 1))
        # _labels.append(label.Label(character_font, scale=2, x=0, y=0, text="C"))
        # layout.add_content(_labels[41], grid_position=(2, 3), cell_size=(1, 1))
        # _labels.append(label.Label(character_font, scale=2, x=0, y=0, text="V"))
        # layout.add_content(_labels[42], grid_position=(3, 3), cell_size=(1, 1))
        # _labels.append(label.Label(character_font, scale=2, x=0, y=0, text="B"))
        # layout.add_content(_labels[43], grid_position=(4, 3), cell_size=(1, 1))
        # _labels.append(label.Label(character_font, scale=2, x=0, y=0, text="N"))
        # layout.add_content(_labels[44], grid_position=(5, 3), cell_size=(1, 1))
        # _labels.append(label.Label(character_font, scale=2, x=0, y=0, text="M"))
        # layout.add_content(_labels[45], grid_position=(6, 3), cell_size=(1, 1))
        # _labels.append(label.Label(character_font, scale=2, x=0, y=0, text=","))
        # layout.add_content(_labels[46], grid_position=(7, 3), cell_size=(1, 1))
        # _labels.append(label.Label(character_font, scale=2, x=0, y=0, text=","))
        # layout.add_content(_labels[47], grid_position=(8, 3), cell_size=(1, 1))
        # _labels.append(label.Label(character_font, scale=2, x=0, y=0, text="."))
        # layout.add_content(_labels[48], grid_position=(9, 3), cell_size=(1, 1))
        # _labels.append(label.Label(character_font, scale=2, x=0, y=0, text="/"))
        # layout.add_content(_labels[49], grid_position=(10, 3), cell_size=(1, 1))
        # _labels.append(label.Label(character_font, scale=2, x=0, y=0, text="SHIFT"))
        # layout.add_content(_labels[50], grid_position=(11, 3), cell_size=(3, 1))
        # 
        # _labels.append(label.Label(character_font, scale=2, x=0, y=0, text="CTRL"))
        # layout.add_content(_labels[51], grid_position=(0, 4), cell_size=(2, 1))
        # _labels.append(label.Label(character_font, scale=2, x=0, y=0, text="ALT"))
        # layout.add_content(_labels[52], grid_position=(2, 4), cell_size=(2, 1))
        # _labels.append(label.Label(character_font, scale=2, x=0, y=0, text="SPACE"))
        # layout.add_content(_labels[53], grid_position=(4, 4), cell_size=(6, 1))
        # _labels.append(label.Label(symbol_font, scale=1, x=0, y=0, text="\uf060"))
        # layout.add_content(_labels[54], grid_position=(10, 4), cell_size=(1, 1))
        # _labels.append(label.Label(symbol_font, scale=1, x=0, y=0, text="\uf061"))
        # layout.add_content(_labels[55], grid_position=(11, 4), cell_size=(1, 1))
        # _labels.append(label.Label(symbol_font, scale=1, x=0, y=0, text="\uf062"))
        # layout.add_content(_labels[56], grid_position=(12, 4), cell_size=(1, 1))
        # _labels.append(label.Label(symbol_font, scale=1, x=0, y=0, text="\uf063"))
        # layout.add_content(_labels[57], grid_position=(13, 4), cell_size=(1, 1))

        self.layout = layout
        self.append(layout)

    @property
    def height(self):
        return self.layout.height

    @property
    def width(self):
        return self.layout.width

    def check_touches(self, touch_point):
        now = time.monotonic()

        for _view, unhighlight_time in self._highlighted_views:
            if now > unhighlight_time:
                _view.color = 0xffffff
                _view.background_color = 0x000000

        if touch_point:

            # if sticky repeat is on, or if the most recent keypress has been debounced i.e. released
            if self.allow_sticky_repeat or self.keypress_debounced:
                touched_cell = self.layout.which_cell_contains(touch_point)
                if touched_cell:
                    if self.last_keypressed_time + self.keypress_cooldown < now:
                        touched_cell_view = self.layout.get_cell(touched_cell)

                        if not self.shift_mode:
                            pressed_value = touched_cell_view.text.lower()
                        else:
                            pressed_value = touched_cell_view.text
                            self.shift_mode = False
                            self.shift_key_view.background_color = 0x000000
                            
                        print(touched_cell_view.key_config)
                        if "key_value" in touched_cell_view.key_config:
                            pressed_value = touched_cell_view.key_config["key_value"]

                        print(f"key_text: {pressed_value}")

                        self.last_keypressed_time = now
                        self.keypress_debounced = False

                        if pressed_value == 225:  # 0xE1 shift key
                            self.shift_mode = not self.shift_mode
                            if self.shift_mode:
                                touched_cell_view.background_color = 0x0000ff
                                self.shift_key_view = touched_cell_view
                            else:
                                touched_cell_view.background_color = 0x000000
                        else:
                            # non-special highlighting
                            touched_cell_view.background_color = 0x00ff00
                            touched_cell_view.color = 0x000000
                            self._highlighted_views.append((touched_cell_view, now + self.keypress_cooldown))

                        return pressed_value
        # keypress is None
        else:
            self.keypress_debounced = True
