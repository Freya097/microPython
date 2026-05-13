# ============================================================
#  ssd1306.py  –  OLED display driver  (128×64 pixels)
#  Chip: SSD1306   Default I2C address: 0x3C
# ============================================================
#
#  HOW THE OLED WORKS (student notes)
#  ────────────────────────────────────
#  The display has a 128×64 grid of pixels.
#  We store them in a "framebuffer" – a bytearray in RAM.
#  Each BYTE controls 8 vertical pixels in one column.
#  When you call show(), we send the whole buffer to the chip.
#
#  Coordinate system:
#    (0,0) = top-left
#    (127,0) = top-right
#    (0,63) = bottom-left
#
#  I2C data format:
#    Every I2C write must start with a control byte:
#      0x00 = the next bytes are COMMANDS
#      0x40 = the next bytes are PIXEL DATA
#
# ============================================================

import framebuf          # MicroPython built-in: pixel drawing primitives


# ── Initialisation command sequence ──────────────────────────
# These bytes wake up and configure the SSD1306 chip.
# (You don't need to memorise these – they come from the datasheet.)
_INIT_SEQUENCE = bytes([
    0x00,        # following bytes are commands
    0xAE,        # display off (while we configure)
    0x20, 0x00,  # memory addressing mode = horizontal
    0xB0,        # page start address
    0xC8,        # COM scan direction: flip vertically
    0x00,        # lower column address
    0x10,        # upper column address
    0x40,        # display start line = 0
    0x81, 0xFF,  # contrast = maximum
    0xA1,        # segment re-map (flip horizontally)
    0xA6,        # normal display (not inverted)
    0xA8, 0x3F,  # multiplex ratio = 64 rows
    0xA4,        # output follows RAM content
    0xD3, 0x00,  # display offset = 0
    0xD5, 0xF0,  # clock divide ratio / oscillator frequency
    0xD9, 0x22,  # pre-charge period
    0xDA, 0x12,  # COM pins hardware configuration
    0xDB, 0x20,  # VCOMH deselect level
    0x8D, 0x14,  # charge pump enable
    0xAF,        # display ON
])


class SSD1306:
    """
    128×64 OLED display over I2C.

    Parameters
    ----------
    i2c  : I2CCore instance (or any object with .write() / .read())
    addr : I2C address  (0x3C is default; some modules use 0x3D)

    Quick example
    -------------
        oled = SSD1306(bus)
        oled.text("Hello!", 0, 0)
        oled.show()
    """

    WIDTH  = 128
    HEIGHT = 64

    def __init__(self, i2c, addr: int = 0x3C):
        self._i2c  = i2c
        self._addr = addr

        # Framebuffer: 128 columns × 8 pages × 1 byte/page = 1024 bytes
        # MONO_VLSB means: each byte = 8 vertical pixels (LSB at top)
        self._buf = bytearray(self.WIDTH * self.HEIGHT // 8)
        self._fb  = framebuf.FrameBuffer(
            self._buf, self.WIDTH, self.HEIGHT, framebuf.MONO_VLSB
        )

        # Wake up the display
        self._i2c.write(self._addr, _INIT_SEQUENCE)

    # ── Low-level commands ────────────────────────────────────

    def _cmd(self, *cmds):
        """Send one or more command bytes."""
        self._i2c.write(self._addr, bytes([0x00]) + bytes(cmds))

    def _data(self, buf):
        """Send raw pixel data (prefixed with 0x40 control byte)."""
        # Send in chunks of 32 bytes to stay within I2C buffer limits
        chunk = 32
        prefix = bytes([0x40])
        for i in range(0, len(buf), chunk):
            self._i2c.write(self._addr, prefix + bytes(buf[i:i+chunk]))

    # ── Display control ───────────────────────────────────────

    def show(self):
        """
        Push the framebuffer to the display.
        NOTHING changes on screen until you call this.
        """
        self._cmd(0x21, 0, self.WIDTH - 1)    # column range
        self._cmd(0x22, 0, self.HEIGHT // 8 - 1)  # page range
        self._data(self._buf)

    def fill(self, color: int = 0):
        """
        Fill the entire screen with one color.
        color = 0 → black (off)
        color = 1 → white (on)
        """
        self._fb.fill(color)

    def invert(self, on: bool):
        """Invert all pixels (white↔black) without touching the framebuffer."""
        self._cmd(0xA7 if on else 0xA6)

    def contrast(self, level: int):
        """Set brightness 0 (dimmest) to 255 (brightest)."""
        self._cmd(0x81, level)

    def power(self, on: bool):
        """Turn display on or off (content stays in RAM)."""
        self._cmd(0xAF if on else 0xAE)

    # ── Drawing primitives ────────────────────────────────────
    # These just wrap MicroPython's built-in framebuf methods.

    def pixel(self, x: int, y: int, color: int = 1):
        """Draw a single pixel at (x, y)."""
        self._fb.pixel(x, y, color)

    def line(self, x0, y0, x1, y1, color: int = 1):
        """Draw a line from (x0,y0) to (x1,y1)."""
        self._fb.line(x0, y0, x1, y1, color)

    def rect(self, x, y, w, h, color: int = 1, fill: bool = False):
        """Draw a rectangle. fill=True fills it solid."""
        if fill:
            self._fb.fill_rect(x, y, w, h, color)
        else:
            self._fb.rect(x, y, w, h, color)

    def text(self, string: str, x: int, y: int, color: int = 1):
        """
        Write text at pixel position (x, y).
        Built-in font is 8×8 pixels, ASCII only.
        Max columns at x=0: 16 characters (128/8).
        Max rows    at y=0:  8 lines      (64/8).
        """
        self._fb.text(string, x, y, color)

    def scroll(self, dx: int, dy: int):
        """Scroll the framebuffer by (dx, dy) pixels."""
        self._fb.scroll(dx, dy)

    def blit(self, fbuf, x: int, y: int, key: int = -1):
        """
        Copy another framebuffer into this one at (x, y).
        Useful for sprites / icons.
        """
        self._fb.blit(fbuf, x, y, key)

    # ── Convenience ───────────────────────────────────────────

    def clear(self, show: bool = True):
        """Clear screen. Pass show=False to skip pushing to hardware."""
        self._fb.fill(0)
        if show:
            self.show()

    def center_text(self, string: str, y: int, color: int = 1):
        """Draw text centered horizontally on the display."""
        x = (self.WIDTH - len(string) * 8) // 2
        self.text(string, max(0, x), y, color)

    def draw_status_bar(self, title: str, value: str):
        """
        Convenience: draw a title on top line and a value large-ish below.
        Useful for sensor readouts.
        """
        self.fill(0)
        self.rect(0, 0, self.WIDTH, 12, 1, fill=True)  # header bar
        self.text(title[:16], 0, 2, 0)                  # title in black
        self.text(value, 0, 20, 1)                       # value in white
        self.show()
