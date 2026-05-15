# ESP32 MicroPython Digital I/O Projects
### Using `digital.py` + `systemio.py` — Safe Exit Pattern

---

## Required Libraries

```python
from digital import (pinMode, digitalWrite, digitalRead, togglePin,
                     pulse, blink, pwmSetup, pwmWrite, pwmWritePercent,
                     pwmStop, attachInterrupt, detachInterrupt,
                     INPUT, OUTPUT, INPUT_PULLUP, INPUT_PULLDOWN,
                     RISING, FALLING, CHANGE)
from systemio import run
import time
```

> **All projects use `run(main, cleanup)`**
> Press **Ctrl+C** anytime — `cleanup()` always turns off pins safely.

---

---

# 1. blink.py — LED Blink

```python
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
import time

LED = 2

def setup():
    pinMode(LED, OUTPUT)

def main():
    setup()
    print("LED Blink Started")
    while True:
        digitalWrite(LED, 1)
        print("ON")
        time.sleep(1)
        digitalWrite(LED, 0)
        print("OFF")
        time.sleep(1)

def cleanup():
    digitalWrite(LED, 0)
    print("LED OFF — Safe Exit")

run(main, cleanup)
```

---

# 2. button_led.py — Push Button LED Control

```python
from digital import pinMode, digitalWrite, digitalRead, INPUT_PULLUP, OUTPUT
from systemio import run
import time

LED = 2
BTN = 4

def setup():
    pinMode(LED, OUTPUT)
    pinMode(BTN, INPUT_PULLUP)

def main():
    setup()
    print("Button LED Ready")
    while True:
        digitalWrite(LED, not digitalRead(BTN))
        time.sleep(0.01)

def cleanup():
    digitalWrite(LED, 0)
    print("LED OFF — Safe Exit")

run(main, cleanup)
```

---

# 3. toggle_led.py — Toggle LED with Button

```python
from digital import pinMode, digitalWrite, digitalRead, INPUT_PULLUP, OUTPUT
from systemio import run
import time

LED   = 2
BTN   = 4
state = False

def setup():
    pinMode(LED, OUTPUT)
    pinMode(BTN, INPUT_PULLUP)

def main():
    global state
    setup()
    last_btn = 1
    print("Toggle LED Ready")
    while True:
        btn = digitalRead(BTN)
        if last_btn == 1 and btn == 0:
            state = not state
            digitalWrite(LED, state)
            print("LED:", "ON" if state else "OFF")
        last_btn = btn
        time.sleep(0.05)

def cleanup():
    digitalWrite(LED, 0)
    print("LED OFF — Safe Exit")

run(main, cleanup)
```

---

# 4. traffic_light.py — Traffic Light System

```python
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
import time

RED    = 2
YELLOW = 4
GREEN  = 5

LIGHTS = [RED, YELLOW, GREEN]

def setup():
    for pin in LIGHTS:
        pinMode(pin, OUTPUT)
        digitalWrite(pin, 0)

def set_light(r, y, g):
    digitalWrite(RED,    r)
    digitalWrite(YELLOW, y)
    digitalWrite(GREEN,  g)

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
    print("All Lights OFF — Safe Exit")

run(main, cleanup)
```

---

# 5. led_chaser.py — LED Chaser

```python
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
import time

LEDS = [2, 4, 5, 18]

def setup():
    for led in LEDS:
        pinMode(led, OUTPUT)
        digitalWrite(led, 0)

def main():
    setup()
    print("LED Chaser Started")
    while True:
        for led in LEDS:
            digitalWrite(led, 1)
            time.sleep(0.2)
            digitalWrite(led, 0)
        for led in reversed(LEDS):
            digitalWrite(led, 1)
            time.sleep(0.2)
            digitalWrite(led, 0)

def cleanup():
    for led in LEDS:
        digitalWrite(led, 0)
    print("All LEDs OFF — Safe Exit")

run(main, cleanup)
```

---

# 6. pwm_led.py — PWM LED Brightness

```python
from digital import pwmSetup, pwmWrite, pwmStop
from systemio import run
import time

LED = 2

def setup():
    pwmSetup(LED, freq=1000)

def main():
    setup()
    print("PWM Fade Started")
    while True:
        for i in range(0, 1024, 10):
            pwmWrite(LED, i)
            time.sleep_ms(10)
        for i in range(1023, -1, -10):
            pwmWrite(LED, i)
            time.sleep_ms(10)

def cleanup():
    pwmStop(LED)
    print("PWM Stopped — Safe Exit")

run(main, cleanup)
```

---

# 7. rgb_led.py — RGB LED Mixer

```python
from digital import pwmSetup, pwmWrite, pwmStop
from systemio import run
import time

R = 14
G = 12
B = 13

RGB_PINS = [R, G, B]

COLORS = [
    (1023, 0,    0,    "Red"    ),
    (0,    1023, 0,    "Green"  ),
    (0,    0,    1023, "Blue"   ),
    (1023, 1023, 0,    "Yellow" ),
    (0,    1023, 1023, "Cyan"   ),
    (1023, 0,    1023, "Magenta"),
    (512,  512,  512,  "White"  ),
]

def setup():
    for pin in RGB_PINS:
        pwmSetup(pin, freq=1000)

def main():
    setup()
    print("RGB LED Started")
    while True:
        for rv, gv, bv, name in COLORS:
            pwmWrite(R, rv)
            pwmWrite(G, gv)
            pwmWrite(B, bv)
            print("Color:", name)
            time.sleep(1)

def cleanup():
    for pin in RGB_PINS:
        pwmStop(pin)
    print("RGB OFF — Safe Exit")

run(main, cleanup)
```

---

# 8. counter.py — Push Button Counter

```python
from digital import pinMode, attachInterrupt, detachInterrupt, INPUT_PULLUP, FALLING
from systemio import run
import time

BTN   = 4
count = 0

def pressed(pin):
    global count
    count += 1
    print("Count:", count)

def setup():
    pinMode(BTN, INPUT_PULLUP)
    attachInterrupt(BTN, pressed, FALLING, debounce_ms=50)

def main():
    setup()
    print("Button Counter Ready — press the button")
    while True:
        time.sleep(1)
        print("Total:", count)

def cleanup():
    detachInterrupt(BTN)
    print("Interrupt Removed — Safe Exit")

run(main, cleanup)
```

---

# 9. buzzer.py — Buzzer Alarm

```python
from digital import pinMode, pulse, blink, digitalWrite, OUTPUT
from systemio import run
import time

BUZZER = 15

def setup():
    pinMode(BUZZER, OUTPUT)

def main():
    setup()
    print("Buzzer Alarm Started")
    while True:
        print("BEEP")
        pulse(BUZZER, 500)
        time.sleep(1)

def cleanup():
    digitalWrite(BUZZER, 0)
    print("Buzzer OFF — Safe Exit")

run(main, cleanup)
```

---

# 10. pir_light.py — PIR Motion Light

```python
from digital import pinMode, digitalWrite, digitalRead, INPUT, OUTPUT
from systemio import run
import time

PIR = 4
LED = 2

def setup():
    pinMode(PIR, INPUT)
    pinMode(LED, OUTPUT)

def main():
    setup()
    print("PIR Motion Light Ready")
    while True:
        motion = digitalRead(PIR)
        digitalWrite(LED, motion)
        if motion:
            print("Motion Detected — LED ON")
        time.sleep(0.1)

def cleanup():
    digitalWrite(LED, 0)
    print("LED OFF — Safe Exit")

run(main, cleanup)
```

---

# 11. smart_fan.py — Smart Fan Controller

```python
from digital import pinMode, digitalWrite, pwmSetup, pwmWritePercent, pwmStop
from digital import digitalRead, INPUT_PULLUP, OUTPUT
from systemio import run
import time

FAN_PIN  = 2
BTN_UP   = 4
BTN_DOWN = 5
STEP     = 25

def setup():
    pwmSetup(FAN_PIN, freq=1000)
    pinMode(BTN_UP,   INPUT_PULLUP)
    pinMode(BTN_DOWN, INPUT_PULLUP)

def main():
    setup()
    speed = 50
    pwmWritePercent(FAN_PIN, speed)
    print("Smart Fan — Speed:", speed, "%")

    while True:
        if digitalRead(BTN_UP) == 0:
            speed = min(100, speed + STEP)
            pwmWritePercent(FAN_PIN, speed)
            print("Fan Speed:", speed, "%")
            time.sleep(0.3)

        if digitalRead(BTN_DOWN) == 0:
            speed = max(0, speed - STEP)
            pwmWritePercent(FAN_PIN, speed)
            print("Fan Speed:", speed, "%")
            time.sleep(0.3)

        time.sleep(0.05)

def cleanup():
    pwmStop(FAN_PIN)
    print("Fan OFF — Safe Exit")

run(main, cleanup)
```

---

# 12. touch_lamp.py — Touch Sensor Lamp

```python
from digital import pinMode, digitalWrite, digitalRead, togglePin, INPUT, OUTPUT
from systemio import run
import time

TOUCH_PIN = 4
LED_PIN   = 2

def setup():
    pinMode(TOUCH_PIN, INPUT)
    pinMode(LED_PIN,   OUTPUT)

def main():
    setup()
    last_state = 0
    print("Touch Lamp Ready")
    while True:
        current = digitalRead(TOUCH_PIN)
        if last_state == 0 and current == 1:
            togglePin(LED_PIN)
            print("Lamp:", "ON" if digitalRead(LED_PIN) else "OFF")
        last_state = current
        time.sleep(0.05)

def cleanup():
    digitalWrite(LED_PIN, 0)
    print("Lamp OFF — Safe Exit")

run(main, cleanup)
```

---

# 13. door_bell.py — Door Bell

```python
from digital import pinMode, digitalWrite, digitalRead, blink, INPUT_PULLUP, OUTPUT
from systemio import run
import time

BTN_PIN    = 4
BUZZER_PIN = 2
LED_PIN    = 5

def setup():
    pinMode(BTN_PIN,    INPUT_PULLUP)
    pinMode(BUZZER_PIN, OUTPUT)
    pinMode(LED_PIN,    OUTPUT)

def main():
    setup()
    print("Door Bell Ready")
    while True:
        if digitalRead(BTN_PIN) == 0:
            print("DING DONG!")
            blink(LED_PIN,    times=2, on_ms=200, off_ms=100)
            blink(BUZZER_PIN, times=1, on_ms=300, off_ms=0)
            time.sleep(0.2)
            blink(BUZZER_PIN, times=1, on_ms=500, off_ms=0)
            time.sleep(0.5)
        time.sleep(0.05)

def cleanup():
    digitalWrite(BUZZER_PIN, 0)
    digitalWrite(LED_PIN, 0)
    print("Door Bell OFF — Safe Exit")

run(main, cleanup)
```

---

# 14. smart_dustbin.py — Smart Dustbin (Ultrasonic Simulation)

```python
from digital import pinMode, digitalWrite, digitalRead, pulse, INPUT, OUTPUT
from systemio import run
import time

TRIG_PIN = 5
ECHO_PIN = 4
LED_PIN  = 2
BUZ_PIN  = 18

def measure_distance():
    pulse(TRIG_PIN, 10)
    start = time.ticks_us()
    while digitalRead(ECHO_PIN) == 0:
        if time.ticks_diff(time.ticks_us(), start) > 30000:
            return 999
    t1 = time.ticks_us()
    while digitalRead(ECHO_PIN) == 1:
        if time.ticks_diff(time.ticks_us(), t1) > 30000:
            return 999
    t2  = time.ticks_us()
    return time.ticks_diff(t2, t1) * 0.0343 / 2

def setup():
    pinMode(TRIG_PIN, OUTPUT)
    pinMode(ECHO_PIN, INPUT)
    pinMode(LED_PIN,  OUTPUT)
    pinMode(BUZ_PIN,  OUTPUT)

def main():
    setup()
    print("Smart Dustbin Ready")
    while True:
        dist = measure_distance()
        full = dist < 10
        digitalWrite(LED_PIN, 1 if full else 0)
        if full:
            print(f"Bin FULL ({dist:.1f} cm) — Alert!")
            pulse(BUZ_PIN, 200)
        else:
            print(f"Bin OK  ({dist:.1f} cm)")
        time.sleep(1)

def cleanup():
    digitalWrite(LED_PIN, 0)
    digitalWrite(BUZ_PIN, 0)
    print("Dustbin OFF — Safe Exit")

run(main, cleanup)
```

---

# 15. dice.py — Electronic Dice

```python
from digital import pinMode, digitalWrite, blink, digitalRead, INPUT_PULLUP, OUTPUT
from systemio import run
import time, random

BTN_PIN  = 4
LED_PINS = [2, 5, 18, 19, 21, 22, 23]

FACES = {
    1: [0,0,0,1,0,0,0],
    2: [1,0,0,0,0,0,1],
    3: [1,0,0,1,0,0,1],
    4: [1,1,0,0,0,1,1],
    5: [1,1,0,1,0,1,1],
    6: [1,1,1,0,1,1,1],
}

def show(n):
    for i, pin in enumerate(LED_PINS):
        digitalWrite(pin, FACES[n][i])

def setup():
    pinMode(BTN_PIN, INPUT_PULLUP)
    for pin in LED_PINS:
        pinMode(pin, OUTPUT)
        digitalWrite(pin, 0)

def main():
    setup()
    print("Electronic Dice Ready — press button to roll")
    last_btn = 1
    while True:
        btn = digitalRead(BTN_PIN)
        if last_btn == 1 and btn == 0:
            print("Rolling...")
            for _ in range(8):
                show(random.randint(1, 6))
                time.sleep(0.1)
            result = random.randint(1, 6)
            show(result)
            print("Result:", result)
        last_btn = btn
        time.sleep(0.05)

def cleanup():
    for pin in LED_PINS:
        digitalWrite(pin, 0)
    print("Dice OFF — Safe Exit")

run(main, cleanup)
```

---

# 16. breathing_led.py — Breathing LED

```python
from digital import pwmSetup, pwmWrite, pwmStop
from systemio import run
import math, time

LED = 2

def setup():
    pwmSetup(LED, freq=1000)

def main():
    setup()
    print("Breathing LED Started")
    t = 0.0
    while True:
        brightness = int((math.sin(t) + 1) / 2 * 1023)
        pwmWrite(LED, brightness)
        t += 0.05
        time.sleep(0.02)

def cleanup():
    pwmStop(LED)
    print("LED OFF — Safe Exit")

run(main, cleanup)
```

---

# 17. laser_alarm.py — Laser Alarm

```python
from digital import pinMode, digitalWrite, digitalRead, blink, INPUT, OUTPUT
from systemio import run
import time

LASER_PIN  = 2
LDR_PIN    = 4
BUZZER_PIN = 5
LED_PIN    = 18
THRESHOLD  = 0

def setup():
    pinMode(LASER_PIN,  OUTPUT)
    pinMode(LDR_PIN,    INPUT)
    pinMode(BUZZER_PIN, OUTPUT)
    pinMode(LED_PIN,    OUTPUT)
    digitalWrite(LASER_PIN, 1)

def main():
    setup()
    print("Laser Alarm Armed")
    while True:
        beam_broken = digitalRead(LDR_PIN) == THRESHOLD
        if beam_broken:
            print("⚠ INTRUDER! Beam broken!")
            blink(LED_PIN,    times=5, on_ms=100, off_ms=50)
            blink(BUZZER_PIN, times=5, on_ms=100, off_ms=50)
        else:
            print("Beam OK")
        time.sleep(0.2)

def cleanup():
    digitalWrite(LASER_PIN,  0)
    digitalWrite(BUZZER_PIN, 0)
    digitalWrite(LED_PIN,    0)
    print("Laser Alarm OFF — Safe Exit")

run(main, cleanup)
```

---

# 18. water_tank.py — Water Tank Indicator

```python
from digital import pinMode, digitalWrite, digitalRead, blink, INPUT, OUTPUT
from systemio import run
import time

SENSOR_PINS = [2, 4, 5, 18]    # LOW=25%, MID-LOW=50%, MID-HIGH=75%, HIGH=100%
LED_PINS    = [19, 21, 22, 23]
BUZZER_PIN  = 15
FULL_PIN    = 3

def setup():
    for pin in SENSOR_PINS:
        pinMode(pin, INPUT)
    for pin in LED_PINS:
        pinMode(pin, OUTPUT)
        digitalWrite(pin, 0)
    pinMode(BUZZER_PIN, OUTPUT)

def main():
    setup()
    print("Water Tank Monitor Started")
    while True:
        level = sum(digitalRead(p) for p in SENSOR_PINS)
        pct   = level * 25

        for i, pin in enumerate(LED_PINS):
            digitalWrite(pin, 1 if i < level else 0)

        print(f"Water Level: {pct}%", "FULL!" if level == 4 else "")

        if level == 4:
            blink(BUZZER_PIN, times=2, on_ms=200, off_ms=100)

        time.sleep(1)

def cleanup():
    for pin in LED_PINS:
        digitalWrite(pin, 0)
    digitalWrite(BUZZER_PIN, 0)
    print("Tank Monitor OFF — Safe Exit")

run(main, cleanup)
```

---

# 19. smart_parking.py — Smart Parking

```python
from digital import pinMode, digitalWrite, digitalRead, blink, INPUT, OUTPUT
from systemio import run
import time

IR_PINS  = [4, 5, 18, 19]        # IR sensors for 4 slots
LED_PINS = [2, 12, 13, 14]       # Green=free, Red=occupied (same pin, logic inverted)
BUZ_PIN  = 15

def setup():
    for pin in IR_PINS:
        pinMode(pin, INPUT)
    for pin in LED_PINS:
        pinMode(pin, OUTPUT)
        digitalWrite(pin, 0)
    pinMode(BUZ_PIN, OUTPUT)

def main():
    setup()
    print("Smart Parking Ready")
    while True:
        occupied = [digitalRead(p) for p in IR_PINS]
        free     = occupied.count(0)
        full     = free == 0

        for i, pin in enumerate(LED_PINS):
            digitalWrite(pin, occupied[i])   # 1=occupied(red), 0=free(green)

        print(f"Slots: {['OCC' if o else 'FREE' for o in occupied]}  Free: {free}/4")

        if full:
            print("Parking FULL!")
            blink(BUZ_PIN, times=1, on_ms=500, off_ms=0)

        time.sleep(1)

def cleanup():
    for pin in LED_PINS:
        digitalWrite(pin, 0)
    digitalWrite(BUZ_PIN, 0)
    print("Parking System OFF — Safe Exit")

run(main, cleanup)
```

---

# 20. motor_speed.py — Motor Speed Controller

```python
from digital import pwmSetup, pwmWrite, pwmWritePercent, pwmStop
from digital import pinMode, digitalRead, INPUT_PULLUP
from systemio import run
import time

MOTOR_PIN = 2
BTN_UP    = 4
BTN_DOWN  = 5
STEP      = 10

def setup():
    pwmSetup(MOTOR_PIN, freq=1000)
    pinMode(BTN_UP,   INPUT_PULLUP)
    pinMode(BTN_DOWN, INPUT_PULLUP)

def main():
    setup()
    speed = 0
    pwmWritePercent(MOTOR_PIN, speed)
    print("Motor Controller Ready")

    while True:
        if digitalRead(BTN_UP) == 0:
            speed = min(100, speed + STEP)
            pwmWritePercent(MOTOR_PIN, speed)
            print("Motor Speed:", speed, "%")
            time.sleep(0.3)

        if digitalRead(BTN_DOWN) == 0:
            speed = max(0, speed - STEP)
            pwmWritePercent(MOTOR_PIN, speed)
            print("Motor Speed:", speed, "%")
            time.sleep(0.3)

        time.sleep(0.05)

def cleanup():
    pwmStop(MOTOR_PIN)
    print("Motor STOPPED — Safe Exit")

run(main, cleanup)
```

---

# 21. home_automation.py — Home Automation

```python
from digital import pinMode, digitalWrite, digitalRead, INPUT_PULLUP, OUTPUT
from systemio import run
import time

SWITCH_PINS   = [4, 5, 18, 19]
APPLIANCE_PINS = [2, 12, 13, 14]
NAMES = ["Light", "Fan", "TV", "AC"]

def setup():
    for pin in SWITCH_PINS:
        pinMode(pin, INPUT_PULLUP)
    for pin in APPLIANCE_PINS:
        pinMode(pin, OUTPUT)
        digitalWrite(pin, 0)

def main():
    setup()
    states   = [False] * 4
    last_btn = [1] * 4
    print("Home Automation Ready")

    while True:
        for i in range(4):
            btn = digitalRead(SWITCH_PINS[i])
            if last_btn[i] == 1 and btn == 0:
                states[i] = not states[i]
                digitalWrite(APPLIANCE_PINS[i], states[i])
                print(f"{NAMES[i]}: {'ON' if states[i] else 'OFF'}")
            last_btn[i] = btn
        time.sleep(0.05)

def cleanup():
    for pin in APPLIANCE_PINS:
        digitalWrite(pin, 0)
    print("All Appliances OFF — Safe Exit")

run(main, cleanup)
```

---

# 22. energy_saver.py — Energy Saver (Auto Light Off)

```python
from digital import pinMode, digitalWrite, digitalRead, INPUT, INPUT_PULLUP, OUTPUT
from systemio import run
import time

PIR_PIN = 4
LED_PIN = 2
TIMEOUT = 10    # seconds of no motion → light off

def setup():
    pinMode(PIR_PIN, INPUT)
    pinMode(LED_PIN, OUTPUT)

def main():
    setup()
    last_motion = time.ticks_ms()
    print("Energy Saver Active — auto off after", TIMEOUT, "s")

    while True:
        if digitalRead(PIR_PIN) == 1:
            last_motion = time.ticks_ms()
            digitalWrite(LED_PIN, 1)
            print("Motion — Light ON")

        elapsed = time.ticks_diff(time.ticks_ms(), last_motion) // 1000
        if elapsed >= TIMEOUT:
            digitalWrite(LED_PIN, 0)

        time.sleep(0.2)

def cleanup():
    digitalWrite(LED_PIN, 0)
    print("Light OFF — Safe Exit")

run(main, cleanup)
```

---

# 23. voting_machine.py — Voting Machine

```python
from digital import pinMode, digitalRead, blink, attachInterrupt, detachInterrupt
from digital import digitalWrite, INPUT_PULLUP, OUTPUT, FALLING
from systemio import run
import time

BTN_A   = 4
BTN_B   = 5
BTN_B2  = 18
LED_A   = 2
LED_B   = 12
votes_a = 0
votes_b = 0

def vote_a(pin):
    global votes_a
    votes_a += 1
    blink(LED_A, times=1, on_ms=100, off_ms=0)
    print(f"Vote A! Total A:{votes_a}  B:{votes_b}")

def vote_b(pin):
    global votes_b
    votes_b += 1
    blink(LED_B, times=1, on_ms=100, off_ms=0)
    print(f"Vote B! Total A:{votes_a}  B:{votes_b}")

def setup():
    pinMode(BTN_A, INPUT_PULLUP)
    pinMode(BTN_B, INPUT_PULLUP)
    pinMode(LED_A, OUTPUT)
    pinMode(LED_B, OUTPUT)
    attachInterrupt(BTN_A, vote_a, FALLING, debounce_ms=300)
    attachInterrupt(BTN_B, vote_b, FALLING, debounce_ms=300)

def main():
    setup()
    print("Voting Machine Ready — press A or B")
    while True:
        time.sleep(1)
        winner = "A" if votes_a > votes_b else "B" if votes_b > votes_a else "TIE"
        print(f"  Scores → A:{votes_a}  B:{votes_b}  Leading:{winner}")

def cleanup():
    detachInterrupt(BTN_A)
    detachInterrupt(BTN_B)
    print(f"\nFinal: A={votes_a}  B={votes_b} — Safe Exit")

run(main, cleanup)
```

---

# 24. school_bell.py — School Bell Timer

```python
from digital import pinMode, digitalWrite, blink, OUTPUT
from systemio import run
import time

BELL_PIN = 2
LED_PIN  = 5

# (hour, minute, duration_ms, label)
SCHEDULE = [
    (8,  0,  1000, "School Start"),
    (9,  0,  500,  "Period 2"    ),
    (10, 0,  500,  "Period 3"    ),
    (11, 0,  1000, "Break Time"  ),
    (12, 0,  500,  "Period 4"    ),
    (13, 0,  2000, "Lunch Break" ),
    (14, 0,  500,  "Period 5"    ),
    (15, 30, 3000, "School End"  ),
]

def get_time():
    t   = time.localtime()
    return t[3], t[4]   # hour, minute

def ring(duration_ms, label):
    print(f"BELL: {label}")
    blink(BELL_PIN, times=3, on_ms=duration_ms // 3, off_ms=100)
    blink(LED_PIN,  times=3, on_ms=100, off_ms=100)

def setup():
    pinMode(BELL_PIN, OUTPUT)
    pinMode(LED_PIN,  OUTPUT)

def main():
    setup()
    fired = set()
    print("School Bell System Running")

    while True:
        hh, mm = get_time()
        for entry in SCHEDULE:
            key = (entry[0], entry[1])
            if hh == entry[0] and mm == entry[1] and key not in fired:
                ring(entry[2], entry[3])
                fired.add(key)
        # Reset fired set at midnight
        if hh == 0 and mm == 0:
            fired.clear()
        time.sleep(30)

def cleanup():
    digitalWrite(BELL_PIN, 0)
    digitalWrite(LED_PIN,  0)
    print("School Bell OFF — Safe Exit")

run(main, cleanup)
```

---

# 25. rfid_door.py — RFID Door Lock (Simulated)

```python
from digital import pinMode, digitalWrite, digitalRead, blink, pulse
from digital import INPUT_PULLUP, OUTPUT
from systemio import run
import time

# Simulated with 2 buttons: BTN_AUTH = authorized card, BTN_DENY = wrong card
BTN_AUTH   = 4
BTN_DENY   = 5
RELAY_PIN  = 2     # Door lock relay
GREEN_LED  = 18
RED_LED    = 19
BUZZER_PIN = 21

OPEN_MS = 3000

def setup():
    for pin in [BTN_AUTH, BTN_DENY]:
        pinMode(pin, INPUT_PULLUP)
    for pin in [RELAY_PIN, GREEN_LED, RED_LED, BUZZER_PIN]:
        pinMode(pin, OUTPUT)
        digitalWrite(pin, 0)

def door_open():
    print("Access GRANTED — Door Open")
    digitalWrite(RELAY_PIN, 1)
    blink(GREEN_LED, times=3, on_ms=100, off_ms=100)
    pulse(BUZZER_PIN, 100)
    time.sleep(OPEN_MS / 1000)
    digitalWrite(RELAY_PIN, 0)
    print("Door Closed")

def door_deny():
    print("Access DENIED")
    blink(RED_LED,    times=3, on_ms=100, off_ms=100)
    blink(BUZZER_PIN, times=3, on_ms=50,  off_ms=100)

def main():
    setup()
    print("RFID Door Lock Ready")
    while True:
        if digitalRead(BTN_AUTH) == 0:
            door_open()
            time.sleep(0.5)
        if digitalRead(BTN_DENY) == 0:
            door_deny()
            time.sleep(0.5)
        time.sleep(0.05)

def cleanup():
    digitalWrite(RELAY_PIN, 0)
    for pin in [GREEN_LED, RED_LED, BUZZER_PIN]:
        digitalWrite(pin, 0)
    print("Door Lock OFF — Safe Exit")

run(main, cleanup)
```

---

# 26. street_light.py — Smart Street Light

```python
from digital import pinMode, digitalWrite, digitalRead, pwmSetup, pwmWritePercent, pwmStop
from digital import INPUT, OUTPUT
from systemio import run
import time

LDR_PIN  = 4
PIR_PIN  = 5
LED_PIN  = 2

DIM_PCT  = 20
FULL_PCT = 100

def setup():
    pinMode(LDR_PIN, INPUT)
    pinMode(PIR_PIN, INPUT)
    pwmSetup(LED_PIN, freq=1000)

def main():
    setup()
    print("Smart Street Light Active")
    while True:
        dark   = digitalRead(LDR_PIN) == 0    # LOW = dark
        motion = digitalRead(PIR_PIN) == 1

        if not dark:
            pwmWritePercent(LED_PIN, 0)
            status = "OFF (daylight)"
        elif motion:
            pwmWritePercent(LED_PIN, FULL_PCT)
            status = "FULL (motion)"
        else:
            pwmWritePercent(LED_PIN, DIM_PCT)
            status = "DIM (no motion)"

        print("Street Light:", status)
        time.sleep(1)

def cleanup():
    pwmStop(LED_PIN)
    print("Street Light OFF — Safe Exit")

run(main, cleanup)
```

---

# 27. fire_alarm.py — Fire Alarm System

```python
from digital import pinMode, digitalWrite, digitalRead, blink, attachInterrupt, detachInterrupt
from digital import INPUT, OUTPUT, RISING
from systemio import run
import time

FLAME_PIN  = 4
GAS_PIN    = 5
SIREN_PIN  = 2
RED_LED    = 18
GREEN_LED  = 19
alarm_flag = False

def on_flame(pin):
    global alarm_flag
    alarm_flag = True
    print("FLAME DETECTED!")

def on_gas(pin):
    global alarm_flag
    alarm_flag = True
    print("GAS DETECTED!")

def setup():
    pinMode(FLAME_PIN, INPUT)
    pinMode(GAS_PIN,   INPUT)
    pinMode(SIREN_PIN, OUTPUT)
    pinMode(RED_LED,   OUTPUT)
    pinMode(GREEN_LED, OUTPUT)
    attachInterrupt(FLAME_PIN, on_flame, RISING, debounce_ms=200)
    attachInterrupt(GAS_PIN,   on_gas,   RISING, debounce_ms=200)
    digitalWrite(GREEN_LED, 1)

def main():
    global alarm_flag
    setup()
    print("Fire Alarm System Armed")

    while True:
        if alarm_flag:
            digitalWrite(GREEN_LED, 0)
            blink(RED_LED,   times=5, on_ms=100, off_ms=100)
            blink(SIREN_PIN, times=5, on_ms=100, off_ms=100)
            alarm_flag = False
        else:
            digitalWrite(GREEN_LED, 1)
        time.sleep(0.1)

def cleanup():
    detachInterrupt(FLAME_PIN)
    detachInterrupt(GAS_PIN)
    digitalWrite(SIREN_PIN, 0)
    digitalWrite(RED_LED,   0)
    digitalWrite(GREEN_LED, 0)
    print("Fire Alarm OFF — Safe Exit")

run(main, cleanup)
```

---

# 28. smart_irrigation.py — Smart Irrigation

```python
from digital import pinMode, digitalWrite, digitalRead, blink, INPUT, OUTPUT
from systemio import run
import time

SOIL_PIN  = 4      # Digital soil sensor output
PUMP_PIN  = 2
LED_PIN   = 5
DRY_VAL   = 0      # 0 = dry for most digital soil sensors
CHECK_INT = 10     # seconds between checks

def setup():
    pinMode(SOIL_PIN, INPUT)
    pinMode(PUMP_PIN, OUTPUT)
    pinMode(LED_PIN,  OUTPUT)
    digitalWrite(PUMP_PIN, 0)

def water(seconds=3):
    print(f"Soil DRY — Pumping {seconds}s")
    blink(LED_PIN, times=3, on_ms=100, off_ms=100)
    digitalWrite(PUMP_PIN, 1)
    time.sleep(seconds)
    digitalWrite(PUMP_PIN, 0)
    print("Pump OFF")

def main():
    setup()
    print("Smart Irrigation Ready")
    while True:
        soil = digitalRead(SOIL_PIN)
        dry  = soil == DRY_VAL
        print("Soil:", "DRY" if dry else "MOIST")

        if dry:
            water(seconds=3)
        else:
            print("Moisture OK — No watering needed")

        time.sleep(CHECK_INT)

def cleanup():
    digitalWrite(PUMP_PIN, 0)
    digitalWrite(LED_PIN,  0)
    print("Irrigation OFF — Safe Exit")

run(main, cleanup)
```

---

# 29. emergency_stop.py — Emergency Stop Button

```python
from digital import pinMode, digitalWrite, digitalRead, pwmSetup, pwmWrite, pwmStop
from digital import attachInterrupt, detachInterrupt, blink, INPUT_PULLUP, OUTPUT, FALLING
from systemio import run
import time

ESTOP_PIN = 4
MOTOR_PIN = 2
SIREN_PIN = 5
LED_RED   = 18
LED_GREEN = 19
stopped   = False

def emergency_stop(pin):
    global stopped
    stopped = True
    print("⚠ EMERGENCY STOP TRIGGERED!")

def setup():
    pinMode(ESTOP_PIN, INPUT_PULLUP)
    pwmSetup(MOTOR_PIN, freq=1000)
    pinMode(SIREN_PIN, OUTPUT)
    pinMode(LED_RED,   OUTPUT)
    pinMode(LED_GREEN, OUTPUT)
    attachInterrupt(ESTOP_PIN, emergency_stop, FALLING, debounce_ms=100)
    digitalWrite(LED_GREEN, 1)

def main():
    global stopped
    setup()
    speed = 0
    print("Motor Running — press E-STOP to halt")

    while True:
        if stopped:
            pwmStop(MOTOR_PIN)
            digitalWrite(LED_GREEN, 0)
            blink(LED_RED,   times=3, on_ms=200, off_ms=100)
            blink(SIREN_PIN, times=3, on_ms=200, off_ms=100)
            print("System HALTED — reset to restart")
            while True:
                time.sleep(1)
        else:
            if speed < 800:
                speed += 50
            pwmWrite(MOTOR_PIN, speed)
            print("Motor speed:", speed)
        time.sleep(0.5)

def cleanup():
    pwmStop(MOTOR_PIN)
    for pin in [SIREN_PIN, LED_RED, LED_GREEN]:
        digitalWrite(pin, 0)
    detachInterrupt(ESTOP_PIN)
    print("Emergency Stop System OFF — Safe Exit")

run(main, cleanup)
```

---

# 30. factory_monitor.py — Factory Monitoring System

```python
from digital import (pinMode, digitalWrite, digitalRead, blink, pulse,
                     attachInterrupt, detachInterrupt,
                     INPUT, INPUT_PULLUP, OUTPUT, FALLING)
from systemio import run
import time

# Sensor pins
MACHINE_A_PIN = 4     # Running status sensor
MACHINE_B_PIN = 5
FAULT_PIN     = 18    # Fault interrupt
COUNT_PIN     = 19    # Product count interrupt

# Output pins
LED_A     = 2
LED_B     = 12
LED_FAULT = 13
SIREN_PIN = 14
BUZZER_PIN = 15

fault_active = False
product_count = 0

def on_fault(pin):
    global fault_active
    fault_active = True
    print("⚠ MACHINE FAULT DETECTED!")

def on_product(pin):
    global product_count
    product_count += 1

def setup():
    for pin in [MACHINE_A_PIN, MACHINE_B_PIN, FAULT_PIN, COUNT_PIN]:
        pinMode(pin, INPUT_PULLUP)
    for pin in [LED_A, LED_B, LED_FAULT, SIREN_PIN, BUZZER_PIN]:
        pinMode(pin, OUTPUT)
        digitalWrite(pin, 0)
    attachInterrupt(FAULT_PIN,   on_fault,   FALLING, debounce_ms=200)
    attachInterrupt(COUNT_PIN,   on_product, FALLING, debounce_ms=100)

def main():
    global fault_active
    setup()
    print("Factory Monitor Active")
    last_count = 0

    while True:
        machine_a = digitalRead(MACHINE_A_PIN) == 0   # LOW = running (active low)
        machine_b = digitalRead(MACHINE_B_PIN) == 0

        digitalWrite(LED_A, machine_a)
        digitalWrite(LED_B, machine_b)

        if product_count != last_count:
            pulse(BUZZER_PIN, 50)
            last_count = product_count

        if fault_active:
            digitalWrite(LED_FAULT, 1)
            blink(SIREN_PIN, times=3, on_ms=200, off_ms=100)
            print(f"FAULT! MachA:{'RUN' if machine_a else 'STOP'}  "
                  f"MachB:{'RUN' if machine_b else 'STOP'}  "
                  f"Products:{product_count}")
            fault_active = False
        else:
            digitalWrite(LED_FAULT, 0)
            print(f"MachA:{'RUN' if machine_a else 'STOP'}  "
                  f"MachB:{'RUN' if machine_b else 'STOP'}  "
                  f"Products:{product_count}  Status:OK")

        time.sleep(1)

def cleanup():
    detachInterrupt(FAULT_PIN)
    detachInterrupt(COUNT_PIN)
    for pin in [LED_A, LED_B, LED_FAULT, SIREN_PIN, BUZZER_PIN]:
        digitalWrite(pin, 0)
    print(f"Factory Monitor OFF — Total Products: {product_count} — Safe Exit")

run(main, cleanup)
```

---

---

# 📋 Complete Project List

| # | File Name | Project | Key Functions | Safe Cleanup |
|---|-----------|---------|---------------|:---:|
| 1 | blink.py | LED Blink | `digitalWrite` | LED OFF |
| 2 | button_led.py | Button LED Control | `digitalRead` | LED OFF |
| 3 | toggle_led.py | Toggle LED | Edge detection | LED OFF |
| 4 | traffic_light.py | Traffic Light | Multi-output timing | All LEDs OFF |
| 5 | led_chaser.py | LED Chaser | Loop array | All LEDs OFF |
| 6 | pwm_led.py | PWM Fade | `pwmSetup`, `pwmWrite` | `pwmStop` |
| 7 | rgb_led.py | RGB LED Mixer | Multi-PWM | All `pwmStop` |
| 8 | counter.py | Button Counter | `attachInterrupt` | `detachInterrupt` |
| 9 | buzzer.py | Buzzer Alarm | `pulse` | Buzzer OFF |
| 10 | pir_light.py | PIR Motion Light | `digitalRead` sensor | LED OFF |
| 11 | smart_fan.py | Smart Fan | `pwmWritePercent` | `pwmStop` |
| 12 | touch_lamp.py | Touch Lamp | `togglePin` | LED OFF |
| 13 | door_bell.py | Door Bell | `blink`, `pulse` | All OFF |
| 14 | smart_dustbin.py | Smart Dustbin | Ultrasonic `pulse` | All OFF |
| 15 | dice.py | Electronic Dice | Pattern array, `blink` | All LEDs OFF |
| 16 | breathing_led.py | Breathing LED | `math.sin`, PWM | `pwmStop` |
| 17 | laser_alarm.py | Laser Alarm | Beam detect, `blink` | Laser + Siren OFF |
| 18 | water_tank.py | Water Tank | Multi-sensor levels | All OFF |
| 19 | smart_parking.py | Smart Parking | IR array, bargraph | All OFF |
| 20 | motor_speed.py | Motor Speed | `pwmWritePercent` | `pwmStop` |
| 21 | home_automation.py | Home Automation | 4-switch, 4-relay | All relays OFF |
| 22 | energy_saver.py | Energy Saver | PIR + timeout | LED OFF |
| 23 | voting_machine.py | Voting Machine | Dual interrupt | `detachInterrupt` |
| 24 | school_bell.py | School Bell | Time schedule | Bell OFF |
| 25 | rfid_door.py | RFID Door Lock | Relay, LED, buzzer | Relay OFF |
| 26 | street_light.py | Smart Street Light | LDR + PIR + PWM | `pwmStop` |
| 27 | fire_alarm.py | Fire Alarm | Dual interrupt | Siren + LEDs OFF |
| 28 | smart_irrigation.py | Smart Irrigation | Soil sensor + relay | Pump OFF |
| 29 | emergency_stop.py | Emergency Stop | IRQ halt, siren | Motor + Siren OFF |
| 30 | factory_monitor.py | Factory Monitor | Dual IRQ + sensors | All OFF + count log |

---

## Safe Exit Pattern — How It Works

```
run(main, cleanup)
       │
       ├── Calls main()
       │       └── Runs your while True loop
       │
       ├── Ctrl+C pressed → KeyboardInterrupt caught
       │
       └── Calls cleanup()
               └── Turns off LEDs, PWM, relays, removes interrupts
                   Prints "Safe Exit" message
```

> **Rule:** Every `pwmSetup()` → must have `pwmStop()` in cleanup
> Every `attachInterrupt()` → must have `detachInterrupt()` in cleanup
> Every `digitalWrite(pin, 1)` output → must be set to `0` in cleanup
