# ============================================================
#  tca9548a.py  –  I2C Multiplexer driver
#  TCA9548A = 1 bus IN → 8 buses OUT (channels 0-7)
# ============================================================
#
#  WHY YOU NEED THIS (student notes)
#  ──────────────────────────────────
#  Some devices have a fixed I2C address you cannot change.
#  If you have TWO SSD1306 OLEDs, they both live at 0x3C.
#  You can't talk to them individually on the same wire!
#
#  Solution: put them on different TCA9548A channels.
#  You tell the TCA "switch to channel 2" – now only the
#  device on channel 2 hears the bus.
#
#  TCA9548A default address: 0x70 (A0=A1=A2=GND)
#  Can be 0x70–0x77 depending on A0/A1/A2 pins.
#
#  Control register (1 byte):
#    bit 0 = channel 0 enable
#    bit 1 = channel 1 enable
#    …
#    bit 7 = channel 7 enable
#  (Multiple bits set = multiple channels open simultaneously)
#
# ============================================================


class TCA9548A:
    """
    Driver for the TCA9548A 8-channel I2C multiplexer.

    Usage
    -----
        from i2c_core  import I2CCore
        from tca9548a  import TCA9548A

        bus = I2CCore(sda_pin=21, scl_pin=22)
        mux = TCA9548A(bus, addr=0x70)

        mux.select(0)          # open channel 0 only
        # … talk to device on channel 0 …
        mux.close_all()        # disconnect all channels
    """

    def __init__(self, i2c, addr: int = 0x70):
        self._i2c   = i2c
        self._addr  = addr
        self._channel = None
        self.close_all()    # start with everything disconnected

    # ── Channel control ───────────────────────────────────────

    def select(self, channel: int):
        """
        Open a single channel (0-7) and close all others.

        Parameters
        ----------
        channel : int  0 to 7
        """
        if not 0 <= channel <= 7:
            raise ValueError(f"Channel must be 0-7, got {channel}")
        self._channel = channel
        # Write one byte: bit N set = channel N open
        self._i2c.write(self._addr, bytes([1 << channel]))

    def select_multi(self, channels: list):
        """
        Open multiple channels at once.
        Useful when you want devices on two channels to be addressable
        at the same time (they must have different addresses).

        Parameters
        ----------
        channels : list of ints  e.g. [0, 2, 5]
        """
        mask = 0
        for ch in channels:
            if not 0 <= ch <= 7:
                raise ValueError(f"Channel must be 0-7, got {ch}")
            mask |= (1 << ch)
        self._channel = None   # undefined when multiple open
        self._i2c.write(self._addr, bytes([mask]))

    def close_all(self):
        """Disconnect all channels. Good practice between operations."""
        self._channel = None
        self._i2c.write(self._addr, bytes([0x00]))

    def current_channel(self):
        """Return the last selected single channel (or None)."""
        return self._channel

    # ── Context manager support ───────────────────────────────
    # Lets you write:
    #   with mux.channel(3):
    #       oled.write(...)
    # and channels are automatically closed when the block ends.

    def channel(self, n: int):
        """Return a context manager for the given channel."""
        return _ChannelCtx(self, n)


class _ChannelCtx:
    """Helper context manager for TCA9548A.channel(n)."""

    def __init__(self, mux, n: int):
        self._mux = mux
        self._n   = n

    def __enter__(self):
        self._mux.select(self._n)
        return self._mux

    def __exit__(self, *args):
        self._mux.close_all()
