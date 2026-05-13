from machine import I2C, Pin
import framebuf
import time

class OLED:

    def __init__(self, scl, sda, addr=0x3C):

        self.width = 128
        self.height = 64
        self.addr = addr

        # I2C created using passed pins
        self.i2c = I2C(
            0,
            scl=Pin(scl),
            sda=Pin(sda),
            freq=400000
        )

        self.buffer = bytearray(self.width * self.height // 8)

        self.fb = framebuf.FrameBuffer(
            self.buffer,
            self.width,
            self.height,
            framebuf.MONO_VLSB
        )

        self.init_oled()

    # ---------------- LOW LEVEL ---------------- #

    def write_cmd(self, cmd):
        self.i2c.writeto(self.addr, bytearray([0x80, cmd]))

    def write_data(self, data):
        self.i2c.writeto(self.addr, bytearray([0x40]) + data)

    # ---------------- INIT ---------------- #

    def init_oled(self):

        for cmd in (
            0xAE, 0x20, 0x00,
            0xB0, 0xC8, 0x00, 0x10,
            0x40, 0x81, 0x7F,
            0xA1, 0xA6, 0xA8, 0x3F,
            0xA4, 0xD3, 0x00,
            0xD5, 0x80, 0xD9, 0xF1,
            0xDA, 0x12, 0xDB, 0x40,
            0x8D, 0x14, 0xAF
        ):
            self.write_cmd(cmd)

        self.clear()
        self.show()

    # ---------------- API ---------------- #

    def clear(self):
        self.fb.fill(0)

    def show(self):
        for i in range(0, len(self.buffer), 16):
            self.write_data(self.buffer[i:i+16])

    def text(self, msg, x, y):
        self.fb.text(msg, x, y, 1)

    def line(self, x1, y1, x2, y2):
        self.fb.line(x1, y1, x2, y2, 1)

    def rect(self, x, y, w, h):
        self.fb.rect(x, y, w, h, 1)
