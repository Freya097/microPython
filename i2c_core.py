# ============================================================
#  i2c_core.py  –  Software (bit-bang) I2C driver
#  No HAL, no platform library needed.
#  Works on any MicroPython board (ESP32, RP2040, STM32, …)
# ============================================================
#
#  HOW I2C WORKS (student notes)
#  ─────────────────────────────
#  SDA  = data line  (1 wire carries all bytes)
#  SCL  = clock line (master drives this)
#
#  Every transfer looks like:
#    START ─► [address + R/W bit] ─► ACK ─► [data bytes] ─► STOP
#
#  START condition : SDA falls while SCL is HIGH
#  STOP  condition : SDA rises  while SCL is HIGH
#  Each bit        : SDA is stable while SCL is HIGH
#
# ============================================================

from machine import Pin
import time


class I2CCore:
    """
    Pure software I2C master.

    Parameters
    ----------
    sda_pin : int   GPIO number for SDA
    scl_pin : int   GPIO number for SCL
    freq    : int   clock speed in Hz  (default 100 000 = 100 kHz)
    """

    def __init__(self, sda_pin: int, scl_pin: int, freq: int = 100_000):
        # Store pin numbers for later (TCA multiplexer needs to reset the bus)
        self.sda_pin_num = sda_pin
        self.scl_pin_num = scl_pin

        # Half-period delay in microseconds  (freq=100kHz → 5 µs)
        self._delay_us = max(1, 500_000 // freq)

        # Set up open-drain pins
        # Open-drain = output only pulls LOW; releases HIGH to pull-up resistor
        self._sda = Pin(sda_pin, Pin.OPEN_DRAIN, value=1)
        self._scl = Pin(scl_pin, Pin.OPEN_DRAIN, value=1)

        # Make sure bus is free before we start
        self._release_bus()

    # ── Internal helpers ──────────────────────────────────────

    def _delay(self):
        time.sleep_us(self._delay_us)

    def _sda_high(self):  self._sda(1)
    def _sda_low(self):   self._sda(0)
    def _scl_high(self):  self._scl(1); self._delay()   # give slave time to react
    def _scl_low(self):   self._scl(0); self._delay()

    def _release_bus(self):
        """Send 9 dummy clocks so a stuck slave can finish its byte."""
        self._sda_high()
        for _ in range(9):
            self._scl_high()
            self._scl_low()
        self._sda_high()

    # ── I2C conditions ────────────────────────────────────────

    def _start(self):
        """START: SDA goes LOW while SCL is HIGH."""
        self._sda_high()
        self._scl_high()
        self._sda_low()   # ← the actual START event
        self._scl_low()

    def _stop(self):
        """STOP: SDA goes HIGH while SCL is HIGH."""
        self._sda_low()
        self._scl_high()
        self._sda_high()  # ← the actual STOP event
        self._delay()

    def _repeated_start(self):
        """Repeated START (used when switching read↔write without releasing bus)."""
        self._sda_high()
        self._scl_high()
        self._sda_low()
        self._scl_low()

    # ── Bit-level read / write ────────────────────────────────

    def _write_bit(self, bit: int):
        if bit:
            self._sda_high()
        else:
            self._sda_low()
        self._scl_high()   # slave reads SDA while SCL is HIGH
        self._scl_low()

    def _read_bit(self) -> int:
        self._sda_high()   # release SDA so slave can drive it
        self._scl_high()
        bit = self._sda()  # sample SDA while SCL is HIGH
        self._scl_low()
        return bit

    # ── Byte-level read / write ───────────────────────────────

    def _write_byte(self, byte: int) -> bool:
        """
        Send 8 bits MSB-first, then read the ACK bit.
        Returns True if slave acknowledged (ACK = SDA pulled LOW by slave).
        """
        for i in range(7, -1, -1):          # bit 7 down to bit 0
            self._write_bit((byte >> i) & 1)
        ack = self._read_bit()
        return ack == 0  # ACK = LOW = 0

    def _read_byte(self, ack: bool = True) -> int:
        """
        Read 8 bits MSB-first, then send ACK or NACK.
        Send ACK  (ack=True)  if you want more bytes.
        Send NACK (ack=False) for the last byte.
        """
        byte = 0
        for _ in range(8):
            byte = (byte << 1) | self._read_bit()
        self._write_bit(0 if ack else 1)    # 0=ACK, 1=NACK
        return byte

    # ── Public API ────────────────────────────────────────────

    def write(self, addr: int, data: bytes, stop: bool = True) -> bool:
        """
        Write bytes to a device.

        Parameters
        ----------
        addr : 7-bit I2C address  (e.g. 0x3C for SSD1306)
        data : bytes or bytearray to send
        stop : send STOP at the end (set False for repeated-start reads)

        Returns True if device acknowledged its address.
        """
        self._start()
        if not self._write_byte((addr << 1) | 0):   # address + WRITE bit (0)
            self._stop()
            return False

        for byte in data:
            self._write_byte(byte)

        if stop:
            self._stop()
        return True

    def read(self, addr: int, n_bytes: int) -> bytes:
        """
        Read n_bytes from a device.

        Parameters
        ----------
        addr    : 7-bit I2C address
        n_bytes : how many bytes to read

        Returns a bytes object of length n_bytes.
        """
        self._start()
        if not self._write_byte((addr << 1) | 1):   # address + READ bit (1)
            self._stop()
            return bytes(n_bytes)  # return zeros on error

        result = bytearray()
        for i in range(n_bytes):
            ack = (i < n_bytes - 1)          # ACK all but the last byte
            result.append(self._read_byte(ack))
        self._stop()
        return bytes(result)

    def write_then_read(self, addr: int, write_data: bytes, n_bytes: int) -> bytes:
        """
        Write a register address, then read back data without releasing the bus.
        This is the most common pattern:  write reg → repeated-START → read.
        """
        self._start()
        if not self._write_byte((addr << 1) | 0):
            self._stop()
            return bytes(n_bytes)

        for byte in write_data:
            self._write_byte(byte)

        # Repeated START (no STOP between write and read)
        self._repeated_start()
        self._write_byte((addr << 1) | 1)

        result = bytearray()
        for i in range(n_bytes):
            ack = (i < n_bytes - 1)
            result.append(self._read_byte(ack))
        self._stop()
        return bytes(result)

    def scan(self) -> list:
        """
        Scan the bus and return a list of addresses that responded.
        Useful for debugging wiring.
        """
        found = []
        for addr in range(0x08, 0x78):       # valid 7-bit range
            self._start()
            ack = self._write_byte((addr << 1) | 0)
            self._stop()
            if ack:
                found.append(addr)
        return found
