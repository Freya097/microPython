# ============================================================
#  pcf8574.py  –  GPIO Expander driver
#  Chip: PCF8574 (8-bit) or PCF8574A
#  Default I2C address: 0x20–0x27 (set by A0/A1/A2 pins)
# ============================================================
#
#  HOW THE GPIO EXPANDER WORKS (student notes)
#  ─────────────────────────────────────────────
#  The PCF8574 gives you 8 extra GPIO pins (P0–P7) over I2C.
#  You only need 2 wires (SDA + SCL) instead of 8 GPIO pins!
#
#  It works like a simple register:
#    WRITE  one byte → sets output states  (bit=1 → HIGH, bit=0 → LOW)
#    READ   one byte → gets input states   (bit=1 → HIGH, bit=0 → LOW)
#
#  Important: PCF8574 is "quasi-bidirectional" – 
#    To read a pin, you must first write 1 to it (set it as input mode).
#    Writing 0 drives it LOW (output mode).
#
#  Address selection (PCF8574):
#    A2=0 A1=0 A0=0 → 0x20
#    A2=0 A1=0 A0=1 → 0x21
#    … up to 0x27 (A2=1 A1=1 A0=1)
#
#  PCF8574A uses addresses 0x38–0x3F instead.
#
# ============================================================


class PCF8574:
    """
    Driver for PCF8574 / PCF8574A 8-bit I2C GPIO expander.

    Parameters
    ----------
    i2c  : I2CCore instance
    addr : I2C address 0x20-0x27 (PCF8574) or 0x38-0x3F (PCF8574A)

    Quick example
    -------------
        gpio = PCF8574(bus, addr=0x20)
        gpio.write_pin(0, 1)    # set P0 HIGH
        gpio.write_pin(3, 0)    # set P3 LOW
        val = gpio.read_pin(5)  # read P5
    """

    def __init__(self, i2c, addr: int = 0x20):
        self._i2c   = i2c
        self._addr  = addr
        # Shadow register: keeps track of the current output state
        # All pins start HIGH (input mode / high-impedance)
        self._state = 0xFF
        self._write_byte(self._state)

    # ── Internal helpers ──────────────────────────────────────

    def _write_byte(self, byte: int):
        """Send the full 8-pin state to the chip."""
        self._i2c.write(self._addr, bytes([byte & 0xFF]))

    def _read_byte(self) -> int:
        """Read the full 8-pin state from the chip."""
        return self._i2c.read(self._addr, 1)[0]

    # ── Single pin operations ─────────────────────────────────

    def write_pin(self, pin: int, value: int):
        """
        Set a single pin HIGH (1) or LOW (0).

        Parameters
        ----------
        pin   : 0–7 (P0 to P7)
        value : 1 = HIGH, 0 = LOW
        """
        if not 0 <= pin <= 7:
            raise ValueError(f"Pin must be 0-7, got {pin}")
        if value:
            self._state |=  (1 << pin)   # set bit
        else:
            self._state &= ~(1 << pin)   # clear bit
        self._write_byte(self._state)

    def read_pin(self, pin: int) -> int:
        """
        Read the current state of a single pin.
        The pin must have been written HIGH first (to enable input mode).

        Parameters
        ----------
        pin : 0–7

        Returns 1 (HIGH) or 0 (LOW).
        """
        if not 0 <= pin <= 7:
            raise ValueError(f"Pin must be 0-7, got {pin}")
        # Set pin HIGH first so it can be read
        self._state |= (1 << pin)
        self._write_byte(self._state)
        # Now read all 8 pins and return the specific one
        byte = self._read_byte()
        return (byte >> pin) & 1

    def toggle_pin(self, pin: int):
        """Flip a pin: HIGH→LOW or LOW→HIGH."""
        current = (self._state >> pin) & 1
        self.write_pin(pin, 0 if current else 1)

    # ── Full port operations ──────────────────────────────────

    def write_port(self, byte: int):
        """
        Write all 8 pins at once.

        Parameters
        ----------
        byte : 8-bit value, e.g. 0b10110000
               bit 0 = P0, bit 7 = P7
        """
        self._state = byte & 0xFF
        self._write_byte(self._state)

    def read_port(self) -> int:
        """
        Read all 8 pins at once.

        Returns an integer, e.g. 0b00101100
        Use:  (result >> pin) & 1  to extract a single pin.
        """
        # First release all pins to HIGH so we can read them
        self._write_byte(0xFF)
        return self._read_byte()

    # ── Convenience ───────────────────────────────────────────

    def set_outputs(self, *pins):
        """
        Set specific pins as outputs (drive LOW).
        Remaining pins stay as inputs (HIGH).

        Example: gpio.set_outputs(0, 1, 2)  → P0, P1, P2 driven LOW
        """
        mask = 0xFF
        for pin in pins:
            mask &= ~(1 << pin)
        self._state = mask
        self._write_byte(self._state)

    def get_state(self) -> int:
        """Return the current output shadow register (what we wrote last)."""
        return self._state

    def pins_to_dict(self) -> dict:
        """Return all pin states as a dictionary {0: 1, 1: 0, …}"""
        byte = self._read_byte()
        return {pin: (byte >> pin) & 1 for pin in range(8)}


# ── LCD helper that sits on top of PCF8574 ───────────────────
# Many cheap 16×2 LCD I2C modules use a PCF8574 as the backpack.
# Pin mapping for the popular HW-063 / FC-113 backpack module:
#   P0=RS  P1=RW  P2=EN  P3=backlight  P4=D4  P5=D5  P6=D6  P7=D7

class LCD1602:
    """
    16×2 character LCD driven via PCF8574 I2C backpack.
    Uses the HD44780 controller in 4-bit mode.

    Quick example
    -------------
        lcd = LCD1602(bus, addr=0x27)
        lcd.print("Hello world!")
        lcd.print("Line 2", row=1)
    """

    import time as _time

    RS  = 0   # Register Select (0=command, 1=data)
    RW  = 1   # Read/Write (always 0=write here)
    EN  = 2   # Enable
    BL  = 3   # Backlight
    D4  = 4
    D5  = 5
    D6  = 6
    D7  = 7

    def __init__(self, i2c, addr: int = 0x27, cols: int = 16, rows: int = 2):
        self._io   = PCF8574(i2c, addr)
        self._cols = cols
        self._rows = rows
        self._backlight = True
        self._init_lcd()

    def _pulse_enable(self):
        """Pulse the EN pin to latch data."""
        self._io.write_pin(self.EN, 1)
        import time; time.sleep_us(1)
        self._io.write_pin(self.EN, 0)
        import time; time.sleep_us(50)

    def _write_nibble(self, nibble: int, rs: int):
        """Write the upper 4 bits of a byte."""
        bl = 1 if self._backlight else 0
        self._io.write_port(
            (rs         << self.RS) |
            (0          << self.RW) |
            (bl         << self.BL) |
            (((nibble >> 3) & 1) << self.D7) |
            (((nibble >> 2) & 1) << self.D6) |
            (((nibble >> 1) & 1) << self.D5) |
            (((nibble >> 0) & 1) << self.D4)
        )
        self._pulse_enable()

    def _write_byte(self, byte: int, rs: int = 0):
        """Write a full byte as two nibbles (4-bit mode)."""
        self._write_nibble(byte >> 4, rs)    # high nibble first
        self._write_nibble(byte & 0x0F, rs)  # low nibble

    def _command(self, cmd: int):
        """Send a command byte (rs=0)."""
        self._write_byte(cmd, rs=0)
        import time; time.sleep_ms(2)

    def _char(self, ch: int):
        """Send a character byte (rs=1)."""
        self._write_byte(ch, rs=1)

    def _init_lcd(self):
        """Initialise LCD in 4-bit mode (from HD44780 datasheet)."""
        import time
        time.sleep_ms(50)
        # Special 3-step init for 4-bit mode
        self._write_nibble(0x03, 0); time.sleep_ms(5)
        self._write_nibble(0x03, 0); time.sleep_ms(1)
        self._write_nibble(0x03, 0); time.sleep_ms(1)
        self._write_nibble(0x02, 0)   # switch to 4-bit mode
        # Configuration commands
        self._command(0x28)   # 4-bit, 2 lines, 5×8 font
        self._command(0x0C)   # display ON, cursor OFF
        self._command(0x06)   # cursor moves right
        self.clear()

    # ── Public API ────────────────────────────────────────────

    def clear(self):
        """Clear screen and home cursor."""
        self._command(0x01)

    def home(self):
        """Move cursor to top-left."""
        self._command(0x02)

    def set_cursor(self, col: int, row: int):
        """Move cursor to (col, row). col=0-15, row=0-1."""
        offsets = [0x00, 0x40]    # row 0 starts at 0x00, row 1 at 0x40
        self._command(0x80 | (offsets[row % 2] + col))

    def print(self, text: str, col: int = 0, row: int = 0):
        """Print text at (col, row), truncated to display width."""
        self.set_cursor(col, row)
        for ch in str(text)[:self._cols - col]:
            self._char(ord(ch))

    def backlight(self, on: bool):
        """Turn the backlight on or off."""
        self._backlight = on
        self._io.write_pin(self.BL, 1 if on else 0)
