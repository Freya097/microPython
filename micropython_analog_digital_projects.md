# 🔬 20 MicroPython Analog + Digital Projects
### Using `analog.py`, `digital.py` & `systemio.py` — ESP32

---

## Library Imports Reference

```python
# Analog
from analog import (analogPin, analogRead, analogPercent, analogVoltage,
                    analogAverage, analogAveragePercent, analogSmooth,
                    analogThreshold, mapValue, mapFloat,
                    dacPin, dacWrite, dacWriteVoltage, dacWritePercent,
                    ATTN_11DB, WIDTH_12BIT)

# Digital
from digital import (pinMode, digitalWrite, digitalRead, togglePin,
                     pulse, blink, pwmSetup, pwmWrite, pwmWritePercent,
                     pwmStop, attachInterrupt, detachInterrupt,
                     INPUT, OUTPUT, INPUT_PULLUP, RISING, FALLING, CHANGE)

# Safe Run
from systemio import run
```

---

## Project 1 — Potentiometer Raw Read

**Components:** 10kΩ Potentiometer  
**Concept:** Basic ADC read — the simplest analog input

| Pin | Connect To |
|-----|-----------|
| GPIO 34 | Middle pin of potentiometer |
| 3.3V | Left pin |
| GND | Right pin |

```python
from analog import analogPin, analogRead
from systemio import run
import time

POT_PIN = 34

def setup():
    analogPin(POT_PIN)

def main():
    setup()
    print("Potentiometer Read Started")
    while True:
        raw = analogRead(POT_PIN)
        print("Raw ADC:", raw)
        time.sleep(0.5)

def cleanup():
    print("Stopped")

run(main, cleanup)
```

---

## Project 2 — Potentiometer Percent & Voltage

**Components:** 10kΩ Potentiometer  
**Concept:** Converting raw ADC to human-readable percent and voltage

```python
from analog import analogPin, analogPercent, analogVoltage
from systemio import run
import time

POT_PIN = 34

def setup():
    analogPin(POT_PIN)

def main():
    setup()
    print("Pot Percent + Voltage")
    while True:
        pct  = analogPercent(POT_PIN)
        volt = analogVoltage(POT_PIN)
        print(f"Percent: {pct}%   Voltage: {volt}V")
        time.sleep(0.5)

def cleanup():
    print("Stopped")

run(main, cleanup)
```

---

## Project 3 — Potentiometer Controls LED Brightness (Analog → PWM)

**Components:** Potentiometer, LED, 220Ω resistor  
**Concept:** Map analog input directly to PWM duty — analog controls digital output

```python
from analog import analogPin, analogRead, mapValue
from digital import pwmSetup, pwmWrite, pwmStop
from systemio import run
import time

POT_PIN = 34
LED_PIN = 4

def setup():
    analogPin(POT_PIN)
    pwmSetup(LED_PIN, freq=1000)

def main():
    setup()
    print("Pot → LED Brightness")
    while True:
        raw   = analogRead(POT_PIN)              # 0 – 4095
        duty  = mapValue(raw, 0, 4095, 0, 1023)  # map to PWM range
        pwmWrite(LED_PIN, duty)
        print(f"ADC: {raw}  →  PWM Duty: {duty}")
        time.sleep(0.05)

def cleanup():
    pwmStop(LED_PIN)

run(main, cleanup)
```

---

## Project 4 — Averaged ADC Read (Noise Reduction)

**Components:** Potentiometer or any analog sensor  
**Concept:** Multi-sample averaging vs single read — see the stability difference

```python
from analog import analogPin, analogRead, analogAverage
from systemio import run
import time

SENSOR_PIN = 34

def setup():
    analogPin(SENSOR_PIN)

def main():
    setup()
    print("Single vs Averaged Read Comparison")
    while True:
        single = analogRead(SENSOR_PIN)
        avg    = analogAverage(SENSOR_PIN, samples=16)
        print(f"Single: {single:4d}   Averaged(16): {avg:4d}   Diff: {abs(single - avg)}")
        time.sleep(0.5)

def cleanup():
    print("Stopped")

run(main, cleanup)
```

> **Student Note:** The `Diff` value shows how much noise averaging removes. Try touching the wire to see it spike on single reads but stay stable on averaged.

---

## Project 5 — Smoothed Sensor with Moving Average

**Components:** Potentiometer  
**Concept:** Moving-average window smoothing — filters fast jitter in real-time

```python
from analog import analogPin, analogRead, analogSmooth
from systemio import run
import time

POT_PIN = 34

def setup():
    analogPin(POT_PIN)

def main():
    setup()
    print("Raw vs Smoothed Read")
    while True:
        raw      = analogRead(POT_PIN)
        smoothed = analogSmooth(POT_PIN, window=12)
        print(f"Raw: {raw:4d}   Smoothed: {smoothed:4d}")
        time.sleep(0.05)

def cleanup():
    print("Stopped")

run(main, cleanup)
```

---

## Project 6 — Analog Threshold → Digital LED Alert

**Components:** LDR or potentiometer, LED  
**Concept:** Analog value crossing a threshold triggers a digital output

```python
from analog import analogPin, analogThreshold
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
import time

SENSOR_PIN = 34
LED_PIN    = 4
THRESHOLD  = 2000     # ~48% of 4095 — adjust to your sensor

def setup():
    analogPin(SENSOR_PIN)
    pinMode(LED_PIN, OUTPUT)

def main():
    setup()
    print(f"Threshold Alert — trigger at ADC > {THRESHOLD}")
    while True:
        triggered = analogThreshold(SENSOR_PIN, THRESHOLD, samples=5)
        digitalWrite(LED_PIN, 1 if triggered else 0)
        print("ALERT!" if triggered else "Normal", end="\r")
        time.sleep(0.2)

def cleanup():
    digitalWrite(LED_PIN, 0)

run(main, cleanup)
```

---

## Project 7 — LDR Night Light (Analog + Digital)

**Components:** LDR, 10kΩ resistor, LED  
**Concept:** Analog light level controls digital LED — auto night light

```python
from analog import analogPin, analogAverage
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
import time

LDR_PIN   = 34
LED_PIN   = 4
DARK_VAL  = 1500      # Below this = dark; adjust for your room

def setup():
    analogPin(LDR_PIN)
    pinMode(LED_PIN, OUTPUT)

def main():
    setup()
    print("Auto Night Light")
    while True:
        light = analogAverage(LDR_PIN, samples=8)
        dark  = light < DARK_VAL
        digitalWrite(LED_PIN, 1 if dark else 0)
        print(f"Light Level: {light:4d}  →  LED {'ON ' if dark else 'OFF'}")
        time.sleep(1)

def cleanup():
    digitalWrite(LED_PIN, 0)

run(main, cleanup)
```

---

## Project 8 — Analog Bargraph on 5 LEDs

**Components:** Potentiometer, 5 LEDs, 220Ω resistors  
**Concept:** Map analog range to LED count — visual level meter

```python
from analog import analogPin, analogRead, mapValue
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
import time

POT_PIN  = 34
LED_PINS = [4, 5, 18, 19, 21]   # 5 LEDs

def setup():
    analogPin(POT_PIN)
    for pin in LED_PINS:
        pinMode(pin, OUTPUT)
        digitalWrite(pin, 0)

def main():
    setup()
    print("Analog Bargraph")
    while True:
        raw   = analogRead(POT_PIN)
        level = mapValue(raw, 0, 4095, 0, 5)    # 0 to 5 LEDs on
        for i, pin in enumerate(LED_PINS):
            digitalWrite(pin, 1 if i < level else 0)
        bar = "█" * level + "░" * (5 - level)
        print(f"ADC: {raw:4d}  [{bar}]")
        time.sleep(0.1)

def cleanup():
    for pin in LED_PINS:
        digitalWrite(pin, 0)

run(main, cleanup)
```

---

## Project 9 — DAC Sine Wave Generator

**Components:** Oscilloscope or speaker on GPIO 25  
**Concept:** DAC output producing a smooth sine wave — analog signal generation

```python
from analog import dacPin, dacWrite
from systemio import run
import time, math

DAC_PIN   = 25
SAMPLES   = 64
FREQUENCY = 100    # Hz

def setup():
    dacPin(DAC_PIN)

def main():
    setup()
    delay_us = int(1_000_000 / (FREQUENCY * SAMPLES))
    table    = [int(127 + 127 * math.sin(2 * math.pi * i / SAMPLES))
                for i in range(SAMPLES)]
    print(f"Sine Wave: {FREQUENCY}Hz, {SAMPLES} samples/cycle")
    while True:
        for val in table:
            dacWrite(DAC_PIN, val)
            time.sleep_us(delay_us)

def cleanup():
    dacWrite(DAC_PIN, 0)
    print("DAC OFF")

run(main, cleanup)
```

---

## Project 10 — DAC Controlled by Potentiometer

**Components:** Potentiometer on ADC, jumper wire from DAC to LED or scope  
**Concept:** Analog input controls analog output — full analog loop

```python
from analog import analogPin, analogRead, dacPin, dacWrite, mapValue
from systemio import run
import time

POT_PIN = 34
DAC_PIN = 25

def setup():
    analogPin(POT_PIN)
    dacPin(DAC_PIN)

def main():
    setup()
    print("Pot → DAC Output")
    while True:
        raw = analogRead(POT_PIN)                # 0 – 4095
        out = mapValue(raw, 0, 4095, 0, 255)     # scale to DAC range
        dacWrite(DAC_PIN, out)
        print(f"ADC: {raw:4d}  →  DAC: {out:3d}")
        time.sleep(0.1)

def cleanup():
    dacWrite(DAC_PIN, 0)

run(main, cleanup)
```

---

## Project 11 — Temperature Monitor (NTC Thermistor)

**Components:** NTC 10kΩ thermistor, 10kΩ resistor (voltage divider)  
**Concept:** Convert ADC voltage to Celsius using Steinhart–Hart equation

```python
from analog import analogPin, analogAverage, analogVoltage
from systemio import run
import math, time

TEMP_PIN  = 34
R_FIXED   = 10000    # 10kΩ fixed resistor
B_CONST   = 3950     # NTC Beta value
T_NOM     = 298.15   # 25°C in Kelvin
R_NOM     = 10000    # Thermistor nominal resistance at 25°C

def setup():
    analogPin(TEMP_PIN)

def read_celsius():
    raw  = analogAverage(TEMP_PIN, samples=10)
    if raw == 0: return 0
    r    = R_FIXED * (4095.0 / raw - 1.0)
    temp = 1.0 / (1.0/T_NOM + math.log(r / R_NOM) / B_CONST)
    return round(temp - 273.15, 1)

def main():
    setup()
    print("NTC Temperature Monitor")
    while True:
        celsius    = read_celsius()
        fahrenheit = round(celsius * 9/5 + 32, 1)
        print(f"Temperature: {celsius}°C  /  {fahrenheit}°F")
        time.sleep(2)

def cleanup():
    print("Temp monitor stopped")

run(main, cleanup)
```

---

## Project 12 — Sound Level Meter (Microphone Module)

**Components:** KY-038 or MAX4466 mic module (analog out)  
**Concept:** Analog mic level → peak detection → LED bargraph

```python
from analog import analogPin, analogRead, mapValue
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
import time

MIC_PIN  = 34
LED_PINS = [4, 5, 18, 19, 21]
SILENCE  = 1800     # Mid-scale idle level for your mic module

def setup():
    analogPin(MIC_PIN)
    for pin in LED_PINS:
        pinMode(pin, OUTPUT)
        digitalWrite(pin, 0)

def main():
    setup()
    peak = 0
    print("Sound Level Meter")
    while True:
        raw       = analogRead(MIC_PIN)
        amplitude = abs(raw - SILENCE)          # distance from idle
        peak      = max(peak, amplitude)
        if peak > 0:
            level = mapValue(amplitude, 0, peak, 0, 5)
            for i, pin in enumerate(LED_PINS):
                digitalWrite(pin, 1 if i < level else 0)
        bar = "█" * level + "░" * (5 - level)
        print(f"Amplitude: {amplitude:4d}  [{bar}]")
        peak = int(peak * 0.98)                 # slow decay
        time.sleep(0.02)

def cleanup():
    for pin in LED_PINS:
        digitalWrite(pin, 0)

run(main, cleanup)
```

---

## Project 13 — Soil Moisture Monitor

**Components:** Capacitive soil moisture sensor (analog output)  
**Concept:** Analog moisture level + digital alert LED + threshold warning

```python
from analog import analogPin, analogAverage, analogPercent
from digital import pinMode, digitalWrite, blink, OUTPUT
from systemio import run
import time

SOIL_PIN  = 34
LED_PIN   = 4
DRY_LIMIT = 30      # Below 30% = dry → alert

def setup():
    analogPin(SOIL_PIN)
    pinMode(LED_PIN, OUTPUT)

def main():
    setup()
    print("Soil Moisture Monitor")
    while True:
        moisture = analogPercent(SOIL_PIN)
        # Invert if your sensor reads high when dry
        moisture = 100 - moisture
        status   = "DRY  ⚠" if moisture < DRY_LIMIT else "OK   ✓"
        print(f"Moisture: {moisture:3d}%  Status: {status}")
        if moisture < DRY_LIMIT:
            blink(LED_PIN, times=3, on_ms=100, off_ms=100)
        else:
            digitalWrite(LED_PIN, 0)
        time.sleep(3)

def cleanup():
    digitalWrite(LED_PIN, 0)

run(main, cleanup)
```

---

## Project 14 — Joystick Controller (2-Axis + Button)

**Components:** Analog joystick module (VRx, VRy, SW)  
**Concept:** Dual-axis analog read + digital button — directional detection

```python
from analog import analogPin, analogRead, mapValue
from digital import pinMode, digitalRead, INPUT_PULLUP
from systemio import run
import time

VRX_PIN = 34
VRY_PIN = 35
SW_PIN  = 5

ZONES = [(0, 30, "LEFT"), (70, 100, "RIGHT")]

def direction(percent):
    if percent < 30:  return "LOW "
    if percent > 70:  return "HIGH"
    return "MID "

def setup():
    analogPin(VRX_PIN)
    analogPin(VRY_PIN)
    pinMode(SW_PIN, INPUT_PULLUP)

def main():
    setup()
    print("Joystick Controller")
    while True:
        x   = mapValue(analogRead(VRX_PIN), 0, 4095, 0, 100)
        y   = mapValue(analogRead(VRY_PIN), 0, 4095, 0, 100)
        btn = "PRESSED" if digitalRead(SW_PIN) == 0 else "open   "
        print(f"X: {x:3d}% [{direction(x)}]  Y: {y:3d}% [{direction(y)}]  BTN: {btn}")
        time.sleep(0.1)

def cleanup():
    print("Joystick stopped")

run(main, cleanup)
```

---

## Project 15 — Analog Voltmeter (0–3.3V Display)

**Components:** Any voltage source (max 3.3V), potentiometer for testing  
**Concept:** Accurate voltage measurement with averaged samples and smoothing

```python
from analog import analogPin, analogAverage, analogSmooth, mapFloat
from systemio import run
import time

VOLT_PIN = 34

def setup():
    analogPin(VOLT_PIN)

def draw_bar(v, v_max=3.3, width=20):
    filled = int((v / v_max) * width)
    return "[" + "=" * filled + " " * (width - filled) + "]"

def main():
    setup()
    print("ESP32 Voltmeter  (0 – 3.3V)")
    print("-" * 40)
    while True:
        avg     = analogAverage(VOLT_PIN, samples=20)
        voltage = mapFloat(avg, 0, 4095, 0.0, 3.3)
        bar     = draw_bar(voltage)
        print(f"  {voltage:.3f} V  {bar}")
        time.sleep(0.5)

def cleanup():
    print("Voltmeter stopped")

run(main, cleanup)
```

---

## Project 16 — Servo Angle via Potentiometer (Analog → PWM)

**Components:** SG90 Servo, Potentiometer  
**Concept:** Potentiometer directly maps to servo angle — analog-to-motion

```python
from analog import analogPin, analogSmooth, mapValue
from digital import pwmSetup, pwmWrite, pwmStop
from systemio import run
import time

POT_PIN   = 34
SERVO_PIN = 4

def angle_duty(angle):
    return mapValue(angle, 0, 180, 26, 102)   # SG90 at 50Hz

def setup():
    analogPin(POT_PIN)
    pwmSetup(SERVO_PIN, freq=50)

def main():
    setup()
    print("Pot → Servo Angle Control")
    while True:
        smooth = analogSmooth(POT_PIN, window=8)
        angle  = mapValue(smooth, 0, 4095, 0, 180)
        pwmWrite(SERVO_PIN, angle_duty(angle))
        print(f"ADC: {smooth:4d}  →  Angle: {angle:3d}°")
        time.sleep(0.05)

def cleanup():
    pwmStop(SERVO_PIN)

run(main, cleanup)
```

---

## Project 17 — Gas / Smoke Detector (MQ Sensor)

**Components:** MQ-2 or MQ-135 gas sensor (analog output), LED, Buzzer  
**Concept:** Analog gas level with threshold alert — safety application

```python
from analog import analogPin, analogAverage, analogPercent
from digital import pinMode, digitalWrite, blink, OUTPUT
from systemio import run
import time

GAS_PIN    = 34
LED_PIN    = 4
BUZZER_PIN = 5
WARNING    = 40     # % threshold — adjust after warming up sensor
DANGER     = 70

def setup():
    analogPin(GAS_PIN)
    pinMode(LED_PIN, OUTPUT)
    pinMode(BUZZER_PIN, OUTPUT)
    print("Warming up sensor — 20 seconds...")
    time.sleep(20)

def main():
    setup()
    print("Gas Detector Active")
    while True:
        level = analogPercent(GAS_PIN)
        if level >= DANGER:
            print(f"⚠⚠ DANGER! Gas: {level}%")
            blink(LED_PIN,    times=5, on_ms=100, off_ms=50)
            blink(BUZZER_PIN, times=5, on_ms=100, off_ms=50)
        elif level >= WARNING:
            print(f"⚠  WARNING  Gas: {level}%")
            blink(LED_PIN, times=2, on_ms=200, off_ms=200)
            digitalWrite(BUZZER_PIN, 0)
        else:
            print(f"   Normal   Gas: {level}%")
            digitalWrite(LED_PIN, 0)
            digitalWrite(BUZZER_PIN, 0)
        time.sleep(1)

def cleanup():
    digitalWrite(LED_PIN, 0)
    digitalWrite(BUZZER_PIN, 0)

run(main, cleanup)
```

---

## Project 18 — DAC Audio Tone Generator (Button Controlled)

**Components:** 3 Push Buttons, speaker/buzzer on DAC pin  
**Concept:** Buttons select musical notes generated via DAC sine output

```python
from analog import dacPin, dacWrite
from digital import pinMode, digitalRead, INPUT_PULLUP
from systemio import run
import time, math

DAC_PIN = 25
BTN_C   = 4     # Do
BTN_E   = 5     # Mi
BTN_G   = 18    # Sol

NOTES = {
    BTN_C: 261,
    BTN_E: 330,
    BTN_G: 392,
}

def play_tone(freq, duration_ms=300, samples=32):
    delay_us = int(1_000_000 / (freq * samples))
    end      = time.ticks_add(time.ticks_ms(), duration_ms)
    while time.ticks_diff(end, time.ticks_ms()) > 0:
        for i in range(samples):
            val = int(127 + 100 * math.sin(2 * math.pi * i / samples))
            dacWrite(DAC_PIN, val)
            time.sleep_us(delay_us)
    dacWrite(DAC_PIN, 128)

def setup():
    dacPin(DAC_PIN)
    for pin in NOTES:
        pinMode(pin, INPUT_PULLUP)

def main():
    setup()
    print("DAC Tone Piano — press C / E / G buttons")
    while True:
        for btn, freq in NOTES.items():
            if digitalRead(btn) == 0:
                note = {BTN_C: "C (Do)", BTN_E: "E (Mi)", BTN_G: "G (Sol)"}[btn]
                print(f"Playing {note} — {freq}Hz")
                play_tone(freq, duration_ms=400)
        time.sleep(0.05)

def cleanup():
    dacWrite(DAC_PIN, 0)

run(main, cleanup)
```

---

## Project 19 — Heart Rate Simulator (Analog + DAC Waveform)

**Components:** Potentiometer (controls BPM), DAC output to scope/speaker  
**Concept:** Pot sets heart rate (BPM); DAC outputs a simulated pulse wave

```python
from analog import analogPin, analogRead, dacPin, dacWrite, mapValue
from systemio import run
import time

POT_PIN = 34
DAC_PIN = 25

PULSE_WAVE = [
    128,130,132,135,140,148,160,180,220,255,
    220,160,120,100, 90, 85, 88, 92, 96,100,
    105,108,110,112,113,114,115,115,114,112,
    110,108,106,104,102,100, 99, 98, 98, 98,
    99, 100,102,104,106,108,110,112,114,116,
    118,120,122,124,126,127,128,128,128,128
]

def setup():
    analogPin(POT_PIN)
    dacPin(DAC_PIN)

def main():
    setup()
    print("Heart Rate Simulator")
    while True:
        bpm       = mapValue(analogRead(POT_PIN), 0, 4095, 40, 180)
        period_ms = int(60000 / bpm)
        delay_ms  = period_ms // len(PULSE_WAVE)
        print(f"BPM: {bpm}  period: {period_ms}ms")
        for val in PULSE_WAVE:
            dacWrite(DAC_PIN, val)
            time.sleep_ms(max(1, delay_ms))

def cleanup():
    dacWrite(DAC_PIN, 0)
    print("Simulator stopped")

run(main, cleanup)
```

---

## Project 20 — Full Sensor Dashboard (Analog + Digital Combined)

**Components:** Potentiometer, LDR, Push Button, 2 LEDs, Active Buzzer  
**Concept:** Reads multiple analog sensors, shows a live terminal dashboard, triggers digital outputs on thresholds

```python
from analog import analogPin, analogAverage, analogPercent, analogVoltage
from digital import pinMode, digitalWrite, digitalRead, blink, pwmSetup, pwmWrite, pwmStop
from digital import INPUT_PULLUP, OUTPUT
from systemio import run
import time

POT_PIN    = 34
LDR_PIN    = 35
BTN_PIN    = 5
LED_STATUS = 4
LED_ALERT  = 18
BUZZER_PIN = 19
PWM_LED    = 21

DARK_THR  = 40    # % light below this = dark
KNOB_WARN = 80    # % pot above this = warning

def setup():
    analogPin(POT_PIN)
    analogPin(LDR_PIN)
    pinMode(BTN_PIN,    INPUT_PULLUP)
    pinMode(LED_STATUS, OUTPUT)
    pinMode(LED_ALERT,  OUTPUT)
    pinMode(BUZZER_PIN, OUTPUT)
    pwmSetup(PWM_LED,   freq=1000)

def print_dashboard(knob, light, volt, btn):
    knob_bar  = "█" * (knob  // 10) + "░" * (10 - knob  // 10)
    light_bar = "█" * (light // 10) + "░" * (10 - light // 10)
    print("\033[H\033[J", end="")            # clear terminal
    print("╔══════════════════════════════╗")
    print("║   ESP32 SENSOR DASHBOARD     ║")
    print("╠══════════════════════════════╣")
    print(f"║  Knob  : {knob:3d}%  [{knob_bar}] ║")
    print(f"║  Light : {light:3d}%  [{light_bar}] ║")
    print(f"║  Volt  : {volt:.3f}V              ║")
    print(f"║  Button: {'PRESSED' if btn else 'open   '}               ║")
    print("╚══════════════════════════════╝")

def main():
    setup()
    while True:
        knob  = analogPercent(POT_PIN)
        light = analogPercent(LDR_PIN)
        volt  = analogVoltage(POT_PIN)
        btn   = digitalRead(BTN_PIN) == 0

        print_dashboard(knob, light, volt, btn)

        # Knob controls PWM LED brightness
        from analog import mapValue
        pwmWrite(PWM_LED, mapValue(knob, 0, 100, 0, 1023))

        # Status LED = ON when button pressed
        digitalWrite(LED_STATUS, 1 if btn else 0)

        # Alert LED + Buzzer when knob > warning level
        if knob > KNOB_WARN:
            blink(LED_ALERT, times=1, on_ms=100, off_ms=0)
            blink(BUZZER_PIN, times=1, on_ms=50, off_ms=0)
        else:
            digitalWrite(LED_ALERT, 0)
            digitalWrite(BUZZER_PIN, 0)

        time.sleep(0.2)

def cleanup():
    pwmStop(PWM_LED)
    for pin in [LED_STATUS, LED_ALERT, BUZZER_PIN]:
        digitalWrite(pin, 0)
    print("Dashboard stopped")

run(main, cleanup)
```

---

## 📊 Quick Reference Table

| # | Project | Sensor / Component | Key Functions | Analog | Digital |
|---|---------|-------------------|---------------|:------:|:-------:|
| 1 | Pot Raw Read | Potentiometer | `analogRead` | ✅ | — |
| 2 | Pot Percent & Voltage | Potentiometer | `analogPercent`, `analogVoltage` | ✅ | — |
| 3 | Pot → LED Brightness | Pot + LED | `mapValue`, `pwmWrite` | ✅ | ✅ |
| 4 | Averaged ADC | Any sensor | `analogAverage` | ✅ | — |
| 5 | Smoothed Read | Potentiometer | `analogSmooth` | ✅ | — |
| 6 | Threshold Alert | LDR / Pot | `analogThreshold`, `digitalWrite` | ✅ | ✅ |
| 7 | Night Light | LDR + LED | `analogAverage`, `digitalWrite` | ✅ | ✅ |
| 8 | Bargraph | Pot + 5 LEDs | `mapValue`, `digitalWrite` | ✅ | ✅ |
| 9 | DAC Sine Wave | Speaker/Scope | `dacWrite`, `math.sin` | ✅ | — |
| 10 | Pot → DAC Out | Pot + DAC | `dacWrite`, `mapValue` | ✅ | — |
| 11 | Temperature | NTC Thermistor | `analogAverage`, Steinhart | ✅ | — |
| 12 | Sound Meter | Mic + LEDs | `analogRead`, peak detect | ✅ | ✅ |
| 13 | Soil Moisture | Moisture sensor | `analogPercent`, `blink` | ✅ | ✅ |
| 14 | Joystick | Joystick module | `analogRead`, `digitalRead` | ✅ | ✅ |
| 15 | Voltmeter | Any 0–3.3V | `analogAverage`, `mapFloat` | ✅ | — |
| 16 | Pot → Servo | Pot + Servo | `analogSmooth`, `pwmWrite` | ✅ | ✅ |
| 17 | Gas Detector | MQ sensor | `analogPercent`, `blink` | ✅ | ✅ |
| 18 | DAC Piano | Buttons + DAC | `dacWrite`, `digitalRead` | ✅ | ✅ |
| 19 | Heart Rate Sim | Pot + DAC | `dacWrite`, `mapValue` | ✅ | — |
| 20 | Sensor Dashboard | Multi-sensor | All functions combined | ✅ | ✅ |

---

## 🧠 Key Concepts Summary

**When to use which read function:**

| Situation | Use |
|-----------|-----|
| Fast loop, live control | `analogRead()` |
| Stable single reading | `analogAverage(samples=10)` |
| Continuous smooth display | `analogSmooth(window=8)` |
| Just a yes/no trigger | `analogThreshold()` |
| Show % to user | `analogPercent()` |
| Measure actual voltage | `analogVoltage()` |

**DAC output range:** GPIO 25 & 26 only — always 0 to 255 (0V to 3.3V)

**ADC input range:** 0–4095 at 12-bit with `ATTN_11DB` — covers 0V to ~3.3V

> **All projects use `run(main, cleanup)`** so pressing **Ctrl+C** always exits cleanly and turns off every output safely.
