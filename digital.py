from machine import Pin, PWM
import time

# ============================================================
#  ESP32 DIGITAL I/O LIBRARY
#  Supports: Digital Read/Write, PWM, Interrupts, Debounce
# ============================================================

INPUT          = 0
OUTPUT         = 1
INPUT_PULLUP   = 2
INPUT_PULLDOWN = 3

RISING  = Pin.IRQ_RISING
FALLING = Pin.IRQ_FALLING
CHANGE  = Pin.IRQ_RISING | Pin.IRQ_FALLING

_pins     = {}
_pwm_pins = {}
_callbacks = {}
_debounce_ms = {}
_last_trigger = {}

# ---------- PIN MODE ----------

def pinMode(pin, mode):
    """Configure a GPIO pin as INPUT, OUTPUT, INPUT_PULLUP, or INPUT_PULLDOWN."""
    if mode == OUTPUT:
        _pins[pin] = Pin(pin, Pin.OUT)
    elif mode == INPUT_PULLUP:
        _pins[pin] = Pin(pin, Pin.IN, Pin.PULL_UP)
    elif mode == INPUT_PULLDOWN:
        _pins[pin] = Pin(pin, Pin.IN, Pin.PULL_DOWN)
    else:
        _pins[pin] = Pin(pin, Pin.IN)

# ---------- DIGITAL WRITE ----------

def digitalWrite(pin, value):
    """Write HIGH (1) or LOW (0) to a digital output pin."""
    _pins[pin].value(value)

# ---------- DIGITAL READ ----------

def digitalRead(pin):
    """Read current value (0 or 1) from a digital pin."""
    return _pins[pin].value()

# ---------- TOGGLE ----------

def togglePin(pin):
    """Toggle the current state of a digital output pin."""
    _pins[pin].value(not _pins[pin].value())

# ---------- PULSE ----------

def pulse(pin, duration_ms=100):
    """Emit a HIGH pulse for duration_ms milliseconds, then go LOW."""
    _pins[pin].value(1)
    time.sleep_ms(duration_ms)
    _pins[pin].value(0)

# ---------- BLINK ----------

def blink(pin, times=3, on_ms=200, off_ms=200):
    """Blink a pin N times with configurable on/off durations."""
    for _ in range(times):
        _pins[pin].value(1)
        time.sleep_ms(on_ms)
        _pins[pin].value(0)
        time.sleep_ms(off_ms)

# ---------- PWM SETUP ----------

def pwmSetup(pin, freq=1000):
    """Initialize PWM on a pin at a given frequency (default 1kHz)."""
    _pwm_pins[pin] = PWM(Pin(pin), freq=freq)

# ---------- PWM WRITE ----------

def pwmWrite(pin, duty):
    """Set PWM duty cycle (0–1023)."""
    _pwm_pins[pin].duty(duty)

# ---------- PWM WRITE PERCENT ----------

def pwmWritePercent(pin, percent):
    """Set PWM duty cycle as a percentage (0–100)."""
    duty = int((percent / 100.0) * 1023)
    _pwm_pins[pin].duty(duty)

# ---------- PWM FREQUENCY ----------

def pwmFreq(pin, freq):
    """Change the PWM frequency on a pin."""
    _pwm_pins[pin].freq(freq)

# ---------- PWM STOP ----------

def pwmStop(pin):
    """Stop PWM on a pin and deinit."""
    if pin in _pwm_pins:
        _pwm_pins[pin].deinit()
        del _pwm_pins[pin]

# ---------- INTERRUPT ATTACH ----------

def attachInterrupt(pin, callback, trigger=RISING, debounce_ms=50):
    """
    Attach an interrupt to a pin.
    trigger: RISING, FALLING, or CHANGE
    debounce_ms: minimum ms between triggers (0 = no debounce)
    """
    _debounce_ms[pin] = debounce_ms
    _last_trigger[pin] = 0

    def _handler(p):
        if debounce_ms > 0:
            now = time.ticks_ms()
            if time.ticks_diff(now, _last_trigger[pin]) < debounce_ms:
                return
            _last_trigger[pin] = now
        callback(p)

    _callbacks[pin] = _handler

    if pin not in _pins:
        _pins[pin] = Pin(pin, Pin.IN)

    _pins[pin].irq(trigger=trigger, handler=_handler)

# ---------- DETACH INTERRUPT ----------

def detachInterrupt(pin):
    """Remove the interrupt handler from a pin."""
    if pin in _pins:
        _pins[pin].irq(handler=None)
    _callbacks.pop(pin, None)
