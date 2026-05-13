from machine import Pin, I2C
import time

# ============================================================
#  ESP32 I2C LIBRARY
#  Supports: Read, Write, Register R/W, Scan, Multi-bus,
#            Bit manipulation, Soft I2C
# ============================================================

_buses = {}     # { bus_id: I2C instance }

# Default bus config
_config = {
    "sda"    : 21,
    "scl"    : 22,
    "freq"   : 400000,
    "i2c_id" : 0
}

# ---------- GLOBAL CONFIG ----------

def setPins(sda=21, scl=22, freq=400000, i2c_id=0):
    """Set default I2C bus pin and frequency configuration."""
    _config["sda"]    = sda
    _config["scl"]    = scl
    _config["freq"]   = freq
    _config["i2c_id"] = i2c_id

# ---------- BEGIN ----------

def begin(bus_id=None):
    """
    Initialize the I2C bus using the stored configuration.
    Optionally specify bus_id to manage multiple buses.
    """
    bid = bus_id if bus_id is not None else _config["i2c_id"]
    _buses[bid] = I2C(
        bid,
        scl=Pin(_config["scl"]),
        sda=Pin(_config["sda"]),
        freq=_config["freq"]
    )
    print(f"I2C Bus {bid} started (SDA={_config['sda']}, SCL={_config['scl']}, freq={_config['freq']})")
    return _buses[bid]

# ---------- SOFT I2C ----------

def beginSoft(sda_pin, scl_pin, freq=100000, bus_id="soft"):
    """
    Initialize a software (bit-bang) I2C bus on any GPIO pins.
    Useful when hardware I2C pins are occupied.
    """
    from machine import SoftI2C
    _buses[bus_id] = SoftI2C(
        scl=Pin(scl_pin),
        sda=Pin(sda_pin),
        freq=freq
    )
    print(f"Soft I2C started (SDA={sda_pin}, SCL={scl_pin})")
    return _buses[bus_id]

# ---------- GET BUS ----------

def _bus(bus_id=None):
    bid = bus_id if bus_id is not None else _config["i2c_id"]
    if bid not in _buses:
        raise RuntimeError(f"I2C bus {bid} not initialized. Call begin() first.")
    return _buses[bid]

# ---------- SCAN ----------

def scan(bus_id=None):
    """Scan for I2C devices and return list of addresses (also prints them)."""
    devices = _bus(bus_id).scan()
    if devices:
        for d in devices:
            print(f"I2C device found: 0x{d:02X} ({d})")
    else:
        print("No I2C devices found")
    return devices

# ---------- IS PRESENT ----------

def isPresent(addr, bus_id=None):
    """Return True if a device at addr responds on the bus."""
    return addr in _bus(bus_id).scan()

# ---------- WRITE ----------

def write(addr, data, bus_id=None):
    """Write bytes to a device address. data should be bytes or bytearray."""
    if isinstance(data, (int, list)):
        data = bytes(data if isinstance(data, list) else [data])
    _bus(bus_id).writeto(addr, data)

# ---------- READ ----------

def read(addr, size=1, bus_id=None):
    """Read size bytes from a device address. Returns bytes."""
    return _bus(bus_id).readfrom(addr, size)

# ---------- WRITE REGISTER ----------

def writeRegister(addr, reg, data, bus_id=None):
    """Write data to a specific register of a device."""
    if isinstance(data, int):
        data = bytes([data])
    elif isinstance(data, list):
        data = bytes(data)
    _bus(bus_id).writeto_mem(addr, reg, data)

# ---------- READ REGISTER ----------

def readRegister(addr, reg, size=1, bus_id=None):
    """Read size bytes from a specific register of a device."""
    return _bus(bus_id).readfrom_mem(addr, reg, size)

# ---------- READ REGISTER BYTE ----------

def readRegisterByte(addr, reg, bus_id=None):
    """Read a single byte from a register and return as integer."""
    return readRegister(addr, reg, 1, bus_id)[0]

# ---------- READ REGISTER WORD ----------

def readRegisterWord(addr, reg, big_endian=True, bus_id=None):
    """Read two bytes from a register and return as a 16-bit integer."""
    data = readRegister(addr, reg, 2, bus_id)
    if big_endian:
        return (data[0] << 8) | data[1]
    else:
        return (data[1] << 8) | data[0]

# ---------- SET BITS ----------

def setBits(addr, reg, mask, bus_id=None):
    """Set specific bits in a register (bitwise OR with mask)."""
    current = readRegisterByte(addr, reg, bus_id)
    writeRegister(addr, reg, current | mask, bus_id)

# ---------- CLEAR BITS ----------

def clearBits(addr, reg, mask, bus_id=None):
    """Clear specific bits in a register (bitwise AND with inverted mask)."""
    current = readRegisterByte(addr, reg, bus_id)
    writeRegister(addr, reg, current & (~mask & 0xFF), bus_id)

# ---------- WRITE THEN READ ----------

def writeRead(addr, write_data, read_size, bus_id=None):
    """Write data then read response (combined transaction)."""
    b = _bus(bus_id)
    if isinstance(write_data, (int, list)):
        write_data = bytes(write_data if isinstance(write_data, list) else [write_data])
    b.writeto(addr, write_data, False)  # no stop bit
    return b.readfrom(addr, read_size)
