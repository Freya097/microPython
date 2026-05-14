# 🔌 20 MicroPython Digital Basic Projects
### Using `digital.py` and `systemio.py` Libraries — ESP32

---

## How to Use These Libraries

```python
from digital import pinMode, digitalWrite, digitalRead, togglePin, pulse, blink
from digital import pwmSetup, pwmWrite, pwmWritePercent, pwmFreq, pwmStop
from digital import attachInterrupt, detachInterrupt
from digital import INPUT, OUTPUT, INPUT_PULLUP, INPUT_PULLDOWN, RISING, FALLING, CHANGE
from systemio import run
import time
```

---

## Project 1 — LED Blink

**Components:** LED, 220Ω resistor  
**Concept:** Basic digital output, safe program exit

```python
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
import time

LED_PIN = 4

def setup():
    pinMode(LED_PIN, OUTPUT)

def main():
    setup()
    print("LED Blink Started")
    while True:
        digitalWrite(LED_PIN, 1)
        print("LED: ON")
        time.sleep(0.5)
        digitalWrite(LED_PIN, 0)
        print("LED: OFF")
        time.sleep(0.5)

def cleanup():
    digitalWrite(LED_PIN, 0)
    print("LED turned OFF")

run(main, cleanup)
```

---

## Project 2 — LED Toggle with Button

**Components:** LED, Push Button, 10kΩ pull-down resistor  
**Concept:** Digital input read, button-controlled toggle

```python
from digital import pinMode, digitalWrite, digitalRead, INPUT_PULLUP, OUTPUT
from systemio import run
import time

LED_PIN    = 4
BUTTON_PIN = 5

def setup():
    pinMode(LED_PIN, OUTPUT)
    pinMode(BUTTON_PIN, INPUT_PULLUP)

def main():
    setup()
    led_state = 0
    last_button = 1
    print("Button Toggle Started")
    while True:
        current = digitalRead(BUTTON_PIN)
        if last_button == 1 and current == 0:   # falling edge (active LOW)
            led_state = not led_state
            digitalWrite(LED_PIN, led_state)
            print("LED:", "ON" if led_state else "OFF")
        last_button = current
        time.sleep(0.05)

def cleanup():
    digitalWrite(LED_PIN, 0)

run(main, cleanup)
```

---

## Project 3 — LED Blink with `blink()` Helper

**Components:** LED, 220Ω resistor  
**Concept:** Using the built-in `blink()` function for pattern control

```python
from digital import pinMode, digitalWrite, blink, OUTPUT
from systemio import run
import time

LED_PIN = 4

def setup():
    pinMode(LED_PIN, OUTPUT)

def main():
    setup()
    print("Blink Pattern Started")
    while True:
        print("Fast blink x5")
        blink(LED_PIN, times=5, on_ms=100, off_ms=100)
        time.sleep(1)
        print("Slow blink x3")
        blink(LED_PIN, times=3, on_ms=500, off_ms=500)
        time.sleep(1)

def cleanup():
    digitalWrite(LED_PIN, 0)

run(main, cleanup)
```

---

## Project 4 — Traffic Light Simulator

**Components:** Red, Yellow, Green LEDs, 220Ω resistors  
**Concept:** Sequential digital output, timed state machine

```python
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
import time

RED_PIN    = 4
YELLOW_PIN = 5
GREEN_PIN  = 18

LIGHTS = [RED_PIN, YELLOW_PIN, GREEN_PIN]

def setup():
    for pin in LIGHTS:
        pinMode(pin, OUTPUT)
        digitalWrite(pin, 0)

def set_light(red, yellow, green):
    digitalWrite(RED_PIN,    red)
    digitalWrite(YELLOW_PIN, yellow)
    digitalWrite(GREEN_PIN,  green)

def main():
    setup()
    print("Traffic Light Started")
    while True:
        print("RED")
        set_light(1, 0, 0)
        time.sleep(3)

        print("YELLOW")
        set_light(0, 1, 0)
        time.sleep(1)

        print("GREEN")
        set_light(0, 0, 1)
        time.sleep(3)

        print("YELLOW")
        set_light(0, 1, 0)
        time.sleep(1)

def cleanup():
    for pin in LIGHTS:
        digitalWrite(pin, 0)
    print("All lights OFF")

run(main, cleanup)
```

---

## Project 5 — PWM LED Fade In/Out

**Components:** LED, 220Ω resistor  
**Concept:** PWM duty cycle control, smooth brightness fade

```python
from digital import pwmSetup, pwmWrite, pwmStop
from systemio import run
import time

LED_PIN = 4

def setup():
    pwmSetup(LED_PIN, freq=1000)

def main():
    setup()
    print("LED Fade Started")
    while True:
        for duty in range(0, 1024, 10):
            pwmWrite(LED_PIN, duty)
            time.sleep(0.01)
        for duty in range(1023, -1, -10):
            pwmWrite(LED_PIN, duty)
            time.sleep(0.01)

def cleanup():
    pwmStop(LED_PIN)
    print("PWM Stopped")

run(main, cleanup)
```

---

## Project 6 — PWM LED Brightness via Button

**Components:** LED, 2 Push Buttons (Up/Down), 220Ω resistor  
**Concept:** PWM percentage control via button presses

```python
from digital import pinMode, digitalRead, pwmSetup, pwmWritePercent, pwmStop
from digital import INPUT_PULLUP, OUTPUT
from systemio import run
import time

LED_PIN    = 4
BTN_UP     = 5
BTN_DOWN   = 18
STEP       = 10

def setup():
    pwmSetup(LED_PIN, freq=1000)
    pinMode(BTN_UP, INPUT_PULLUP)
    pinMode(BTN_DOWN, INPUT_PULLUP)

def main():
    setup()
    brightness = 50
    pwmWritePercent(LED_PIN, brightness)
    print("Brightness Control Started — brightness:", brightness, "%")

    while True:
        if digitalRead(BTN_UP) == 0:
            brightness = min(100, brightness + STEP)
            pwmWritePercent(LED_PIN, brightness)
            print("Brightness:", brightness, "%")
            time.sleep(0.3)

        if digitalRead(BTN_DOWN) == 0:
            brightness = max(0, brightness - STEP)
            pwmWritePercent(LED_PIN, brightness)
            print("Brightness:", brightness, "%")
            time.sleep(0.3)

        time.sleep(0.05)

def cleanup():
    pwmStop(LED_PIN)

run(main, cleanup)
```

---

## Project 7 — Doorbell with Buzzer Pulse

**Components:** Active Buzzer, Push Button  
**Concept:** Using `pulse()` to fire a timed output on button press

```python
from digital import pinMode, digitalRead, pulse, OUTPUT, INPUT_PULLUP
from systemio import run
import time

BUZZER_PIN = 4
BUTTON_PIN = 5

def setup():
    pinMode(BUZZER_PIN, OUTPUT)
    pinMode(BUTTON_PIN, INPUT_PULLUP)

def main():
    setup()
    print("Doorbell Ready")
    while True:
        if digitalRead(BUTTON_PIN) == 0:
            print("DING DONG!")
            pulse(BUZZER_PIN, duration_ms=200)
            time.sleep(0.3)
            pulse(BUZZER_PIN, duration_ms=400)
            time.sleep(0.5)

def cleanup():
    from digital import digitalWrite
    digitalWrite(BUZZER_PIN, 0)

run(main, cleanup)
```

---

## Project 8 — Button Counter with LED Display

**Components:** Push Button, 4 LEDs  
**Concept:** Counting button presses and showing binary value on LEDs

```python
from digital import pinMode, digitalWrite, digitalRead, INPUT_PULLUP, OUTPUT
from systemio import run
import time

BUTTON_PIN = 5
LED_PINS   = [4, 18, 19, 21]    # bit0, bit1, bit2, bit3

def setup():
    pinMode(BUTTON_PIN, INPUT_PULLUP)
    for pin in LED_PINS:
        pinMode(pin, OUTPUT)
        digitalWrite(pin, 0)

def show_binary(value):
    for i, pin in enumerate(LED_PINS):
        digitalWrite(pin, (value >> i) & 1)

def main():
    setup()
    count    = 0
    last_btn = 1
    print("Counter Started")
    while True:
        current = digitalRead(BUTTON_PIN)
        if last_btn == 1 and current == 0:
            count = (count + 1) % 16
            show_binary(count)
            print("Count:", count)
        last_btn = current
        time.sleep(0.05)

def cleanup():
    for pin in LED_PINS:
        digitalWrite(pin, 0)

run(main, cleanup)
```

---

## Project 9 — PIR Motion Detector Alert

**Components:** PIR Sensor, LED, Buzzer  
**Concept:** Digital read from sensor, multi-output alert

```python
from digital import pinMode, digitalWrite, blink, INPUT, OUTPUT
from systemio import run
import time

PIR_PIN    = 34     # PIR output (input-only GPIO on ESP32)
LED_PIN    = 4
BUZZER_PIN = 5

def setup():
    pinMode(PIR_PIN, INPUT)
    pinMode(LED_PIN, OUTPUT)
    pinMode(BUZZER_PIN, OUTPUT)

def main():
    setup()
    print("Motion Detector Active")
    while True:
        if digitalRead(PIR_PIN) == 1:
            print("⚠ Motion Detected!")
            blink(LED_PIN, times=3, on_ms=100, off_ms=100)
            blink(BUZZER_PIN, times=2, on_ms=200, off_ms=100)
        time.sleep(0.2)

def cleanup():
    digitalWrite(LED_PIN, 0)
    digitalWrite(BUZZER_PIN, 0)

from digital import digitalRead
run(main, cleanup)
```

---

## Project 10 — Interrupt-Based Button Press Counter

**Components:** Push Button  
**Concept:** Hardware interrupt with debounce using `attachInterrupt()`

```python
from digital import pinMode, attachInterrupt, detachInterrupt, INPUT_PULLUP, FALLING
from systemio import run
import time

BUTTON_PIN = 5
press_count = 0

def on_button_press(pin):
    global press_count
    press_count += 1
    print("Button Pressed! Count:", press_count)

def setup():
    pinMode(BUTTON_PIN, INPUT_PULLUP)
    attachInterrupt(BUTTON_PIN, on_button_press, trigger=FALLING, debounce_ms=50)

def main():
    setup()
    print("Interrupt Counter Running — press button anytime")
    while True:
        time.sleep(1)
        print("Total presses so far:", press_count)

def cleanup():
    detachInterrupt(BUTTON_PIN)
    print("Interrupt detached")

run(main, cleanup)
```

---

## Project 11 — SOS Morse Code LED

**Components:** LED, 220Ω resistor  
**Concept:** Encoding Morse code using `pulse()` and `blink()`

```python
from digital import pinMode, pulse, OUTPUT
from systemio import run
import time

LED_PIN = 4
DOT     = 150
DASH    = 450
GAP     = 150
LETTER  = 500

def morse_dot():
    pulse(LED_PIN, DOT)
    time.sleep_ms(GAP)

def morse_dash():
    pulse(LED_PIN, DASH)
    time.sleep_ms(GAP)

def setup():
    pinMode(LED_PIN, OUTPUT)

def main():
    setup()
    print("SOS Morse Code Transmitting")
    while True:
        # S — three dots
        for _ in range(3): morse_dot()
        time.sleep_ms(LETTER)
        # O — three dashes
        for _ in range(3): morse_dash()
        time.sleep_ms(LETTER)
        # S — three dots
        for _ in range(3): morse_dot()
        print("SOS sent")
        time.sleep(2)

def cleanup():
    from digital import digitalWrite
    digitalWrite(LED_PIN, 0)

run(main, cleanup)
```

---

## Project 12 — Relay-Controlled AC Appliance

**Components:** 5V Relay Module, AC load (lamp/fan)  
**Concept:** Digital output to drive relay, timed on/off cycle

```python
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
import time

RELAY_PIN = 4     # Active HIGH relay; change to LOW if your module is active LOW

def setup():
    pinMode(RELAY_PIN, OUTPUT)
    digitalWrite(RELAY_PIN, 0)    # Start OFF

def main():
    setup()
    print("Relay Timer Started")
    while True:
        print("Relay ON  — appliance running")
        digitalWrite(RELAY_PIN, 1)
        time.sleep(5)

        print("Relay OFF — appliance stopped")
        digitalWrite(RELAY_PIN, 0)
        time.sleep(5)

def cleanup():
    digitalWrite(RELAY_PIN, 0)
    print("Relay OFF — appliance safe")

run(main, cleanup)
```

---

## Project 13 — Night Light (LDR + LED)

**Components:** LDR, 10kΩ resistor (voltage divider → digital threshold), LED  
**Concept:** Digital read from LDR threshold, auto night light

```python
from digital import pinMode, digitalWrite, digitalRead, INPUT, OUTPUT
from systemio import run
import time

LDR_PIN = 34    # Connect LDR voltage-divider to a digital GPIO or comparator output
LED_PIN = 4

def setup():
    pinMode(LDR_PIN, INPUT)
    pinMode(LED_PIN, OUTPUT)

def main():
    setup()
    print("Night Light Active")
    while True:
        dark = (digitalRead(LDR_PIN) == 0)   # LOW = dark (adjust for your circuit)
        digitalWrite(LED_PIN, 1 if dark else 0)
        print("Dark" if dark else "Bright", "— LED", "ON" if dark else "OFF")
        time.sleep(1)

def cleanup():
    digitalWrite(LED_PIN, 0)

run(main, cleanup)
```

---

## Project 14 — PWM RGB LED Color Cycle

**Components:** Common-cathode RGB LED, 3x 220Ω resistors  
**Concept:** Multi-channel PWM for smooth color mixing

```python
from digital import pwmSetup, pwmWrite, pwmStop
from systemio import run
import time

R_PIN = 4
G_PIN = 5
B_PIN = 18

def setup():
    for pin in [R_PIN, G_PIN, B_PIN]:
        pwmSetup(pin, freq=1000)

def set_rgb(r, g, b):
    pwmWrite(R_PIN, r)
    pwmWrite(G_PIN, g)
    pwmWrite(B_PIN, b)

def main():
    setup()
    print("RGB Cycle Started")
    step = 5
    while True:
        # Red → Green
        for i in range(0, 1024, step):
            set_rgb(1023 - i, i, 0)
            time.sleep(0.005)
        # Green → Blue
        for i in range(0, 1024, step):
            set_rgb(0, 1023 - i, i)
            time.sleep(0.005)
        # Blue → Red
        for i in range(0, 1024, step):
            set_rgb(i, 0, 1023 - i)
            time.sleep(0.005)

def cleanup():
    for pin in [R_PIN, G_PIN, B_PIN]:
        pwmStop(pin)
    print("RGB OFF")

run(main, cleanup)
```

---

## Project 15 — Tilt Sensor Alarm

**Components:** Tilt/Ball switch sensor, LED, Buzzer  
**Concept:** CHANGE interrupt triggers alarm when device tilts

```python
from digital import pinMode, digitalWrite, attachInterrupt, CHANGE, INPUT_PULLUP, OUTPUT
from systemio import run
import time

TILT_PIN   = 5
LED_PIN    = 4
BUZZER_PIN = 18
alarm_on   = False

def on_tilt(pin):
    global alarm_on
    alarm_on = True
    print("Tilt Detected!")

def setup():
    pinMode(LED_PIN, OUTPUT)
    pinMode(BUZZER_PIN, OUTPUT)
    attachInterrupt(TILT_PIN, on_tilt, trigger=CHANGE, debounce_ms=100)

def main():
    global alarm_on
    setup()
    print("Tilt Alarm Armed")
    while True:
        if alarm_on:
            from digital import blink
            blink(LED_PIN, times=5, on_ms=100, off_ms=100)
            blink(BUZZER_PIN, times=3, on_ms=150, off_ms=100)
            alarm_on = False
        time.sleep(0.1)

def cleanup():
    from digital import detachInterrupt
    detachInterrupt(TILT_PIN)
    digitalWrite(LED_PIN, 0)
    digitalWrite(BUZZER_PIN, 0)

run(main, cleanup)
```

---

## Project 16 — Toggle Latching Switch

**Components:** Push Button, LED  
**Concept:** Latch state on each press — one button, on/off toggle

```python
from digital import pinMode, digitalWrite, digitalRead, INPUT_PULLUP, OUTPUT
from systemio import run
import time

BUTTON_PIN = 5
LED_PIN    = 4

def setup():
    pinMode(BUTTON_PIN, INPUT_PULLUP)
    pinMode(LED_PIN, OUTPUT)

def main():
    setup()
    state    = False
    last_btn = 1
    print("Latch Toggle Ready")
    while True:
        btn = digitalRead(BUTTON_PIN)
        if last_btn == 1 and btn == 0:
            state = not state
            digitalWrite(LED_PIN, state)
            print("Latch:", "ON" if state else "OFF")
        last_btn = btn
        time.sleep(0.05)

def cleanup():
    digitalWrite(LED_PIN, 0)

run(main, cleanup)
```

---

## Project 17 — Heartbeat LED (Breathing Pattern)

**Components:** LED, 220Ω resistor  
**Concept:** Sine-wave-like breathing using PWM for a heartbeat effect

```python
from digital import pwmSetup, pwmWrite, pwmStop
from systemio import run
import math
import time

LED_PIN = 4

def setup():
    pwmSetup(LED_PIN, freq=1000)

def main():
    setup()
    print("Heartbeat Started")
    t = 0
    while True:
        # Two quick beats then a pause — classic heartbeat
        duty = int(abs(math.sin(t * 6)) * 1023)
        pwmWrite(LED_PIN, duty)
        t += 0.05
        time.sleep(0.02)

def cleanup():
    pwmStop(LED_PIN)
    print("Heartbeat Stopped")

run(main, cleanup)
```

---

## Project 18 — Reaction Timer Game

**Components:** 2 Push Buttons (Player 1 & 2), 3 LEDs (Ready/P1/P2)  
**Concept:** Reaction speed test using `time.ticks_ms()` and digital I/O

```python
from digital import pinMode, digitalWrite, digitalRead, blink, INPUT_PULLUP, OUTPUT
from systemio import run
import time, random

BTN1 = 5;  BTN2 = 18
LED_READY = 4;  LED_P1 = 19;  LED_P2 = 21

def setup():
    for btn in [BTN1, BTN2]:
        pinMode(btn, INPUT_PULLUP)
    for led in [LED_READY, LED_P1, LED_P2]:
        pinMode(led, OUTPUT)
        digitalWrite(led, 0)

def main():
    setup()
    print("Reaction Timer — press your button when LED lights up!")
    while True:
        time.sleep(random.uniform(2, 5))
        digitalWrite(LED_READY, 1)
        start = time.ticks_ms()
        winner = None
        while winner is None:
            if digitalRead(BTN1) == 0:
                winner = 1
            elif digitalRead(BTN2) == 0:
                winner = 2
        elapsed = time.ticks_diff(time.ticks_ms(), start)
        digitalWrite(LED_READY, 0)
        win_led = LED_P1 if winner == 1 else LED_P2
        blink(win_led, times=3, on_ms=200, off_ms=100)
        print(f"Player {winner} wins! Reaction time: {elapsed} ms")
        time.sleep(2)

def cleanup():
    for led in [LED_READY, LED_P1, LED_P2]:
        digitalWrite(led, 0)

run(main, cleanup)
```

---

## Project 19 — PWM Servo Motor Control

**Components:** SG90 Servo Motor  
**Concept:** PWM frequency and duty for servo angle control

```python
from digital import pwmSetup, pwmWrite, pwmFreq, pwmStop
from systemio import run
import time

SERVO_PIN = 4
# SG90: 50Hz, duty 1ms=26, 1.5ms=77, 2ms=102  (at 1023 scale, 50Hz)

def angle_to_duty(angle):
    """Convert 0–180 degrees to PWM duty (0–1023 at 50Hz)."""
    min_duty = 26
    max_duty = 102
    return int(min_duty + (angle / 180.0) * (max_duty - min_duty))

def setup():
    pwmSetup(SERVO_PIN, freq=50)

def main():
    setup()
    print("Servo Sweep Started")
    while True:
        for angle in range(0, 181, 10):
            pwmWrite(SERVO_PIN, angle_to_duty(angle))
            print(f"Angle: {angle}°")
            time.sleep(0.05)
        for angle in range(180, -1, -10):
            pwmWrite(SERVO_PIN, angle_to_duty(angle))
            print(f"Angle: {angle}°")
            time.sleep(0.05)

def cleanup():
    pwmStop(SERVO_PIN)
    print("Servo stopped")

run(main, cleanup)
```

---

## Project 20 — Digital Dice (7 LEDs)

**Components:** 7 LEDs (dice-face layout), Push Button  
**Concept:** Random number display using dot patterns, `blink()` for roll animation

```python
from digital import pinMode, digitalWrite, digitalRead, blink, INPUT_PULLUP, OUTPUT
from systemio import run
import time, random

BUTTON_PIN = 5
# LED pins mapped to dice positions (top-left, top-right, mid-left, center, mid-right, bot-left, bot-right)
LEDS = [4, 18, 19, 21, 22, 23, 25]

# Dice face patterns: index = position 0-6 maps to LEDS list
DICE = {
    1: [0,0,0,1,0,0,0],
    2: [1,0,0,0,0,0,1],
    3: [1,0,0,1,0,0,1],
    4: [1,1,0,0,0,1,1],
    5: [1,1,0,1,0,1,1],
    6: [1,1,1,0,1,1,1],
}

def setup():
    pinMode(BUTTON_PIN, INPUT_PULLUP)
    for pin in LEDS:
        pinMode(pin, OUTPUT)
        digitalWrite(pin, 0)

def show_face(n):
    pattern = DICE[n]
    for i, pin in enumerate(LEDS):
        digitalWrite(pin, pattern[i])

def roll_animation():
    for _ in range(8):
        show_face(random.randint(1, 6))
        time.sleep(0.1)

def main():
    setup()
    print("Digital Dice Ready — press button to roll!")
    last_btn = 1
    while True:
        btn = digitalRead(BUTTON_PIN)
        if last_btn == 1 and btn == 0:
            print("Rolling...")
            roll_animation()
            result = random.randint(1, 6)
            show_face(result)
            print("Result:", result)
        last_btn = btn
        time.sleep(0.05)

def cleanup():
    for pin in LEDS:
        digitalWrite(pin, 0)

run(main, cleanup)
```

---

## Quick Reference Table

| # | Project | Key Functions Used | GPIO Type |
|---|---------|-------------------|-----------|
| 1 | LED Blink | `digitalWrite`, `pinMode` | Output |
| 2 | Button Toggle | `digitalRead`, `INPUT_PULLUP` | In + Out |
| 3 | Blink Patterns | `blink()` | Output |
| 4 | Traffic Light | `digitalWrite`, timing | Output |
| 5 | PWM Fade | `pwmSetup`, `pwmWrite` | PWM Out |
| 6 | Brightness Control | `pwmWritePercent`, button | PWM + In |
| 7 | Doorbell | `pulse()` | Output |
| 8 | Binary Counter | `digitalRead`, `digitalWrite` | In + Out |
| 9 | PIR Motion Alert | `digitalRead`, `blink` | Input |
| 10 | Interrupt Counter | `attachInterrupt`, debounce | IRQ |
| 11 | SOS Morse Code | `pulse()`, timing | Output |
| 12 | Relay Control | `digitalWrite`, relay | Output |
| 13 | Night Light | `digitalRead`, LDR | In + Out |
| 14 | RGB Color Cycle | Multi-channel PWM | PWM Out |
| 15 | Tilt Alarm | `attachInterrupt`, `CHANGE` | IRQ |
| 16 | Latch Toggle | Edge detection | In + Out |
| 17 | Heartbeat LED | `pwmWrite`, `math.sin` | PWM Out |
| 18 | Reaction Timer | `ticks_ms`, multi-GPIO | In + Out |
| 19 | Servo Sweep | `pwmSetup` 50Hz | PWM Out |
| 20 | Digital Dice | Pattern array, `blink` | In + Out |

---

> **Tip:** All projects use `run(main, cleanup)` from `systemio.py` so pressing **Ctrl+C** always exits safely and turns off outputs cleanly.
