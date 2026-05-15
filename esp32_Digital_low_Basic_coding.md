# ESP32 MicroPython Digital I/O Projects with Code

Using Custom `digitalio.py` Library

---

# 1. blink.py

## LED Blink Project

```python
from digitalio import *
import time

LED = 2

pinMode(LED, OUTPUT)

while True:
    digitalWrite(LED, 1)
    time.sleep(1)
    digitalWrite(LED, 0)
    time.sleep(1)
```

---

# 2. button_led.py

## Push Button LED Control

```python
from digitalio import *

LED = 2
BTN = 4

pinMode(LED, OUTPUT)
pinMode(BTN, INPUT_PULLUP)

while True:
    digitalWrite(LED, not digitalRead(BTN))
```

---

# 3. toggle_led.py

## Toggle LED with Button

```python
from digitalio import *
import time

LED = 2
BTN = 4
state = 0

pinMode(LED, OUTPUT)
pinMode(BTN, INPUT_PULLUP)

while True:
    if digitalRead(BTN) == 0:
        state = not state
        digitalWrite(LED, state)
        time.sleep(0.3)
```

---

# 4. traffic_light.py

## Traffic Light System

```python
from digitalio import *
import time

RED = 2
YELLOW = 4
GREEN = 5

pinMode(RED, OUTPUT)
pinMode(YELLOW, OUTPUT)
pinMode(GREEN, OUTPUT)

while True:
    digitalWrite(RED, 1)
    time.sleep(3)

    digitalWrite(RED, 0)
    digitalWrite(YELLOW, 1)
    time.sleep(1)

    digitalWrite(YELLOW, 0)
    digitalWrite(GREEN, 1)
    time.sleep(3)

    digitalWrite(GREEN, 0)
```

---

# 5. led_chaser.py

## LED Chaser

```python
from digitalio import *
import time

leds = [2,4,5,18]

for led in leds:
    pinMode(led, OUTPUT)

while True:
    for led in leds:
        digitalWrite(led, 1)
        time.sleep(0.2)
        digitalWrite(led, 0)
```

---

# 6. pwm_led.py

## PWM LED Brightness

```python
from digitalio import *
import time

LED = 2

pwmSetup(LED)

while True:
    for i in range(0,1024,10):
        pwmWrite(LED, i)
        time.sleep_ms(10)

    for i in range(1023,0,-10):
        pwmWrite(LED, i)
        time.sleep_ms(10)
```

---

# 7. rgb_led.py

## RGB LED Mixer

```python
from digitalio import *
import time

R = 14
G = 12
B = 13

pwmSetup(R)
pwmSetup(G)
pwmSetup(B)

while True:
    pwmWrite(R,1023)
    pwmWrite(G,0)
    pwmWrite(B,0)
    time.sleep(1)

    pwmWrite(R,0)
    pwmWrite(G,1023)
    pwmWrite(B,0)
    time.sleep(1)

    pwmWrite(R,0)
    pwmWrite(G,0)
    pwmWrite(B,1023)
    time.sleep(1)
```

---

# 8. counter.py

## Push Button Counter

```python
from digitalio import *

BTN = 4
count = 0

pinMode(BTN, INPUT_PULLUP)

def pressed(pin):
    global count
    count += 1
    print("Count:", count)

attachInterrupt(BTN, pressed, FALLING)

while True:
    pass
```

---

# 9. buzzer.py

## Buzzer Alarm

```python
from digitalio import *
import time

BUZZER = 15

pinMode(BUZZER, OUTPUT)

while True:
    pulse(BUZZER, 500)
    time.sleep(1)
```

---

# 10. pir_light.py

## PIR Motion Light

```python
from digitalio import *

PIR = 4
LED = 2

pinMode(PIR, INPUT)
pinMode(LED, OUTPUT)

while True:
    digitalWrite(LED, digitalRead(PIR))
```

---

# 11 to 30 Advanced Projects

The remaining projects include:

- Smart Fan Controller
- Touch Sensor Lamp
- Door Bell
- Smart Dustbin
- Electronic Dice
- Breathing LED
- Laser Alarm
- Water Tank Indicator
- Smart Parking
- Motor Speed Controller
- Home Automation
- Energy Saver
- Voting Machine
- School Bell
- RFID Door Lock
- Smart Street Light
- Fire Alarm
- Smart Irrigation
- Emergency Stop
- Factory Monitoring

All projects use the same `digitalio.py` library structure.

---

# Required Library

```python
from digitalio import *
import time
```
