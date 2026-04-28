import displayio
import terminalio
import busio
import digitalio
import board
import adafruit_st7735r
from adafruit_display_text import label


C_BG = 0x0D0D2B
C_TITLE = 0x00FFFF
C_NOTE = 0xFFFFFF
C_NOTE_OFF = 0x334455
C_VOL_FG = 0x00FF66
C_VOL_BG = 0x1A2A1A
C_LABEL = 0x778899
C_POLY = 0xFF8C00
C_OCT = 0xFFAA00

NOTE_NAMES = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']


def midi_note_name(n):
    return f"{NOTE_NAMES[n % 12]}{(n // 12) - 1}"


class KeyboardDisplay:

    def __init__(self, cfg):
        import board as _board
        
        
        displayio.release_displays()


        self._bl = digitalio.DigitalInOut(getattr(_board, f"GP{cfg.LCD_BL_GPIO}"))
        self._bl.direction = digitalio.Direction.OUTPUT
        self._bl.value = True


        spi = busio.SPI(
            clock=getattr(_board, f"GP{cfg.LCD_SCK_GPIO}"),
            MOSI=getattr(_board, f"GP{cfg.LCD_MOSI_GPIO}"),
        )
        
        bus = displayio.FourWire(
            spi,
            command=getattr(_board, f"GP{cfg.LCD_DC_GPIO}"),
            chip_select=getattr(_board, f"GP{cfg.LCD_CS_GPIO}"),
            reset=getattr(_board, f"GP{cfg.LCD_RST_GPIO}"),
        )
        
        self._display = adafruit_st7735r.ST7735R(
            bus,
            width=cfg.LCD_WIDTH,
            height=cfg.LCD_HEIGHT,
            rotation=cfg.LCD_ROTATION,
            bgr=cfg.LCD_BGR,
        )

        W = cfg.LCD_WIDTH
        H = cfg.LCD_HEIGHT
        self._W = W
        self._H = H


        root = displayio.Group()
        self._display.root_group = root


        bg_bmp = displayio.Bitmap(W, H, 1)
        bg_pal = displayio.Palette(1)
        bg_pal[0] = C_BG
        root.append(displayio.TileGrid(bg_bmp, pixel_shader=bg_pal))

        
        title = label.Label(
            terminalio.FONT, text="  MIDI KEYS  ",
            color=C_TITLE, scale=2,
            anchor_point=(0.5, 0.0),
            anchored_position=(W // 2, 3),
        )
        root.append(title)


        div_bmp = displayio.Bitmap(W, 1, 1)
        div_pal = displayio.Palette(1)
        div_pal[0] = C_TITLE
        root.append(displayio.TileGrid(div_bmp, pixel_shader=div_pal, x=0, y=21))


        self._note_lbl = label.Label(
            terminalio.FONT, text="---",
            color=C_NOTE_OFF, scale=4,
            anchor_point=(0.5, 0.5),
            anchored_position=(W // 2, 52),
        )
        root.append(self._note_lbl)


        self._poly_lbl = label.Label(
            terminalio.FONT, text="",
            color=C_POLY, scale=1,
            anchor_point=(0.0, 0.0),
            anchored_position=(4, 80),
        )
        root.append(self._poly_lbl)

        self._oct_lbl = label.Label(
            terminalio.FONT, text="OCT +0",
            color=C_OCT, scale=1,
            anchor_point=(1.0, 0.0),
            anchored_position=(W - 4, 80),
        )
        root.append(self._oct_lbl)


        vol_lbl = label.Label(
            terminalio.FONT, text="VOL",
            color=C_LABEL, scale=1,
            anchor_point=(0.0, 0.0),
            anchored_position=(4, 94),
        )
        root.append(vol_lbl)

        self._vol_num = label.Label(
            terminalio.FONT, text="100",
            color=C_VOL_FG, scale=1,
            anchor_point=(1.0, 0.0),
            anchored_position=(W - 4, 94),
        )
        root.append(self._vol_num)


        BAR_W = W - 8
        BAR_H = 10
        self._bar_bmp = displayio.Bitmap(BAR_W, BAR_H, 2)
        bar_pal = displayio.Palette(2)
        bar_pal[0] = C_VOL_BG
        bar_pal[1] = C_VOL_FG
        self._bar_sprite = displayio.TileGrid(
            self._bar_bmp, pixel_shader=bar_pal, x=4, y=108
        )
        root.append(self._bar_sprite)


        self._draw_mini_keyboard(root, W, H)

        self._last_note  = None
        self._last_vol   = -1
        self._last_oct   = None
        self._last_poly  = -1
        self._bar_W      = BAR_W
        self._bar_H      = BAR_H

    

    def _draw_mini_keyboard(self, root, W, H):
        """Draw a decorative 2-octave piano strip at the very bottom."""
        strip_H = H - 123
        if strip_H < 1:
            return
        
        bmp = displayio.Bitmap(W, max(strip_H, 4), 3)
        pal = displayio.Palette(3)
        pal[0] = 0x222222
        pal[1] = 0xEEEEEE
        pal[2] = 0x111111

        whites = 15
        key_w  = W // whites
        for k in range(whites):
            x0 = k * key_w
            for px in range(x0 + 1, x0 + key_w - 1):
                for py in range(1, max(strip_H, 4) - 1):
                    bmp[px, py] = 1


        black_positions = [1, 2, 4, 5, 6]
        for octave in range(2):
            for bp in black_positions:
                x0 = (octave * 7 + bp) * key_w - key_w // 3
                for px in range(x0, x0 + key_w * 2 // 3):
                    if 0 <= px < W:
                        for py in range(1, max(strip_H, 4) // 2 + 1):
                            bmp[px, py] = 2

        root.append(displayio.TileGrid(bmp, pixel_shader=pal, x=0, y=H - max(strip_H, 4)))

    def _fill_bar(self, volume):
        fill = int((volume / 127) * self._bar_W)
        for x in range(self._bar_W):
            for y in range(self._bar_H):
                self._bar_bmp[x, y] = 1 if x < fill else 0



    def update(self, active_notes, volume, octave_shift):
        changed = False


        if active_notes:
            lowest = min(active_notes)
            name   = midi_note_name(lowest)
            color  = C_NOTE
        else:
            name  = "---"
            color = C_NOTE_OFF

        if name != self._last_note:
            self._note_lbl.text  = name
            self._note_lbl.color = color
            self._last_note = name
            changed = True

 
        poly = len(active_notes)
        if poly != self._last_poly:
            self._poly_lbl.text = f"+{poly - 1} notes" if poly > 1 else ""
            self._last_poly = poly
            changed = True


        if octave_shift != self._last_oct:
            sign = "+" if octave_shift >= 0 else ""
            self._oct_lbl.text = f"OCT {sign}{octave_shift}"
            self._last_oct = octave_shift
            changed = True


        if volume != self._last_vol:
            self._vol_num.text = str(volume)
            self._fill_bar(volume)
            self._last_vol = volume
            changed = True

        return changed

    def set_backlight(self, on: bool):
        self._bl.value = on