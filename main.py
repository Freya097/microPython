# ============================================================
#  ESP32 SMART AIR QUALITY MONITOR
#  Example main.py — uses all 7 library modules
#
#  Hardware:
#    MQ-135 Air Quality Sensor  → GPIO 34  (Analog)
#    Buzzer                     → GPIO 25  (Digital + PWM)
#    Status LED                 → GPIO 2   (Digital + PWM)
#    Relay (exhaust fan)        → GPIO 12  (Digital)
#    OLED SSD1306 (I2C 128x64) → SDA=21, SCL=22
#    SPI Flash / SD Card        → SCK=18, MOSI=23, MISO=19, CS=5
#    Serial debug monitor       → TX=17, RX=16  (UART2)
#    WiFi → send readings to a REST API every 30 s
# ============================================================

import digital
import analog
import i2c
import spi
import serialport
import wifi
import time

# ============================================================
#  CONFIGURATION
# ============================================================

# WiFi
WIFI_SSID     = "YOUR_WIFI_SSID"
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"
API_URL       = "http://api.example.com/air"   # Replace with your endpoint

# Pin assignments
PIN_AIR_QUALITY = 34   # MQ-135 ADC
PIN_BUZZER      = 25   # Buzzer (PWM) — also a DAC pin
PIN_LED         = 2    # Onboard LED
PIN_RELAY       = 12   # Fan relay

# Thresholds
WARN_THRESHOLD     = 40   # % — amber warning
DANGER_THRESHOLD   = 65   # % — red alarm, relay ON, buzzer ON
CLEAR_THRESHOLD    = 30   # % — below this: all clear

# I2C OLED address (SSD1306)
OLED_ADDR = 0x3C

# How often to send data to the cloud (seconds)
CLOUD_INTERVAL = 30

# ============================================================
#  INIT: SERIAL
# ============================================================

serialport.setPins(tx=17, rx=16, baudrate=115200, uart_id=2)
serialport.begin()
serialport.println("=== ESP32 Air Quality Monitor ===")

# ============================================================
#  INIT: WIFI
# ============================================================

wifi.setWiFi(WIFI_SSID, WIFI_PASSWORD, hostname="air-monitor", timeout=15)
connected = wifi.connect()

if connected:
    serialport.println(f"WiFi IP: {wifi.ip()}")
else:
    serialport.println("WiFi FAILED — running offline")

# ============================================================
#  INIT: I2C  (OLED display SSD1306)
# ============================================================

i2c.setPins(sda=21, scl=22, freq=400000, i2c_id=0)
i2c.begin()

# Quick scan — print found devices over serial
devices = i2c.scan()
if OLED_ADDR in devices:
    serialport.println(f"OLED found at 0x{OLED_ADDR:02X}")

    # SSD1306 minimal init sequence
    init_cmds = [
        0xAE,        # display off
        0xD5, 0x80,  # set display clock divide
        0xA8, 0x3F,  # set multiplex
        0xD3, 0x00,  # set display offset
        0x40,        # set start line
        0x8D, 0x14,  # charge pump ON
        0x20, 0x00,  # horizontal addressing
        0xA1,        # segment remap
        0xC8,        # COM scan direction
        0xDA, 0x12,  # set COM pins
        0x81, 0xCF,  # set contrast
        0xD9, 0xF1,  # pre-charge period
        0xDB, 0x40,  # VCOMH deselect
        0xA4,        # resume from RAM
        0xA6,        # normal display
        0xAF,        # display on
    ]
    for cmd in init_cmds:
        i2c.write(OLED_ADDR, bytes([0x00, cmd]))   # 0x00 = command mode

    serialport.println("OLED initialized")
else:
    serialport.println("OLED not found — display skipped")
    OLED_ADDR = None

# ============================================================
#  INIT: SPI  (SD Card / external flash)
# ============================================================

spi.setPins(sck=18, mosi=23, miso=19, cs=5, baudrate=4000000, spi_id=1)
spi.begin()

# Send a dummy clock pulse to wake SD card
spi.deselect()
spi.write(bytes([0xFF] * 10))
serialport.println("SPI bus ready")

# ============================================================
#  INIT: DIGITAL
# ============================================================

digital.pinMode(PIN_RELAY, digital.OUTPUT)
digital.pinMode(PIN_LED,   digital.OUTPUT)

digital.pwmSetup(PIN_BUZZER, freq=2000)   # 2 kHz buzzer tone
digital.pwmSetup(PIN_LED,    freq=500)    # LED brightness control

digital.digitalWrite(PIN_RELAY, 0)        # Fan OFF
digital.pwmWrite(PIN_BUZZER, 0)           # Buzzer silent
digital.pwmWritePercent(PIN_LED, 10)      # LED dim (standby)

# ============================================================
#  INIT: ANALOG
# ============================================================

analog.analogPin(PIN_AIR_QUALITY)   # MQ-135, full 3.3V range
serialport.println("Sensors initialized")

# ============================================================
#  HELPERS
# ============================================================

last_cloud_send = time.ticks_ms()
alert_state     = "clear"   # "clear", "warn", "danger"
reading_count   = 0

def classify(percent):
    """Return status string based on air quality percent."""
    if percent >= DANGER_THRESHOLD:
        return "danger"
    elif percent >= WARN_THRESHOLD:
        return "warn"
    else:
        return "clear"

def update_outputs(status, pct):
    """Drive LED brightness, buzzer, and relay based on alert status."""
    if status == "clear":
        digital.pwmWritePercent(PIN_LED, 10)    # dim green
        digital.pwmWrite(PIN_BUZZER, 0)          # silent
        digital.digitalWrite(PIN_RELAY, 0)       # fan off

    elif status == "warn":
        # Pulsing LED (50% brightness)
        digital.pwmWritePercent(PIN_LED, 50)
        digital.pwmWrite(PIN_BUZZER, 0)          # no buzzer yet
        digital.digitalWrite(PIN_RELAY, 0)       # fan still off

    elif status == "danger":
        digital.pwmWritePercent(PIN_LED, 100)    # full brightness
        digital.pwmWrite(PIN_BUZZER, 512)         # 50% duty — loud
        digital.digitalWrite(PIN_RELAY, 1)        # fan ON

def send_to_cloud(pct, voltage, status):
    """POST a JSON reading to the REST API."""
    import json as _json
    payload = _json.dumps({
        "device"   : wifi.ip() or "offline",
        "reading"  : pct,
        "voltage"  : voltage,
        "status"   : status,
        "rssi"     : wifi.rssi(),
        "uptime_s" : time.ticks_ms() // 1000,
    })
    code, resp = wifi.httpPost(API_URL, body=payload)
    if code == 200 or code == 201:
        serialport.println(f"Cloud OK ({code})")
    else:
        serialport.println(f"Cloud ERR: {code} — {resp[:60]}")

def log_to_spi_flash(pct, status):
    """
    Write a compact CSV log entry to SPI flash/SD card.
    Format: timestamp_ms,percent,status\\n
    This is a placeholder — real SD card needs SPI SD library.
    """
    ts    = time.ticks_ms()
    entry = f"{ts},{pct},{status}\n".encode()
    spi.write(entry)           # Send raw bytes to SPI device

# ============================================================
#  BUTTON (optional): GPIO 0 = BOOT button for manual scan
# ============================================================

digital.pinMode(0, digital.INPUT_PULLUP)

def on_button_press(pin):
    serialport.println("Button: running WiFi scan...")
    wifi.scan()

digital.attachInterrupt(0, on_button_press,
                        trigger=digital.FALLING,
                        debounce_ms=200)

# ============================================================
#  MAIN LOOP
# ============================================================

serialport.println("Starting main loop...")
digital.blink(PIN_LED, times=3, on_ms=100, off_ms=100)  # Ready signal

while True:

    # --- Keep WiFi alive ---
    wifi.keepAlive()

    # --- Read sensor (average 8 samples for stability) ---
    raw_pct  = analog.analogAveragePercent(PIN_AIR_QUALITY, samples=8)
    voltage  = analog.analogVoltage(PIN_AIR_QUALITY)
    smooth   = analog.analogSmooth(PIN_AIR_QUALITY, window=10)
    smooth_pct = analog.mapValue(smooth, 0, 4095, 0, 100)

    # --- Classify ---
    new_status = classify(smooth_pct)

    # --- Update hardware outputs ---
    update_outputs(new_status, smooth_pct)

    # --- Check I2C sensor (example: read temperature register from a device) ---
    if OLED_ADDR and i2c.isPresent(OLED_ADDR):
        # In a real project, send pixel data to OLED here
        pass

    # --- Serial debug output ---
    reading_count += 1
    serialport.println(
        f"[{reading_count}] Raw%={raw_pct} Smooth%={smooth_pct} "
        f"V={voltage}V Status={new_status} RSSI={wifi.rssi()}dBm"
    )

    # --- JSON output on serial (useful for a Pi/PC receiving structured data) ---
    serialport.writeJSON({
        "n" : reading_count,
        "p" : smooth_pct,
        "v" : voltage,
        "s" : new_status,
    })

    # --- SPI logging ---
    if reading_count % 5 == 0:           # log every 5th reading
        log_to_spi_flash(smooth_pct, new_status)

    # --- Cloud send (every CLOUD_INTERVAL seconds) ---
    now = time.ticks_ms()
    if time.ticks_diff(now, last_cloud_send) >= CLOUD_INTERVAL * 1000:
        if wifi.isConnected():
            send_to_cloud(smooth_pct, voltage, new_status)
        last_cloud_send = now

    # --- Alert state change message ---
    if new_status != alert_state:
        serialport.println(f"*** STATUS CHANGE: {alert_state} -> {new_status} ***")
        alert_state = new_status

    # --- PWM demo: ramp LED brightness with air quality level ---
    digital.pwmWritePercent(PIN_LED, max(5, smooth_pct))

    time.sleep(1)
