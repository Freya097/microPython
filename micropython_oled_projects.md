# 📟 20 MicroPython OLED Projects
### Using `oled.py`, `analog.py`, `digital.py` & `systemio.py` — ESP32

---

## Wiring Reference

| OLED Pin | ESP32 GPIO |
|----------|-----------|
| VCC | 3.3V |
| GND | GND |
| SCL | GPIO 22 |
| SDA | GPIO 21 |

```python
from oled import OLED
oled = OLED(scl=22, sda=21)
```

**OLED Screen Area:** 128 × 64 pixels  
**Text grid (8×8 font):** 16 columns × 8 rows  
**Origin (0,0):** Top-left corner

---

## Project 1 — Hello World

**Components:** OLED only  
**Concept:** Basic text display — clear, write, show pattern

```python
from oled import OLED
from systemio import run
import time

def main():
    oled = OLED(scl=22, sda=21)
    oled.clear()
    oled.text("Hello, World!", 0, 0)
    oled.text("MicroPython", 16, 20)
    oled.text("ESP32 Ready", 16, 40)
    oled.show()
    print("Display updated")
    while True:
        time.sleep(1)

def cleanup():
    print("Stopped")

run(main, cleanup)
```

---

## Project 2 — Live Counter on OLED

**Components:** OLED only  
**Concept:** Updating display in a loop — clear before each refresh

```python
from oled import OLED
from systemio import run
import time

def main():
    oled  = OLED(scl=22, sda=21)
    count = 0
    while True:
        oled.clear()
        oled.text("Counter", 32, 4)
        oled.line(0, 14, 128, 14)
        oled.text(str(count), 50, 30)
        oled.show()
        count += 1
        time.sleep(0.5)

def cleanup():
    print("Stopped")

run(main, cleanup)
```

> **Student Note:** Always call `oled.clear()` before redrawing — pixels stay on until cleared.

---

## Project 3 — Button Press Counter on OLED

**Components:** OLED, Push Button  
**Concept:** Digital input count displayed live on screen

```python
from oled import OLED
from digital import pinMode, digitalRead, INPUT_PULLUP
from systemio import run
import time

BTN_PIN = 5
count   = 0

def main():
    global count
    oled     = OLED(scl=22, sda=21)
    last_btn = 1
    pinMode(BTN_PIN, INPUT_PULLUP)

    while True:
        btn = digitalRead(BTN_PIN)
        if last_btn == 1 and btn == 0:
            count += 1
        last_btn = btn

        oled.clear()
        oled.text("Button Counter", 0, 0)
        oled.line(0, 12, 128, 12)
        oled.text("Press count:", 0, 24)
        oled.text(str(count), 56, 40)
        oled.show()
        time.sleep(0.05)

def cleanup():
    print("Final count:", count)

run(main, cleanup)
```

---

## Project 4 — Potentiometer Value Display

**Components:** OLED, 10kΩ Potentiometer  
**Concept:** Show raw ADC, percent, and a live bar on screen

```python
from oled import OLED
from analog import analogPin, analogRead, analogPercent, mapValue
from systemio import run
import time

POT_PIN = 34

def draw_bar(oled, percent):
    bar_w = mapValue(percent, 0, 100, 0, 118)
    oled.rect(4, 50, 120, 10)          # border
    if bar_w > 0:
        for x in range(6, 6 + bar_w):  # fill
            oled.line(x, 52, x, 57)

def main():
    oled = OLED(scl=22, sda=21)
    analogPin(POT_PIN)

    while True:
        raw  = analogRead(POT_PIN)
        pct  = analogPercent(POT_PIN)
        oled.clear()
        oled.text("Potentiometer", 8, 0)
        oled.line(0, 12, 128, 12)
        oled.text(f"Raw : {raw}", 0, 18)
        oled.text(f"Pct : {pct}%", 0, 30)
        draw_bar(oled, pct)
        oled.show()
        time.sleep(0.1)

def cleanup():
    print("Stopped")

run(main, cleanup)
```

---

## Project 5 — Voltage Meter Display

**Components:** OLED, Potentiometer (as voltage source 0–3.3V)  
**Concept:** Display measured voltage with large text and a bar graph

```python
from oled import OLED
from analog import analogPin, analogAverage, mapFloat, mapValue
from systemio import run
import time

PIN = 34

def main():
    oled = OLED(scl=22, sda=21)
    analogPin(PIN)

    while True:
        avg  = analogAverage(PIN, samples=16)
        volt = mapFloat(avg, 0, 4095, 0.0, 3.3)
        bar  = mapValue(avg, 0, 4095, 0, 116)

        oled.clear()
        oled.text("  Voltmeter", 0, 0)
        oled.line(0, 12, 128, 12)
        oled.text(f"  {volt:.3f} V", 16, 26)
        oled.rect(4, 48, 120, 12)
        for x in range(6, 6 + bar):
            oled.line(x, 50, x, 57)
        oled.show()
        time.sleep(0.3)

def cleanup():
    print("Stopped")

run(main, cleanup)
```

---

## Project 6 — Temperature Display (NTC Thermistor)

**Components:** OLED, NTC 10kΩ thermistor, 10kΩ resistor  
**Concept:** Analog temperature reading shown in °C and °F

```python
from oled import OLED
from analog import analogPin, analogAverage
from systemio import run
import math, time

TEMP_PIN = 34

def read_celsius():
    raw = analogAverage(TEMP_PIN, samples=12)
    if raw == 0: return 0.0
    r   = 10000 * (4095.0 / raw - 1.0)
    t   = 1.0 / (1.0/298.15 + math.log(r/10000) / 3950)
    return round(t - 273.15, 1)

def main():
    oled = OLED(scl=22, sda=21)
    analogPin(TEMP_PIN)

    while True:
        c = read_celsius()
        f = round(c * 9/5 + 32, 1)

        oled.clear()
        oled.text("Temperature", 16, 0)
        oled.line(0, 12, 128, 12)
        oled.text(f"{c} C", 24, 24)
        oled.text(f"{f} F", 24, 40)
        oled.rect(0, 0, 128, 64)
        oled.show()
        time.sleep(2)

def cleanup():
    print("Stopped")

run(main, cleanup)
```

---

## Project 7 — Analog Bargraph on OLED (5 Levels)

**Components:** OLED, Potentiometer  
**Concept:** Segment-style level meter drawn with rectangles

```python
from oled import OLED
from analog import analogPin, analogRead, mapValue
from systemio import run
import time

POT_PIN = 34
SEGS    = 5
SEG_W   = 20
SEG_H   = 30
GAP     = 4
START_X = 9
START_Y = 20

def main():
    oled = OLED(scl=22, sda=21)
    analogPin(POT_PIN)

    while True:
        raw   = analogRead(POT_PIN)
        level = mapValue(raw, 0, 4095, 0, SEGS)

        oled.clear()
        oled.text("Level Meter", 16, 0)
        oled.line(0, 12, 128, 12)

        for i in range(SEGS):
            x = START_X + i * (SEG_W + GAP)
            oled.rect(x, START_Y, SEG_W, SEG_H)
            if i < level:
                for row in range(START_Y + 2, START_Y + SEG_H - 1):
                    oled.line(x + 2, row, x + SEG_W - 2, row)

        oled.text(f"{level}/{SEGS}", 48, 56)
        oled.show()
        time.sleep(0.1)

def cleanup():
    print("Stopped")

run(main, cleanup)
```

---

## Project 8 — Digital Clock (Seconds Timer)

**Components:** OLED only  
**Concept:** Time counter using `time.ticks_ms()` — MM:SS display

```python
from oled import OLED
from systemio import run
import time

def fmt(n):
    return f"{n:02d}"

def main():
    oled  = OLED(scl=22, sda=21)
    start = time.ticks_ms()

    while True:
        elapsed = time.ticks_diff(time.ticks_ms(), start) // 1000
        mm = elapsed // 60
        ss = elapsed % 60

        oled.clear()
        oled.text("Stopwatch", 24, 0)
        oled.line(0, 12, 128, 12)
        oled.text(f"  {fmt(mm)} : {fmt(ss)}", 8, 28)
        oled.line(0, 52, 128, 52)
        oled.text("Press Ctrl+C stop", 0, 55)
        oled.show()
        time.sleep(1)

def cleanup():
    print("Stopped")

run(main, cleanup)
```

---

## Project 9 — Reaction Timer Game

**Components:** OLED, 2 Push Buttons (Start/Stop)  
**Concept:** Reaction speed measured in ms — result shown on screen

```python
from oled import OLED
from digital import pinMode, digitalRead, INPUT_PULLUP
from systemio import run
import time, random

BTN_START = 5
BTN_STOP  = 18

def wait_press(pin):
    while digitalRead(pin) == 1:
        time.sleep(0.01)
    while digitalRead(pin) == 0:
        time.sleep(0.01)

def main():
    oled = OLED(scl=22, sda=21)
    pinMode(BTN_START, INPUT_PULLUP)
    pinMode(BTN_STOP,  INPUT_PULLUP)

    while True:
        oled.clear()
        oled.text("Reaction Timer", 0, 0)
        oled.text("Press START", 16, 28)
        oled.show()
        wait_press(BTN_START)

        delay = random.uniform(1.5, 4.0)
        oled.clear()
        oled.text("Get Ready...", 16, 28)
        oled.show()
        time.sleep(delay)

        oled.clear()
        oled.text("  >> NOW! <<", 8, 28)
        oled.show()
        t0 = time.ticks_ms()
        wait_press(BTN_STOP)
        ms = time.ticks_diff(time.ticks_ms(), t0)

        oled.clear()
        oled.text("Your time:", 16, 10)
        oled.text(f"  {ms} ms", 16, 30)
        grade = "Excellent!" if ms < 300 else "Good!" if ms < 500 else "Keep trying"
        oled.text(grade, 16, 50)
        oled.show()
        time.sleep(3)

def cleanup():
    print("Game ended")

run(main, cleanup)
```

---

## Project 10 — Light Meter (LDR)

**Components:** OLED, LDR, 10kΩ resistor  
**Concept:** Show ambient light level, percent and status label

```python
from oled import OLED
from analog import analogPin, analogAverage, analogPercent
from systemio import run
import time

LDR_PIN = 34

def light_label(pct):
    if pct < 20: return "Very Dark"
    if pct < 40: return "Dark     "
    if pct < 60: return "Dim      "
    if pct < 80: return "Bright   "
    return "Very Bright"

def main():
    oled = OLED(scl=22, sda=21)
    analogPin(LDR_PIN)

    while True:
        pct = analogPercent(LDR_PIN)
        bar = int(pct * 1.16)    # scale to 0–116px

        oled.clear()
        oled.text("Light Meter", 16, 0)
        oled.line(0, 12, 128, 12)
        oled.text(f"{pct}%", 48, 20)
        oled.text(light_label(pct), 16, 34)
        oled.rect(4, 50, 120, 10)
        for x in range(6, 6 + bar):
            oled.line(x, 52, x, 57)
        oled.show()
        time.sleep(0.5)

def cleanup():
    print("Stopped")

run(main, cleanup)
```

---

## Project 11 — Joystick Direction Display

**Components:** OLED, Analog Joystick Module  
**Concept:** Show X/Y values and direction arrow as text

```python
from oled import OLED
from analog import analogPin, analogRead, mapValue
from digital import pinMode, digitalRead, INPUT_PULLUP
from systemio import run
import time

VRX = 34
VRY = 35
SW  = 5

ARROWS = {
    ("MID","UP")   : "  UP  ",
    ("MID","DOWN") : " DOWN ",
    ("LEFT","MID") : " LEFT ",
    ("RIGHT","MID"): " RIGHT",
    ("LEFT","UP")  : "UP-LFT",
    ("RIGHT","UP") : "UP-RGT",
    ("LEFT","DOWN"): "DN-LFT",
    ("RIGHT","DOWN"): "DN-RGT",
}

def zone(v):
    if v < 30: return "LOW"
    if v > 70: return "HIGH"
    return "MID"

def h_dir(v):
    if v < 30: return "LEFT"
    if v > 70: return "RIGHT"
    return "MID"

def v_dir(v):
    if v < 30: return "UP"
    if v > 70: return "DOWN"
    return "MID"

def main():
    oled = OLED(scl=22, sda=21)
    analogPin(VRX); analogPin(VRY)
    pinMode(SW, INPUT_PULLUP)

    while True:
        x   = mapValue(analogRead(VRX), 0, 4095, 0, 100)
        y   = mapValue(analogRead(VRY), 0, 4095, 0, 100)
        btn = digitalRead(SW) == 0
        key = (h_dir(x), v_dir(y))
        arrow = ARROWS.get(key, "CENTER")

        oled.clear()
        oled.text("Joystick", 32, 0)
        oled.line(0, 12, 128, 12)
        oled.text(f"X:{x:3d}%  Y:{y:3d}%", 0, 18)
        oled.text(arrow, 32, 34)
        oled.text("BTN:ON" if btn else "BTN:--", 32, 50)
        oled.show()
        time.sleep(0.1)

def cleanup():
    print("Stopped")

run(main, cleanup)
```

---

## Project 12 — Soil Moisture Monitor

**Components:** OLED, Capacitive soil moisture sensor  
**Concept:** Moisture percent with status and watering alert

```python
from oled import OLED
from analog import analogPin, analogAverage, analogPercent
from digital import pinMode, digitalWrite, blink, OUTPUT
from systemio import run
import time

SOIL_PIN = 34
LED_PIN  = 4

def status(pct):
    if pct < 25: return "DRY  Water now!"
    if pct < 50: return "LOW  Water soon"
    if pct < 75: return "GOOD Keep going"
    return "WET  Enough!"

def main():
    oled = OLED(scl=22, sda=21)
    analogPin(SOIL_PIN)
    pinMode(LED_PIN, OUTPUT)

    while True:
        raw  = analogPercent(SOIL_PIN)
        pct  = 100 - raw     # invert: high ADC = dry for most sensors
        bar  = int(pct * 1.16)
        msg  = status(pct)

        oled.clear()
        oled.text("Soil Moisture", 4, 0)
        oled.line(0, 12, 128, 12)
        oled.text(f"{pct}%", 48, 18)
        oled.text(msg, 0, 34)
        oled.rect(4, 50, 120, 10)
        for x in range(6, 6 + bar):
            oled.line(x, 52, x, 57)
        oled.show()

        if pct < 25:
            blink(LED_PIN, times=2, on_ms=100, off_ms=100)
        else:
            digitalWrite(LED_PIN, 0)

        time.sleep(3)

def cleanup():
    digitalWrite(LED_PIN, 0)

run(main, cleanup)
```

---

## Project 13 — Sound Level Display (Microphone)

**Components:** OLED, KY-038 / MAX4466 microphone module  
**Concept:** Live amplitude bargraph + peak marker on OLED

```python
from oled import OLED
from analog import analogPin, analogRead, mapValue
from systemio import run
import time

MIC_PIN = 34
SILENCE = 1800

def main():
    oled = OLED(scl=22, sda=21)
    analogPin(MIC_PIN)
    peak = 0

    while True:
        raw       = analogRead(MIC_PIN)
        amplitude = abs(raw - SILENCE)
        if amplitude > peak:
            peak = amplitude
        bar = mapValue(amplitude, 0, max(peak, 1), 0, 116)

        oled.clear()
        oled.text("Sound Level", 16, 0)
        oled.line(0, 12, 128, 12)
        oled.rect(4, 28, 120, 16)
        for x in range(6, 6 + bar):
            oled.line(x, 30, x, 41)
        peak_x = mapValue(peak, 0, max(peak, 1), 6, 122)
        oled.line(peak_x, 26, peak_x, 46)     # peak marker
        oled.text(f"Amp:{amplitude:4d}", 0, 50)
        oled.text(f"Pk:{peak:4d}", 68, 50)
        oled.show()
        peak = int(peak * 0.97)
        time.sleep(0.03)

def cleanup():
    print("Stopped")

run(main, cleanup)
```

---

## Project 14 — Digital Dice on OLED

**Components:** OLED, Push Button  
**Concept:** Draw dice dot patterns using `rect()` on the screen

```python
from oled import OLED
from digital import pinMode, digitalRead, INPUT_PULLUP
from systemio import run
import time, random

BTN_PIN = 5

# Dot positions (x,y) for each face value
DOTS = {
    1: [(52,24)],
    2: [(28,12),(76,36)],
    3: [(28,12),(52,24),(76,36)],
    4: [(28,12),(76,12),(28,36),(76,36)],
    5: [(28,12),(76,12),(52,24),(28,36),(76,36)],
    6: [(28,10),(76,10),(28,24),(76,24),(28,38),(76,38)],
}

def draw_dice(oled, n):
    oled.rect(24, 8, 80, 48)
    for (x, y) in DOTS[n]:
        oled.rect(x, y, 8, 8)
        for dx in range(1, 7):
            for dy in range(1, 7):
                oled.line(x+dx, y+dy, x+dx, y+dy)

def main():
    oled    = OLED(scl=22, sda=21)
    last    = 1
    result  = 1
    pinMode(BTN_PIN, INPUT_PULLUP)

    oled.clear()
    oled.text("Press button", 8, 0)
    oled.text("  to roll!", 8, 50)
    draw_dice(oled, result)
    oled.show()

    while True:
        btn = digitalRead(BTN_PIN)
        if last == 1 and btn == 0:
            for _ in range(8):              # roll animation
                oled.clear()
                draw_dice(oled, random.randint(1, 6))
                oled.show()
                time.sleep(0.1)
            result = random.randint(1, 6)
            oled.clear()
            oled.text(f"   Rolled: {result}", 0, 0)
            draw_dice(oled, result)
            oled.show()
            print("Rolled:", result)
        last = btn
        time.sleep(0.05)

def cleanup():
    print("Dice game ended")

run(main, cleanup)
```

---

## Project 15 — PWM LED Brightness + OLED Display

**Components:** OLED, LED, Potentiometer  
**Concept:** Pot controls LED brightness; OLED shows value and bar live

```python
from oled import OLED
from analog import analogPin, analogRead, analogPercent, mapValue
from digital import pwmSetup, pwmWrite, pwmStop
from systemio import run
import time

POT_PIN = 34
LED_PIN = 4

def main():
    oled = OLED(scl=22, sda=21)
    analogPin(POT_PIN)
    pwmSetup(LED_PIN, freq=1000)

    while True:
        raw  = analogRead(POT_PIN)
        pct  = analogPercent(POT_PIN)
        duty = mapValue(raw, 0, 4095, 0, 1023)
        bar  = mapValue(pct, 0, 100, 0, 116)
        pwmWrite(LED_PIN, duty)

        oled.clear()
        oled.text("LED Brightness", 4, 0)
        oled.line(0, 12, 128, 12)
        oled.text(f"Duty : {duty:4d}", 0, 18)
        oled.text(f"Level: {pct:3d}%", 0, 32)
        oled.rect(4, 50, 120, 10)
        for x in range(6, 6 + bar):
            oled.line(x, 52, x, 57)
        oled.show()
        time.sleep(0.05)

def cleanup():
    pwmStop(LED_PIN)

run(main, cleanup)
```

---

## Project 16 — Servo Angle Display

**Components:** OLED, SG90 Servo, Potentiometer  
**Concept:** Show current servo angle on OLED with a visual arc indicator

```python
from oled import OLED
from analog import analogPin, analogSmooth, mapValue
from digital import pwmSetup, pwmWrite, pwmStop
from systemio import run
import time

POT_PIN   = 34
SERVO_PIN = 4

def angle_duty(a):
    return mapValue(a, 0, 180, 26, 102)

def draw_angle_bar(oled, angle):
    w = mapValue(angle, 0, 180, 0, 116)
    oled.rect(4, 50, 120, 10)
    for x in range(6, 6 + w):
        oled.line(x, 52, x, 57)

def main():
    oled = OLED(scl=22, sda=21)
    analogPin(POT_PIN)
    pwmSetup(SERVO_PIN, freq=50)

    while True:
        smooth = analogSmooth(POT_PIN, window=8)
        angle  = mapValue(smooth, 0, 4095, 0, 180)
        pwmWrite(SERVO_PIN, angle_duty(angle))

        oled.clear()
        oled.text("Servo Control", 8, 0)
        oled.line(0, 12, 128, 12)
        oled.text(f"Angle: {angle:3d} deg", 16, 24)
        oled.text("0" + " "*12 + "180", 4, 38)
        draw_angle_bar(oled, angle)
        oled.show()
        time.sleep(0.05)

def cleanup():
    pwmStop(SERVO_PIN)

run(main, cleanup)
```

---

## Project 17 — Gas / Air Quality Monitor

**Components:** OLED, MQ-2 or MQ-135 sensor, LED, Buzzer  
**Concept:** Analog gas level with color-coded status message on OLED

```python
from oled import OLED
from analog import analogPin, analogAverage, analogPercent
from digital import pinMode, digitalWrite, blink, OUTPUT
from systemio import run
import time

GAS_PIN    = 34
LED_PIN    = 4
BUZZER_PIN = 5

def gas_status(pct):
    if pct < 30: return ("NORMAL", "Air is clean")
    if pct < 60: return ("WARNING", "Ventilate now")
    return ("DANGER!", "Leave area!")

def main():
    oled = OLED(scl=22, sda=21)
    analogPin(GAS_PIN)
    pinMode(LED_PIN, OUTPUT)
    pinMode(BUZZER_PIN, OUTPUT)
    print("Warming up sensor — 20s...")
    time.sleep(20)

    while True:
        pct          = analogPercent(GAS_PIN)
        bar          = int(pct * 1.16)
        label, note  = gas_status(pct)

        oled.clear()
        oled.text("Air Quality", 16, 0)
        oled.line(0, 12, 128, 12)
        oled.text(f"Level: {pct}%", 0, 18)
        oled.text(label, 32, 32)
        oled.text(note, 0, 46)
        oled.rect(4, 56, 120, 6)
        for x in range(6, 6 + bar):
            oled.line(x, 57, x, 59)
        oled.show()

        if pct >= 60:
            blink(LED_PIN, times=3, on_ms=100, off_ms=50)
            blink(BUZZER_PIN, times=2, on_ms=100, off_ms=50)
        elif pct >= 30:
            blink(LED_PIN, times=1, on_ms=200, off_ms=0)
            digitalWrite(BUZZER_PIN, 0)
        else:
            digitalWrite(LED_PIN, 0)
            digitalWrite(BUZZER_PIN, 0)

        time.sleep(1)

def cleanup():
    digitalWrite(LED_PIN, 0)
    digitalWrite(BUZZER_PIN, 0)

run(main, cleanup)
```

---

## Project 18 — Multi-Sensor Dashboard

**Components:** OLED, Potentiometer, LDR, Push Button  
**Concept:** Show 3 sensor readings together on one screen — split layout

```python
from oled import OLED
from analog import analogPin, analogPercent, analogVoltage
from digital import pinMode, digitalRead, INPUT_PULLUP
from systemio import run
import time

POT_PIN = 34
LDR_PIN = 35
BTN_PIN = 5

def mini_bar(pct, width=30):
    filled = int(pct / 100 * width)
    return "[" + "=" * filled + " " * (width - filled) + "]"

def main():
    oled = OLED(scl=22, sda=21)
    analogPin(POT_PIN)
    analogPin(LDR_PIN)
    pinMode(BTN_PIN, INPUT_PULLUP)

    while True:
        knob  = analogPercent(POT_PIN)
        light = analogPercent(LDR_PIN)
        volt  = analogVoltage(POT_PIN)
        btn   = "ON " if digitalRead(BTN_PIN) == 0 else "OFF"

        oled.clear()
        oled.text("Sensor Dashboard", 0, 0)
        oled.line(0, 10, 128, 10)
        oled.text(f"Knob :{knob:3d}%", 0, 14)
        oled.text(f"Light:{light:3d}%", 0, 26)
        oled.text(f"Volt :{volt:.2f}V", 0, 38)
        oled.text(f"Btn  :{btn}", 0, 50)
        oled.line(100, 10, 100, 64)
        oled.rect(104, 14, 20, knob // 5 if knob else 1)
        oled.show()
        time.sleep(0.2)

def cleanup():
    print("Dashboard stopped")

run(main, cleanup)
```

---

## Project 19 — Interrupt Event Logger

**Components:** OLED, 2 Push Buttons  
**Concept:** Each button press is logged with timestamp on OLED — last 4 events shown

```python
from oled import OLED
from digital import pinMode, attachInterrupt, detachInterrupt, FALLING, INPUT_PULLUP
from systemio import run
import time

BTN_A = 5
BTN_B = 18
log   = []
start = time.ticks_ms()

def ts():
    return time.ticks_diff(time.ticks_ms(), start) // 1000

def on_a(p):
    log.append(f"A pressed  t={ts()}s")
    if len(log) > 4: log.pop(0)
    print(log[-1])

def on_b(p):
    log.append(f"B pressed  t={ts()}s")
    if len(log) > 4: log.pop(0)
    print(log[-1])

def main():
    oled = OLED(scl=22, sda=21)
    pinMode(BTN_A, INPUT_PULLUP)
    pinMode(BTN_B, INPUT_PULLUP)
    attachInterrupt(BTN_A, on_a, FALLING, debounce_ms=80)
    attachInterrupt(BTN_B, on_b, FALLING, debounce_ms=80)

    while True:
        oled.clear()
        oled.text("Event Log", 24, 0)
        oled.line(0, 10, 128, 10)
        for i, entry in enumerate(log[-4:]):
            oled.text(entry[:16], 0, 14 + i * 12)
        if not log:
            oled.text("No events yet", 8, 28)
        oled.show()
        time.sleep(0.1)

def cleanup():
    detachInterrupt(BTN_A)
    detachInterrupt(BTN_B)
    print("Logger stopped")

run(main, cleanup)
```

---

## Project 20 — Full OLED System Monitor

**Components:** OLED, Potentiometer (knob), LDR, Push Button, LED, Buzzer  
**Concept:** Cycling 3 screen pages with button — each page shows a different sensor; LED + buzzer on threshold

```python
from oled import OLED
from analog import analogPin, analogRead, analogPercent, analogVoltage, analogSmooth, mapValue
from digital import (pinMode, digitalRead, digitalWrite,
                     pwmSetup, pwmWrite, pwmStop,
                     blink, INPUT_PULLUP, OUTPUT)
from systemio import run
import time

POT_PIN  = 34
LDR_PIN  = 35
BTN_PIN  = 5
LED_PIN  = 4
BUZ_PIN  = 18
PWM_LED  = 19

PAGE_COUNT = 3

def draw_bar(oled, pct, y=54):
    w = int(pct * 1.16)
    oled.rect(4, y, 120, 8)
    for x in range(6, 6 + w):
        oled.line(x, y+1, x, y+6)

def page_knob(oled):
    raw  = analogRead(POT_PIN)
    pct  = analogPercent(POT_PIN)
    volt = analogVoltage(POT_PIN)
    oled.text("[ Knob ]", 28, 0)
    oled.line(0, 10, 128, 10)
    oled.text(f"Raw : {raw}", 0, 14)
    oled.text(f"Pct : {pct}%", 0, 26)
    oled.text(f"Volt: {volt:.3f}V", 0, 38)
    draw_bar(oled, pct)

def page_light(oled):
    pct = analogPercent(LDR_PIN)
    lbl = "Very Dark" if pct<20 else "Dark" if pct<40 else "Dim" if pct<60 else "Bright"
    oled.text("[ Light ]", 28, 0)
    oled.line(0, 10, 128, 10)
    oled.text(f"Level: {pct}%", 0, 18)
    oled.text(lbl, 28, 34)
    draw_bar(oled, pct)

def page_control(oled):
    smooth = analogSmooth(POT_PIN, window=8)
    duty   = mapValue(smooth, 0, 4095, 0, 1023)
    pct    = mapValue(smooth, 0, 4095, 0, 100)
    pwmWrite(PWM_LED, duty)
    oled.text("[ PWM LED ]", 16, 0)
    oled.line(0, 10, 128, 10)
    oled.text(f"Duty : {duty:4d}", 0, 18)
    oled.text(f"Level: {pct:3d}%", 0, 32)
    draw_bar(oled, pct)

PAGES = [page_knob, page_light, page_control]

def main():
    oled = OLED(scl=22, sda=21)
    analogPin(POT_PIN)
    analogPin(LDR_PIN)
    pinMode(BTN_PIN, INPUT_PULLUP)
    pinMode(LED_PIN, OUTPUT)
    pinMode(BUZ_PIN, OUTPUT)
    pwmSetup(PWM_LED, freq=1000)

    page     = 0
    last_btn = 1

    while True:
        btn = digitalRead(BTN_PIN)
        if last_btn == 1 and btn == 0:
            page = (page + 1) % PAGE_COUNT
        last_btn = btn

        oled.clear()
        PAGES[page](oled)
        oled.text(f"pg {page+1}/{PAGE_COUNT}", 88, 0)
        oled.show()

        knob = analogPercent(POT_PIN)
        if knob > 85:
            blink(LED_PIN, times=1, on_ms=80, off_ms=0)
            blink(BUZ_PIN, times=1, on_ms=40, off_ms=0)
        else:
            digitalWrite(LED_PIN, 0)
            digitalWrite(BUZ_PIN, 0)

        time.sleep(0.1)

def cleanup():
    pwmStop(PWM_LED)
    for p in [LED_PIN, BUZ_PIN]:
        digitalWrite(p, 0)
    print("System monitor stopped")

run(main, cleanup)
```

---

## 📊 Quick Reference Table

| # | Project | Sensors Used | Key OLED Calls | Analog | Digital |
|---|---------|-------------|----------------|:------:|:-------:|
| 1 | Hello World | — | `text`, `show` | — | — |
| 2 | Live Counter | — | `text`, `line`, loop | — | — |
| 3 | Button Counter | Push Button | `text` | — | ✅ |
| 4 | Pot Value Display | Potentiometer | `text`, `rect`, fill | ✅ | — |
| 5 | Voltage Meter | Potentiometer | `text`, bar fill | ✅ | — |
| 6 | Temperature | NTC Thermistor | `text`, `rect` | ✅ | — |
| 7 | Bargraph | Potentiometer | `rect`, fill segments | ✅ | — |
| 8 | Digital Clock | — | `text`, ticks | — | — |
| 9 | Reaction Timer | 2 Buttons | `text`, ticks | — | ✅ |
| 10 | Light Meter | LDR | `text`, bar | ✅ | — |
| 11 | Joystick Display | Joystick Module | `text`, directions | ✅ | ✅ |
| 12 | Soil Moisture | Moisture sensor | `text`, `rect`, bar | ✅ | ✅ |
| 13 | Sound Level | Microphone | `rect`, peak marker | ✅ | — |
| 14 | Digital Dice | Push Button | `rect`, dot patterns | — | ✅ |
| 15 | LED Brightness | Pot + LED | `text`, bar, PWM | ✅ | ✅ |
| 16 | Servo Angle | Pot + Servo | `text`, angle bar | ✅ | ✅ |
| 17 | Gas Monitor | MQ sensor | `text`, status label | ✅ | ✅ |
| 18 | Multi-Sensor | Pot + LDR + Btn | `text`, split layout | ✅ | ✅ |
| 19 | Event Logger | 2 Buttons + IRQ | `text`, scrolling log | — | ✅ |
| 20 | System Monitor | Pot + LDR + Btn | Pages, all methods | ✅ | ✅ |

---

## 🧠 OLED Drawing Tips

| Task | Method | Example |
|------|--------|---------|
| Write text | `oled.text(msg, x, y)` | `oled.text("Hi", 0, 0)` |
| Draw a line | `oled.line(x1,y1,x2,y2)` | `oled.line(0,12,128,12)` — horizontal divider |
| Draw a box | `oled.rect(x,y,w,h)` | `oled.rect(4,50,120,10)` — bar border |
| Fill a bar | loop `oled.line(x,y1,x,y2)` | column-by-column fill |
| Clear screen | `oled.clear()` | Always call before redraw |
| Push to screen | `oled.show()` | Always call after drawing |

> **All projects use `run(main, cleanup)`** — pressing **Ctrl+C** always exits cleanly and turns off all outputs safely.
