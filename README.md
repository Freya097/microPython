# microPython
# ESP32 MicroPython Custom Library
## Complete Hardware Abstraction Layer for ESP32

All 7 modules drop onto your ESP32 alongside `main.py` via Thonny, ampy, or rshell.

---

## Module Overview

| File | Purpose | New Features Added |
|---|---|---|
| `digital.py` | GPIO, PWM, Interrupts | PWM %, toggle, pulse, blink, debounced IRQ |
| `analog.py` | ADC, DAC | Averaging, smoothing, voltage, DAC write |
| `i2c.py` | I2C bus | Multi-bus, SoftI2C, bit ops, word read |
| `spi.py` | SPI bus | Multi-CS, SoftSPI, register R/W, loopback |
| `serialport.py` | UART / Serial | Readline, JSON, RS485, multi-UART, flush |
| `wifi.py` | WiFi + HTTP | HTTP GET/POST, UDP, AP mode, scan, keepAlive |
| `main.py` | Example project | Smart Air Quality Monitor |

---

## Quick Reference

### digital.py
```python
import digital

digital.pinMode(pin, digital.OUTPUT)
digital.pinMode(pin, digital.INPUT_PULLUP)
digital.digitalWrite(pin, 1)
val = digital.digitalRead(pin)
digital.togglePin(pin)
digital.pulse(pin, duration_ms=200)
digital.blink(pin, times=5, on_ms=100, off_ms=100)

# PWM
digital.pwmSetup(pin, freq=1000)
digital.pwmWrite(pin, 512)           # 0–1023
digital.pwmWritePercent(pin, 75)     # 0–100%
digital.pwmFreq(pin, 5000)
digital.pwmStop(pin)

# Interrupts (with debounce)
digital.attachInterrupt(pin, callback, trigger=digital.RISING, debounce_ms=50)
digital.detachInterrupt(pin)
```

### analog.py
```python
import analog

analog.analogPin(pin)                         # default: 12-bit, 0–3.6V
analog.analogPin(pin, attn=analog.ATTN_6DB)  # custom attenuation
raw   = analog.analogRead(pin)               # 0–4095
pct   = analog.analogPercent(pin)            # 0–100
volts = analog.analogVoltage(pin)            # 0.0–3.3 V
avg   = analog.analogAverage(pin, samples=16)
smooth = analog.analogSmooth(pin, window=10) # call in loop
mapped = analog.mapValue(raw, 0, 4095, 0, 100)
fval   = analog.mapFloat(raw, 0, 4095, 0.0, 5.0)

# DAC (GPIO 25 or 26 only)
analog.dacPin(25)
analog.dacWrite(25, 128)             # 0–255
analog.dacWriteVoltage(25, 1.65)     # target voltage
analog.dacWritePercent(25, 50)       # 0–100%
```

### i2c.py
```python
import i2c

i2c.setPins(sda=21, scl=22, freq=400000, i2c_id=0)
i2c.begin()

# Soft I2C on any pins
i2c.beginSoft(sda_pin=4, scl_pin=5)

devices = i2c.scan()
present  = i2c.isPresent(0x3C)

i2c.write(addr, bytes([0x00, 0xAE]))
data = i2c.read(addr, size=2)

i2c.writeRegister(addr, reg, value)
raw  = i2c.readRegister(addr, reg, size=2)
byte = i2c.readRegisterByte(addr, reg)
word = i2c.readRegisterWord(addr, reg, big_endian=True)

i2c.setBits(addr, reg, 0b00000100)   # set bit 2
i2c.clearBits(addr, reg, 0b00000100) # clear bit 2
```

### spi.py
```python
import spi

spi.setPins(sck=18, mosi=23, miso=19, cs=5, baudrate=4000000)
spi.begin()

# Soft SPI
spi.beginSoft(sck_pin=14, mosi_pin=13, miso_pin=12, cs_pin=15)

# Multiple CS pins
spi.addCS("device2", pin=4)

spi.write(bytes([0x01, 0x02]))
data = spi.read(4)
resp = spi.writeRead(bytes([0x80, 0x00]))   # full-duplex

spi.writeRegister(0x10, 0xFF)
reg_data = spi.readRegister(0x10, size=2)

spi.loopbackTest()            # wiring sanity check
spi.setBaudrate(8000000)      # change speed
```

### serialport.py
```python
import serialport

serialport.setPins(tx=17, rx=16, baudrate=115200, uart_id=2)
serialport.begin()

serialport.println("hello")         # with newline
serialport.print_("data: ")         # no newline
serialport.writeBytes([0x01, 0x02]) # raw bytes

line = serialport.readLine(timeout_ms=500)
data = serialport.read()
raw  = serialport.readBytes(4)
avail = serialport.available()
serialport.flush()

# JSON helpers
serialport.writeJSON({"temp": 25.3})
obj = serialport.readJSON()

# RS485 half-duplex
serialport.enableRS485(de_re_pin=4)

# Multi-UART
serialport.setPins(tx=1, rx=3, baudrate=9600, uart_id=1)
serialport.begin(uart_id=1)
serialport.println("hello", uart_id=1)
```

### wifi.py
```python
import wifi

wifi.setWiFi("SSID", "password", hostname="myesp32", timeout=15)
wifi.connect()
wifi.isConnected()   # True / False
wifi.ip()            # "192.168.1.x"
wifi.rssi()          # signal dBm
wifi.disconnect()
wifi.scan()          # print nearby networks

# Keep alive in main loop
wifi.keepAlive()     # auto-reconnect if dropped

# HTTP
code, body = wifi.httpGet("http://api.example.com/data")
code, resp = wifi.httpPost("http://api.example.com/ingest",
                            body='{"val":42}')

# UDP
wifi.udpSend("192.168.1.100", 5005, "hello")
data, addr = wifi.udpReceive(port=5005, timeout=5)

# Access Point mode
wifi.startAP("ESP32-AP", password="12345678")
wifi.stopAP()
```

---

## Example Project — main.py
The included `main.py` implements a **Smart Air Quality Monitor**:

- MQ-135 sensor read via **Analog** (averaged + smoothed)
- Status LED brightness via **PWM**
- Exhaust fan control via **Relay** (Digital)
- Buzzer alarm on danger level via **PWM**
- OLED status display via **I2C**
- Log entries to SPI flash / SD card via **SPI**
- Structured JSON debug output via **Serial**
- Readings POSTed to REST API every 30 s via **WiFi**
- Boot button interrupt (GPIO 0) triggers WiFi scan
- Auto-reconnect if WiFi drops

---

## Installation

Copy all `.py` files to the root of your ESP32 filesystem:
```
ampy --port /dev/ttyUSB0 put digital.py
ampy --port /dev/ttyUSB0 put analog.py
ampy --port /dev/ttyUSB0 put i2c.py
ampy --port /dev/ttyUSB0 put spi.py
ampy --port /dev/ttyUSB0 put serialport.py
ampy --port /dev/ttyUSB0 put wifi.py
ampy --port /dev/ttyUSB0 put main.py
```
Or use **Thonny IDE** → File → Save to MicroPython device.
