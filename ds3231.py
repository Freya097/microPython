# ============================================================
#  ds3231.py  –  Real-Time Clock driver
#  Chip: DS3231   I2C address: 0x68 (fixed, cannot change)
# ============================================================
#
#  HOW THE RTC WORKS (student notes)
#  ────────────────────────────────────
#  The DS3231 keeps track of date and time even when your
#  microcontroller is powered off (it has a tiny backup battery).
#
#  It stores time as BCD (Binary Coded Decimal):
#    The number 59 is stored as  0101 1001  (not 0011 1011)
#    High nibble = tens digit,  Low nibble = units digit
#
#  Register map (each is 1 byte at that address):
#    0x00 = seconds    0x01 = minutes   0x02 = hours
#    0x03 = weekday    0x04 = day       0x05 = month
#    0x06 = year       0x07 = alarm 1 seconds … (not used here)
#    0x11 = MSB temp   0x12 = LSB temp (0.25°C resolution)
#
# ============================================================


class DS3231:
    """
    Driver for the DS3231 Real-Time Clock.

    Parameters
    ----------
    i2c  : I2CCore instance
    addr : always 0x68

    Quick example
    -------------
        rtc = DS3231(bus)
        rtc.set_time(2024, 6, 15, 14, 30, 0)   # 2024-06-15  14:30:00
        year, month, day, hour, minute, second = rtc.get_time()
    """

    ADDR = 0x68   # DS3231 address is fixed by the chip

    def __init__(self, i2c, addr: int = 0x68):
        self._i2c  = i2c
        self._addr = addr

    # ── BCD helpers ───────────────────────────────────────────

    @staticmethod
    def _bcd_to_dec(bcd: int) -> int:
        """Convert BCD byte → normal integer.  0x59 → 59"""
        return (bcd >> 4) * 10 + (bcd & 0x0F)

    @staticmethod
    def _dec_to_bcd(dec: int) -> int:
        """Convert normal integer → BCD byte.  59 → 0x59"""
        return ((dec // 10) << 4) | (dec % 10)

    # ── Register access ───────────────────────────────────────

    def _read_reg(self, reg: int, n: int = 1) -> bytes:
        """Read n bytes starting at register address reg."""
        return self._i2c.write_then_read(self._addr, bytes([reg]), n)

    def _write_reg(self, reg: int, *values):
        """Write one or more bytes starting at register address reg."""
        self._i2c.write(self._addr, bytes([reg]) + bytes(values))

    # ── Time read / write ─────────────────────────────────────

    def get_time(self) -> tuple:
        """
        Read the current time from the RTC.

        Returns
        -------
        (year, month, day, hour, minute, second)
        All values are normal integers (not BCD).
        """
        raw = self._read_reg(0x00, 7)   # read 7 bytes starting at 0x00
        second  = self._bcd_to_dec(raw[0] & 0x7F)   # mask out clock-halt bit
        minute  = self._bcd_to_dec(raw[1])
        hour    = self._bcd_to_dec(raw[2] & 0x3F)   # mask out 12/24-hour bit
        # raw[3] = weekday (1-7), skip
        day     = self._bcd_to_dec(raw[4])
        month   = self._bcd_to_dec(raw[5] & 0x1F)   # mask out century bit
        year    = self._bcd_to_dec(raw[6]) + 2000    # DS3231 stores 0-99

        return year, month, day, hour, minute, second

    def set_time(self, year: int, month: int, day: int,
                 hour: int, minute: int, second: int):
        """
        Set the RTC to a specific date and time.

        Parameters
        ----------
        year   : full year e.g. 2024
        month  : 1-12
        day    : 1-31
        hour   : 0-23
        minute : 0-59
        second : 0-59
        """
        # Weekday: compute from date (simple formula)
        import utime
        # Zeller's congruence (simplified) – just use 1 if unsure
        weekday = 1   # Monday=1, Sunday=7 (not critical for most uses)

        self._write_reg(
            0x00,                               # start at register 0
            self._dec_to_bcd(second),
            self._dec_to_bcd(minute),
            self._dec_to_bcd(hour),
            weekday,
            self._dec_to_bcd(day),
            self._dec_to_bcd(month),
            self._dec_to_bcd(year - 2000),      # store 0-99
        )

    def get_time_str(self) -> str:
        """Return time as human-readable string: '2024-06-15 14:30:00'"""
        y, mo, d, h, mi, s = self.get_time()
        return f"{y:04d}-{mo:02d}-{d:02d} {h:02d}:{mi:02d}:{s:02d}"

    def get_date_str(self) -> str:
        """Return date only: '2024-06-15'"""
        y, mo, d, *_ = self.get_time()
        return f"{y:04d}-{mo:02d}-{d:02d}"

    def get_clock_str(self) -> str:
        """Return time only: '14:30:00'"""
        _, _, _, h, mi, s = self.get_time()
        return f"{h:02d}:{mi:02d}:{s:02d}"

    # ── Temperature sensor ────────────────────────────────────

    def get_temperature(self) -> float:
        """
        Read the built-in temperature sensor (±3°C accuracy).
        The DS3231 has a thermometer used to compensate its crystal.

        Returns temperature in degrees Celsius as a float.
        Resolution is 0.25°C.
        """
        raw = self._read_reg(0x11, 2)
        # MSB: integer part (signed byte)
        # LSB: upper 2 bits = fractional part (0.25°C each)
        integer  = raw[0] if raw[0] < 128 else raw[0] - 256   # handle negative
        fraction = (raw[1] >> 6) * 0.25
        return integer + fraction

    # ── Alarm (basic) ─────────────────────────────────────────

    def set_alarm1_seconds(self, every_n_seconds: int = 0):
        """
        Set Alarm 1 to fire every N seconds (0 = every second).
        Useful for waking a sleeping microcontroller on a timer.
        Note: you must clear the alarm flag after it fires.
        """
        self._write_reg(0x07, self._dec_to_bcd(every_n_seconds) | 0x80)
        self._write_reg(0x08, 0x80)   # match any minute
        self._write_reg(0x09, 0x80)   # match any hour
        self._write_reg(0x0A, 0x80)   # match any day
        # Enable alarm 1 interrupt in control register
        ctrl = self._read_reg(0x0E, 1)[0]
        self._write_reg(0x0E, ctrl | 0x05)

    def clear_alarm(self):
        """Clear alarm flags so the alarm can fire again."""
        status = self._read_reg(0x0F, 1)[0]
        self._write_reg(0x0F, status & 0xFC)   # clear A1F and A2F bits
