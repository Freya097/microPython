# digital.py — ESP32 Digital I/O Library

A MicroPython library for ESP32 digital input/output operations. Supports GPIO control, PWM, interrupts, debouncing, and utility functions like blink and pulse.

---

## Dependencies

```python
from machine import Pin, PWM
import time
```

---

## Constants

### Pin Modes

| Constant | Value | Description |
|---|---|---|
| `INPUT` | `0` | Digital input, no pull resistor |
| `OUTPUT` | `1` | Digital output |
| `INPUT_PULLUP` | `2` | Input with internal pull-up resistor |
| `INPUT_PULLDOWN` | `3` | Input with internal pull-down resistor |

### Interrupt Triggers

| Constant | Value | Description |
|---|---|---|
| `RISING` | `Pin.IRQ_RISING` | Trigger on LOW → HIGH transition |
| `FALLING` | `Pin.IRQ_FALLING` | Trigger on HIGH → LOW transition |
| `CHANGE` | `IRQ_RISING \| IRQ_FALLING` | Trigger on any state change |

---

## GPIO Functions

### `pinMode(pin, mode)`

Configures a GPIO pin with the given mode.

| Parameter | Type | Description |
|---|---|---|
| `pin` | `int` | GPIO pin number |
| `mode` | `const` | `INPUT`, `OUTPUT`, `INPUT_PULLUP`, or `INPUT_PULLDOWN` |

```python
pinMode(2, OUTPUT)
pinMode(4, INPUT_PULLUP)
```

---

### `digitalWrite(pin, value)`

Writes `HIGH` (1) or `LOW` (0) to a digital output pin.

```python
digitalWrite(2, 1)   # HIGH
digitalWrite(2, 0)   # LOW
```

---

### `digitalRead(pin)`

Reads the current state of a digital pin. Returns `0` or `1`.

```python
state = digitalRead(4)
```

---

### `togglePin(pin)`

Flips the current state of a digital output pin.

```python
togglePin(2)   # If HIGH → LOW, if LOW → HIGH
```

---

### `pulse(pin, duration_ms=100)`

Emits a single HIGH pulse on the pin for `duration_ms` milliseconds, then returns LOW.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `pin` | `int` | — | GPIO pin number |
| `duration_ms` | `int` | `100` | Pulse duration in milliseconds |

```python
pulse(2)             # 100 ms pulse
pulse(2, duration_ms=500)
```

---

### `blink(pin, times=3, on_ms=200, off_ms=200)`

Blinks a pin a given number of times with configurable on/off durations.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `pin` | `int` | — | GPIO pin number |
| `times` | `int` | `3` | Number of blink cycles |
| `on_ms` | `int` | `200` | ON duration in milliseconds |
| `off_ms` | `int` | `200` | OFF duration in milliseconds |

```python
blink(2)                                  # 3 blinks, 200ms on/off
blink(2, times=5, on_ms=100, off_ms=400)
```

---

## PWM Functions

### `pwmSetup(pin, freq=1000)`

Initializes PWM on a pin at the given frequency.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `pin` | `int` | — | GPIO pin number |
| `freq` | `int` | `1000` | PWM frequency in Hz |

```python
pwmSetup(5)              # 1 kHz default
pwmSetup(5, freq=5000)
```

---

### `pwmWrite(pin, duty)`

Sets the PWM duty cycle using a raw value.

| Parameter | Type | Range | Description |
|---|---|---|---|
| `pin` | `int` | — | GPIO pin number |
| `duty` | `int` | 0 – 1023 | Duty cycle value |

```python
pwmWrite(5, 512)    # ~50% duty cycle
pwmWrite(5, 0)      # OFF
pwmWrite(5, 1023)   # Full ON
```

---

### `pwmWritePercent(pin, percent)`

Sets the PWM duty cycle as a percentage (0–100).

```python
pwmWritePercent(5, 75)   # 75% duty cycle
```

---

### `pwmFreq(pin, freq)`

Changes the PWM frequency on an already-initialized pin.

```python
pwmFreq(5, 2000)   # Change to 2 kHz
```

---

### `pwmStop(pin)`

Stops PWM on a pin and deinitializes it.

```python
pwmStop(5)
```

---

## Interrupt Functions

### `attachInterrupt(pin, callback, trigger=RISING, debounce_ms=50)`

Attaches an interrupt handler to a pin with optional debounce protection.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `pin` | `int` | — | GPIO pin number |
| `callback` | `function` | — | Function called on trigger; receives the Pin object |
| `trigger` | `const` | `RISING` | `RISING`, `FALLING`, or `CHANGE` |
| `debounce_ms` | `int` | `50` | Minimum ms between triggers; `0` disables debounce |

```python
def on_button(p):
    print("Button pressed!")

pinMode(0, INPUT_PULLUP)
attachInterrupt(0, on_button, trigger=FALLING, debounce_ms=100)
```

> **Note:** If the pin has not been configured with `pinMode()` before calling `attachInterrupt()`, the library automatically configures it as `INPUT`.

---

### `detachInterrupt(pin)`

Removes the interrupt handler from a pin.

```python
detachInterrupt(0)
```

---

## Quick Start Example

```python
from digital import *

# LED on GPIO 2, Button on GPIO 0
pinMode(2, OUTPUT)
pinMode(0, INPUT_PULLUP)

# Button toggles LED via interrupt
def on_press(p):
    togglePin(2)

attachInterrupt(0, on_press, trigger=FALLING, debounce_ms=50)

# Startup blink to confirm running
blink(2, times=3)

# PWM fade example
pwmSetup(5, freq=1000)
for pct in range(0, 101, 5):
    pwmWritePercent(5, pct)

pwmStop(5)
```
