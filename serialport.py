from machine import UART, Pin
import time

# ============================================================
#  ESP32 SERIAL / UART LIBRARY
#  Supports: Multi-UART, Read/Write, Readline, JSON, Timeout,
#            RS485 Direction Control, Binary Packets
# ============================================================

_uarts  = {}   # { uart_id: UART instance }
_rs485  = {}   # { uart_id: DE/RE Pin instance }

_config = {
    "tx"       : 17,
    "rx"       : 16,
    "baudrate" : 115200,
    "uart_id"  : 2,
    "bits"     : 8,
    "parity"   : None,
    "stop"     : 1,
    "timeout"  : 1000,
}

# ---------- GLOBAL CONFIG ----------

def setPins(tx=17, rx=16, baudrate=115200, uart_id=2,
            bits=8, parity=None, stop=1, timeout=1000):
    """Configure UART parameters."""
    _config["tx"]       = tx
    _config["rx"]       = rx
    _config["baudrate"] = baudrate
    _config["uart_id"]  = uart_id
    _config["bits"]     = bits
    _config["parity"]   = parity
    _config["stop"]     = stop
    _config["timeout"]  = timeout

# ---------- BEGIN ----------

def begin(uart_id=None):
    """Initialize UART using the stored configuration."""
    uid = uart_id if uart_id is not None else _config["uart_id"]
    _uarts[uid] = UART(
        uid,
        baudrate = _config["baudrate"],
        tx       = _config["tx"],
        rx       = _config["rx"],
        bits     = _config["bits"],
        parity   = _config["parity"],
        stop     = _config["stop"],
        timeout  = _config["timeout"],
    )
    print(f"UART{uid} started at {_config['baudrate']} baud (TX={_config['tx']}, RX={_config['rx']})")
    return _uarts[uid]

# ---------- RS485 MODE ----------

def enableRS485(de_re_pin, uart_id=None):
    """
    Enable RS485 half-duplex mode using a Direction Enable pin (DE/RE).
    Pin goes HIGH before transmit, LOW after transmit.
    """
    uid = uart_id if uart_id is not None else _config["uart_id"]
    _rs485[uid] = Pin(de_re_pin, Pin.OUT)
    _rs485[uid].value(0)  # receive mode by default
    print(f"RS485 mode enabled on UART{uid} with DE/RE pin {de_re_pin}")

# ---------- GET UART ----------

def _uart(uart_id=None):
    uid = uart_id if uart_id is not None else _config["uart_id"]
    if uid not in _uarts:
        raise RuntimeError(f"UART{uid} not initialized. Call begin() first.")
    return _uarts[uid], uid

# ---------- WRITE ----------

def write(data, uart_id=None):
    """Write raw string or bytes to UART."""
    u, uid = _uart(uart_id)
    if uid in _rs485:
        _rs485[uid].value(1)
        time.sleep_us(100)
    if isinstance(data, str):
        u.write(data.encode())
    else:
        u.write(data)
    if uid in _rs485:
        time.sleep_us(100)
        _rs485[uid].value(0)

# ---------- WRITE BYTES ----------

def writeBytes(data_list, uart_id=None):
    """Write a list of integers as raw bytes."""
    write(bytes(data_list), uart_id)

# ---------- PRINTLN ----------

def println(data, uart_id=None):
    """Write data followed by newline."""
    write(str(data) + "\n", uart_id)

# ---------- PRINT ----------

def print_(data, uart_id=None):
    """Write data without newline."""
    write(str(data), uart_id)

# ---------- READ ----------

def read(size=None, uart_id=None):
    """Read available bytes. Returns decoded string or None."""
    u, _ = _uart(uart_id)
    if u.any():
        raw = u.read(size) if size else u.read()
        if raw:
            try:
                return raw.decode("utf-8").strip()
            except:
                return raw  # return raw bytes if decode fails
    return None

# ---------- READ BYTES ----------

def readBytes(size, uart_id=None):
    """Read exactly size raw bytes. Returns bytes or None."""
    u, _ = _uart(uart_id)
    return u.read(size)

# ---------- READ LINE ----------

def readLine(timeout_ms=500, uart_id=None):
    """
    Read until newline character or timeout.
    Returns the line as a string (without \\n), or None on timeout.
    """
    u, _ = _uart(uart_id)
    buf   = b""
    start = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), start) < timeout_ms:
        if u.any():
            ch = u.read(1)
            if ch == b"\n":
                return buf.decode("utf-8").strip()
            buf += ch
        time.sleep_ms(1)
    return buf.decode("utf-8").strip() if buf else None

# ---------- READ UNTIL ----------

def readUntil(terminator=b"\n", max_bytes=256, uart_id=None):
    """Read bytes until a terminator sequence is found or max_bytes reached."""
    u, _ = _uart(uart_id)
    buf = b""
    while len(buf) < max_bytes:
        if u.any():
            ch = u.read(1)
            buf += ch
            if buf.endswith(terminator):
                return buf[:-len(terminator)]
    return buf

# ---------- READ JSON ----------

def readJSON(timeout_ms=500, uart_id=None):
    """
    Read a newline-terminated line and parse it as JSON.
    Returns a dict/list on success, None on failure.
    """
    import json
    line = readLine(timeout_ms, uart_id)
    if line:
        try:
            return json.loads(line)
        except:
            return None
    return None

# ---------- WRITE JSON ----------

def writeJSON(data, uart_id=None):
    """Serialize a dict/list as JSON and send it with a newline."""
    import json
    println(json.dumps(data), uart_id)

# ---------- AVAILABLE ----------

def available(uart_id=None):
    """Return number of bytes waiting in the receive buffer."""
    u, _ = _uart(uart_id)
    return u.any()

# ---------- FLUSH ----------

def flush(uart_id=None):
    """Discard all bytes currently in the receive buffer."""
    u, _ = _uart(uart_id)
    while u.any():
        u.read(u.any())

# ---------- CHANGE BAUDRATE ----------

def setBaudrate(baudrate, uart_id=None):
    """Change baud rate (reinitializes the UART)."""
    _config["baudrate"] = baudrate
    begin(uart_id)
