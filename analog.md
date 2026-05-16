# analog.py — ESP32 Analog I/O Library

A MicroPython library for ESP32 analog input/output operations. Supports ADC reading, DAC writing, averaging, smoothing, and value mapping.

---

## Dependencies

```python
from machine import Pin, ADC, DAC
import time
```

---

## Constants

### Attenuation Levels (Input Voltage Range)

| Constant | Value | Input Range |
|---|---|---|
| `ATTN_0DB` | `ADC.ATTN_0DB` | 0 – 1.0 V |
| `ATTN_2_5DB` | `ADC.ATTN_2_5DB` | 0 – 1.34 V |
| `ATTN_6DB` | `ADC.ATTN_6DB` | 0 – 2.0 V |
| `ATTN_11DB` | `ADC.ATTN_11DB` | 0 – 3.6 V *(recommended for 3.3V range)* |

### Bit Width (Resolution)

| Constant | Value | Output Range |
|---|---|---|
| `WIDTH_9BIT` | `ADC.WIDTH_9BIT` | 0 – 511 |
| `WIDTH_10BIT` | `ADC.WIDTH_10BIT` | 0 – 1023 |
| `WIDTH_11BIT` | `ADC.WIDTH_11BIT` | 0 – 2047 |
| `WIDTH_12BIT` | `ADC.WIDTH_12BIT` | 0 – 4095 *(default)* |

---

## ADC Functions

### `analogPin(pin, attn, width)`

Configures an ADC pin for reading.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `pin` | `int` | — | GPIO pin number |
| `attn` | `const` | `ADC.ATTN_11DB` | Attenuation level |
| `width` | `const` | `ADC.WIDTH_12BIT` | Bit resolution |

```python
analogPin(34)                              # Default: 11dB attn, 12-bit
analogPin(34, attn=ATTN_6DB, width=WIDTH_10BIT)
```

---

### `analogRead(pin)`

Returns the raw ADC integer value from the pin.

```python
val = analogRead(34)   # e.g. 2048
```

---

### `analogPercent(pin)`

Returns the ADC reading mapped to a 0–100% integer.

```python
pct = analogPercent(34)   # e.g. 50
```

---

### `analogVoltage(pin, vref=3.3)`

Returns the estimated voltage at the pin as a float.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `pin` | `int` | — | GPIO pin number |
| `vref` | `float` | `3.3` | Reference voltage |

```python
v = analogVoltage(34)         # e.g. 1.65
v = analogVoltage(34, vref=5.0)
```

---

### `analogAverage(pin, samples=10)`

Reads the pin `samples` times with a 2 ms delay between each read and returns the integer average.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `pin` | `int` | — | GPIO pin number |
| `samples` | `int` | `10` | Number of samples to average |

```python
avg = analogAverage(34)         # 10 samples
avg = analogAverage(34, samples=20)
```

---

### `analogAveragePercent(pin, samples=10)`

Returns the averaged ADC reading as a 0–100% integer.

```python
pct = analogAveragePercent(34, samples=5)   # e.g. 47
```

---

### `analogSmooth(pin, window=8)`

Moving-average smoothing using a rolling window of `window` readings. Call repeatedly in a loop for a continuously smoothed value.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `pin` | `int` | — | GPIO pin number |
| `window` | `int` | `8` | Rolling window size |

```python
while True:
    smooth_val = analogSmooth(34, window=10)
```

---

### `analogThreshold(pin, threshold, samples=1)`

Returns `True` if the ADC reading exceeds the given raw threshold value.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `pin` | `int` | — | GPIO pin number |
| `threshold` | `int` | — | Raw ADC threshold value |
| `samples` | `int` | `1` | Samples to average before comparing |

```python
if analogThreshold(34, 2000, samples=5):
    print("Above threshold")
```

---

## Value Mapping Functions

### `mapValue(x, in_min, in_max, out_min, out_max)`

Maps a value from one integer range to another. Returns an `int`.

```python
mapped = mapValue(2048, 0, 4095, 0, 100)   # Returns 50
```

---

### `mapFloat(x, in_min, in_max, out_min, out_max)`

Same as `mapValue` but returns a `float`.

```python
mapped = mapFloat(2048, 0, 4095, 0.0, 3.3)   # Returns ~1.65
```

---

## DAC Functions

> **Note:** ESP32 DAC is only available on **GPIO 25** and **GPIO 26**.

### `dacPin(pin)`

Initializes a DAC output pin.

```python
dacPin(25)
```

---

### `dacWrite(pin, value)`

Writes a raw value (0–255) to the DAC output.

```python
dacWrite(25, 128)   # ~50% of vref
```

---

### `dacWriteVoltage(pin, voltage, vref=3.3)`

Writes a target voltage to the DAC output.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `pin` | `int` | — | DAC GPIO pin (25 or 26) |
| `voltage` | `float` | — | Target voltage to output |
| `vref` | `float` | `3.3` | Reference voltage |

```python
dacWriteVoltage(25, 1.65)       # ~1.65V output
dacWriteVoltage(25, 2.5, vref=3.3)
```

---

### `dacWritePercent(pin, percent)`

Writes a 0–100% value as a proportional DAC voltage.

```python
dacWritePercent(25, 75)   # 75% of vref
```

---

## Quick Start Example

```python
from analog import *

# Setup
analogPin(34)
dacPin(25)

# Read and mirror to DAC
while True:
    raw = analogRead(34)
    pct = analogPercent(34)
    print("Raw:", raw, "| %:", pct)

    # Mirror input to DAC output
    dacWritePercent(25, pct)
```
