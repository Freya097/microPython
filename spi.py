from machine import Pin, SPI, SoftSPI
import time

# ============================================================
#  ESP32 SPI LIBRARY
#  Supports: Hardware SPI, Soft SPI, Multi-CS, DMA transfers,
#            Mode 0/1/2/3, MSB/LSB, Loopback test
# ============================================================

_buses = {}    # { bus_id: SPI instance }
_cs    = {}    # { cs_alias: Pin instance }

_config = {
    "sck"     : 18,
    "mosi"    : 23,
    "miso"    : 19,
    "cs"      : 5,
    "baudrate": 1000000,
    "spi_id"  : 1,
    "polarity": 0,
    "phase"   : 0,
    "bits"    : 8,
    "firstbit": SPI.MSB
}

# ---------- GLOBAL CONFIG ----------

def setPins(sck=18, mosi=23, miso=19, cs=5,
            baudrate=1000000, spi_id=1,
            polarity=0, phase=0,
            bits=8, firstbit=None):
    """Set SPI bus parameters. firstbit: SPI.MSB or SPI.LSB."""
    _config["sck"]      = sck
    _config["mosi"]     = mosi
    _config["miso"]     = miso
    _config["cs"]       = cs
    _config["baudrate"] = baudrate
    _config["spi_id"]   = spi_id
    _config["polarity"] = polarity
    _config["phase"]    = phase
    _config["bits"]     = bits
    _config["firstbit"] = firstbit if firstbit is not None else SPI.MSB

# ---------- BEGIN ----------

def begin(bus_id=None):
    """Initialize hardware SPI using the stored configuration."""
    bid = bus_id if bus_id is not None else _config["spi_id"]
    _buses[bid] = SPI(
        bid,
        baudrate  = _config["baudrate"],
        polarity  = _config["polarity"],
        phase     = _config["phase"],
        bits      = _config["bits"],
        firstbit  = _config["firstbit"],
        sck       = Pin(_config["sck"]),
        mosi      = Pin(_config["mosi"]),
        miso      = Pin(_config["miso"])
    )
    # Default CS
    cs_key = f"cs_{bid}"
    _cs[cs_key] = Pin(_config["cs"], Pin.OUT)
    _cs[cs_key].value(1)
    print(f"SPI Bus {bid} started at {_config['baudrate']} baud")
    return _buses[bid]

# ---------- SOFT SPI ----------

def beginSoft(sck_pin, mosi_pin, miso_pin, cs_pin,
              baudrate=500000, bus_id="soft"):
    """
    Initialize software (bit-bang) SPI on any GPIO pins.
    """
    _buses[bus_id] = SoftSPI(
        baudrate = baudrate,
        sck      = Pin(sck_pin),
        mosi     = Pin(mosi_pin),
        miso     = Pin(miso_pin)
    )
    _cs[f"cs_{bus_id}"] = Pin(cs_pin, Pin.OUT)
    _cs[f"cs_{bus_id}"].value(1)
    print(f"Soft SPI started (SCK={sck_pin}, MOSI={mosi_pin}, MISO={miso_pin}, CS={cs_pin})")
    return _buses[bus_id]

# ---------- ADD CS PIN ----------

def addCS(alias, pin):
    """Register an additional chip-select pin under an alias string."""
    _cs[alias] = Pin(pin, Pin.OUT)
    _cs[alias].value(1)

# ---------- INTERNAL HELPERS ----------

def _get_bus(bus_id=None):
    bid = bus_id if bus_id is not None else _config["spi_id"]
    if bid not in _buses:
        raise RuntimeError(f"SPI bus {bid} not initialized. Call begin() first.")
    return _buses[bid]

def _get_cs(bus_id=None, cs_alias=None):
    if cs_alias and cs_alias in _cs:
        return _cs[cs_alias]
    bid = bus_id if bus_id is not None else _config["spi_id"]
    key = f"cs_{bid}"
    return _cs.get(key)

# ---------- SELECT ----------

def select(bus_id=None, cs_alias=None):
    """Assert CS low (select device)."""
    cs = _get_cs(bus_id, cs_alias)
    if cs:
        cs.value(0)

# ---------- DESELECT ----------

def deselect(bus_id=None, cs_alias=None):
    """Deassert CS high (deselect device)."""
    cs = _get_cs(bus_id, cs_alias)
    if cs:
        cs.value(1)

# ---------- WRITE ----------

def write(data, bus_id=None, cs_alias=None):
    """Write bytes to SPI. Asserts/deasserts CS automatically."""
    bus = _get_bus(bus_id)
    if isinstance(data, (int, list)):
        data = bytes(data if isinstance(data, list) else [data])
    select(bus_id, cs_alias)
    bus.write(data)
    deselect(bus_id, cs_alias)

# ---------- READ ----------

def read(size=1, write_byte=0x00, bus_id=None, cs_alias=None):
    """Read size bytes from SPI (sends write_byte as clock filler)."""
    bus = _get_bus(bus_id)
    select(bus_id, cs_alias)
    data = bus.read(size, write_byte)
    deselect(bus_id, cs_alias)
    return data

# ---------- WRITE READ ----------

def writeRead(data, bus_id=None, cs_alias=None):
    """Full-duplex: write data bytes and simultaneously read the same number of bytes."""
    bus = _get_bus(bus_id)
    if isinstance(data, (int, list)):
        data = bytes(data if isinstance(data, list) else [data])
    buf = bytearray(len(data))
    select(bus_id, cs_alias)
    bus.write_readinto(data, buf)
    deselect(bus_id, cs_alias)
    return bytes(buf)

# ---------- TRANSFER INTO BUFFER ----------

def transfer(tx_buf, rx_buf, bus_id=None, cs_alias=None):
    """
    Full-duplex transfer into a pre-allocated rx_buf.
    tx_buf and rx_buf must be the same length (bytearray).
    """
    bus = _get_bus(bus_id)
    select(bus_id, cs_alias)
    bus.write_readinto(tx_buf, rx_buf)
    deselect(bus_id, cs_alias)

# ---------- WRITE REGISTER ----------

def writeRegister(reg, data, bus_id=None, cs_alias=None):
    """Write to a device register (sends reg byte then data bytes)."""
    if isinstance(data, int):
        payload = bytes([reg, data])
    elif isinstance(data, list):
        payload = bytes([reg] + data)
    else:
        payload = bytes([reg]) + data
    write(payload, bus_id, cs_alias)

# ---------- READ REGISTER ----------

def readRegister(reg, size=1, bus_id=None, cs_alias=None):
    """Read from a device register (sends reg byte, reads size bytes)."""
    bus = _get_bus(bus_id)
    buf = bytearray(1 + size)
    buf[0] = reg | 0x80  # common read flag convention
    rx  = bytearray(1 + size)
    select(bus_id, cs_alias)
    bus.write_readinto(buf, rx)
    deselect(bus_id, cs_alias)
    return bytes(rx[1:])

# ---------- LOOPBACK TEST ----------

def loopbackTest(bus_id=None):
    """
    Basic loopback sanity test. Connect MISO to MOSI externally.
    Sends a known pattern and checks if it comes back.
    """
    test_data = bytes([0xA5, 0x5A, 0xF0, 0x0F])
    result    = writeRead(test_data, bus_id)
    passed    = result == test_data
    print(f"SPI Loopback: {'PASS' if passed else 'FAIL'} (sent={list(test_data)}, got={list(result)})")
    return passed

# ---------- CHANGE BAUDRATE ----------

def setBaudrate(baudrate, bus_id=None):
    """Reinitialize the SPI bus at a new baudrate."""
    _config["baudrate"] = baudrate
    begin(bus_id)
