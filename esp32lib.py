from machine import Pin
from machine import ADC
from machine import UART
from machine import I2C
from machine import SPI
import network
import time

# ============================================================
# DIGITAL
# ============================================================

INPUT = 0
OUTPUT = 1

_pins = {}

def pinMode(pin, mode):

    if mode == OUTPUT:

        _pins[pin] = Pin(pin, Pin.OUT)

    else:

        _pins[pin] = Pin(pin, Pin.IN)

def digitalWrite(pin, value):

    _pins[pin].value(value)

def digitalRead(pin):

    return _pins[pin].value()

# ============================================================
# ANALOG
# ============================================================

_adcs = {}

def analogPin(pin,
              attn=ADC.ATTN_11DB):

    adc = ADC(Pin(pin))

    adc.atten(attn)

    _adcs[pin] = adc

def analogRead(pin):

    return _adcs[pin].read()

def analogPercent(pin):

    raw = analogRead(pin)

    return int((raw / 4095) * 100)

def analogVoltage(pin):

    raw = analogRead(pin)

    return round((raw / 4095) * 3.3, 2)

# ============================================================
# WIFI
# ============================================================

wifi = network.WLAN(network.STA_IF)

def connectWiFi(ssid, password):

    wifi.active(True)

    if not wifi.isconnected():

        print("Connecting WiFi...")

        wifi.connect(ssid, password)

        while not wifi.isconnected():

            time.sleep(1)

    print("WiFi Connected")

    print(wifi.ifconfig())

# ============================================================
# SERIAL UART
# ============================================================

_uart = None

def serialBegin(
        baudrate=115200,
        tx=17,
        rx=16,
        uart_id=2):

    global _uart

    _uart = UART(
        uart_id,
        baudrate=baudrate,
        tx=tx,
        rx=rx
    )

    print("UART Started")

def serialPrint(data):

    _uart.write(str(data))

def serialPrintln(data):

    _uart.write(str(data) + "\n")

def serialRead():

    if _uart.any():

        return _uart.read().decode().strip()

    return None

# ============================================================
# I2C
# ============================================================

_i2c = None

def i2cBegin(
        sda=21,
        scl=22,
        freq=400000,
        i2c_id=0):

    global _i2c

    _i2c = I2C(
        i2c_id,
        sda=Pin(sda),
        scl=Pin(scl),
        freq=freq
    )

    print("I2C Started")

def i2cScan():

    devices = _i2c.scan()

    for d in devices:

        print("Found:", hex(d))

    return devices

def i2cWrite(addr, data):

    _i2c.writeto(addr, data)

def i2cRead(addr, size=1):

    return _i2c.readfrom(addr, size)

# ============================================================
# SPI
# ============================================================

_spi = None
_cs = None

def spiBegin(
        sck=18,
        mosi=23,
        miso=19,
        cs=5,
        baudrate=1000000,
        spi_id=1):

    global _spi
    global _cs

    _spi = SPI(
        spi_id,
        baudrate=baudrate,
        polarity=0,
        phase=0,
        sck=Pin(sck),
        mosi=Pin(mosi),
        miso=Pin(miso)
    )

    _cs = Pin(cs, Pin.OUT)

    _cs.value(1)

    print("SPI Started")

def spiWrite(data):

    _cs.value(0)

    _spi.write(data)

    _cs.value(1)

def spiRead(size=1):

    _cs.value(0)

    data = _spi.read(size)

    _cs.value(1)

    return data
