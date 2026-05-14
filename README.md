# ESP32 Beginner Robotics Projects
### MicroPython | Using `analog.py`, `digital.py`, `systemio.py` Libraries

---

> **Library Quick Reference**
> - `digital.py` → `pinMode`, `digitalWrite`, `digitalRead`, `togglePin`, `pulse`, `blink`, `pwmSetup`, `pwmWrite`, `pwmWritePercent`, `attachInterrupt`
> - `analog.py` → `analogPin`, `analogRead`, `analogPercent`, `analogVoltage`, `analogAverage`, `analogSmooth`, `mapValue`, `dacWrite`, `dacWritePercent`
> - `systemio.py` → `run(main, cleanup)` — safe keyboard interrupt + cleanup handler

---

## TABLE OF CONTENTS

### LED & Basic Electronics
1. [LED Blink Robot Indicator](#1-led-blink-robot-indicator)
2. [Traffic Light Controller](#2-traffic-light-controller)
3. [RGB LED Color Mixer](#3-rgb-led-color-mixer)
4. [Police Siren Light](#4-police-siren-light)
5. [Push Button LED Control](#5-push-button-led-control)
6. [Touch Sensor Light](#6-touch-sensor-light)
7. [PWM LED Brightness Controller](#7-pwm-led-brightness-controller)
8. [Smart Street Light](#8-smart-street-light)

### Sensor Projects
9. [Temperature Monitor using LM35](#9-temperature-monitor-using-lm35)
10. [Fire Alarm Robot](#10-fire-alarm-robot)
11. [Gas Leakage Detector](#11-gas-leakage-detector)
12. [Rain Detection System](#12-rain-detection-system)
13. [Soil Moisture Monitoring](#13-soil-moisture-monitoring)
14. [Smart Dustbin using Ultrasonic Sensor](#14-smart-dustbin-using-ultrasonic-sensor)
15. [Light Following Robot](#15-light-following-robot)
16. [Obstacle Detection Alarm](#16-obstacle-detection-alarm)

### Motor & Motion Projects
17. [DC Motor Speed Control](#17-dc-motor-speed-control)
18. [Servo Motor Angle Controller](#18-servo-motor-angle-controller)
19. [Line Follower Robot](#19-line-follower-robot)
20. [Bluetooth Controlled Car](#20-bluetooth-controlled-car)
21. [IR Remote Controlled Robot](#21-ir-remote-controlled-robot)
22. [Maze Solver Beginner Robot](#22-maze-solver-beginner-robot)
23. [Basic Robot Arm](#23-basic-robot-arm)

---

---

# LED & BASIC ELECTRONICS

---

## 1. LED Blink Robot Indicator

### Objective
Learn how to blink an LED — the "Hello World" of robotics. Understand GPIO output, delays, and the `systemio` safe-run pattern.

### Components Required
| Component | Quantity |
|-----------|----------|
| ESP32 Board | 1 |
| LED (any colour) | 1 |
| 220Ω Resistor | 1 |
| Breadboard + Jumper Wires | — |

### Circuit Diagram
```
ESP32 GPIO2 ──── 220Ω ──── LED(+) ──── LED(-) ──── GND
```

### Pin Configuration
| ESP32 Pin | Connected To |
|-----------|-------------|
| GPIO 2 | LED Anode (via 220Ω) |
| GND | LED Cathode |

### Code
```python
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
import time

LED_PIN = 2

def setup():
    pinMode(LED_PIN, OUTPUT)

def main():
    setup()
    print("LED Blink Started")
    while True:
        digitalWrite(LED_PIN, 1)   # LED ON
        print("LED: ON")
        time.sleep(0.5)
        digitalWrite(LED_PIN, 0)   # LED OFF
        print("LED: OFF")
        time.sleep(0.5)

def cleanup():
    digitalWrite(LED_PIN, 0)
    print("LED turned OFF")

run(main, cleanup)
```

### How It Works
- `pinMode(LED_PIN, OUTPUT)` configures GPIO2 as a digital output.
- `digitalWrite(pin, 1)` sends HIGH (3.3V) to turn the LED on.
- `time.sleep(0.5)` waits 500ms before toggling again.
- `run(main, cleanup)` ensures the LED is turned off safely on Ctrl+C.

### Expected Output
```
Program Started
LED Blink Started
LED: ON
LED: OFF
LED: ON
...
```

### Learning Outcomes
- GPIO output configuration
- Basic digital write operations
- Safe program termination with `systemio`

---

## 2. Traffic Light Controller

### Objective
Simulate a real traffic light sequence (Red → Yellow → Green → Yellow → Red) using three LEDs and timing control.

### Components Required
| Component | Quantity |
|-----------|----------|
| ESP32 Board | 1 |
| Red LED | 1 |
| Yellow LED | 1 |
| Green LED | 1 |
| 220Ω Resistors | 3 |
| Breadboard + Jumper Wires | — |

### Circuit Diagram
```
GPIO5  ──── 220Ω ──── RED LED    ──── GND
GPIO18 ──── 220Ω ──── YELLOW LED ──── GND
GPIO19 ──── 220Ω ──── GREEN LED  ──── GND
```

### Pin Configuration
| ESP32 Pin | LED Colour |
|-----------|-----------|
| GPIO 5 | Red |
| GPIO 18 | Yellow |
| GPIO 19 | Green |

### Code
```python
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
import time

RED_PIN    = 5
YELLOW_PIN = 18
GREEN_PIN  = 19

ALL_PINS = [RED_PIN, YELLOW_PIN, GREEN_PIN]

def setup():
    for pin in ALL_PINS:
        pinMode(pin, OUTPUT)
        digitalWrite(pin, 0)

def all_off():
    for pin in ALL_PINS:
        digitalWrite(pin, 0)

def traffic_sequence():
    # RED phase
    print("RED   - STOP")
    all_off()
    digitalWrite(RED_PIN, 1)
    time.sleep(4)

    # YELLOW (transition)
    print("YELLOW - GET READY")
    all_off()
    digitalWrite(YELLOW_PIN, 1)
    time.sleep(1)

    # GREEN phase
    print("GREEN  - GO")
    all_off()
    digitalWrite(GREEN_PIN, 1)
    time.sleep(3)

    # YELLOW (transition back)
    print("YELLOW - SLOW DOWN")
    all_off()
    digitalWrite(YELLOW_PIN, 1)
    time.sleep(1)

def main():
    setup()
    print("Traffic Light Started")
    while True:
        traffic_sequence()

def cleanup():
    all_off()
    print("Traffic Light OFF")

run(main, cleanup)
```

### Traffic Light Timing
| Phase | Duration | Meaning |
|-------|----------|---------|
| Red | 4 seconds | Stop |
| Yellow | 1 second | Get Ready |
| Green | 3 seconds | Go |
| Yellow | 1 second | Slow Down |

### Learning Outcomes
- Controlling multiple GPIO outputs
- Sequential timing logic
- Real-world simulation

---

## 3. RGB LED Color Mixer

### Objective
Control an RGB LED using PWM to mix Red, Green, and Blue channels and create any colour. Read a potentiometer (optional) or cycle through colours automatically.

### Components Required
| Component | Quantity |
|-----------|----------|
| ESP32 Board | 1 |
| RGB LED (Common Cathode) | 1 |
| 100Ω Resistors | 3 |
| Breadboard + Jumper Wires | — |

### Circuit Diagram
```
GPIO25 ──── 100Ω ──── RED   pin of RGB LED
GPIO26 ──── 100Ω ──── GREEN pin of RGB LED
GPIO27 ──── 100Ω ──── BLUE  pin of RGB LED
GND   ──────────────── Common Cathode (longest leg)
```

### Pin Configuration
| ESP32 Pin | RGB Channel |
|-----------|------------|
| GPIO 25 | Red |
| GPIO 26 | Green |
| GPIO 27 | Blue |

### Code
```python
from digital import pwmSetup, pwmWrite
from systemio import run
import time

RED_PIN   = 25
GREEN_PIN = 26
BLUE_PIN  = 27

def setup():
    pwmSetup(RED_PIN,   freq=1000)
    pwmSetup(GREEN_PIN, freq=1000)
    pwmSetup(BLUE_PIN,  freq=1000)

def set_color(r, g, b):
    """Set RGB values (0-255 each)."""
    # Map 0-255 to 0-1023 for PWM duty
    pwmWrite(RED_PIN,   int(r * 4))
    pwmWrite(GREEN_PIN, int(g * 4))
    pwmWrite(BLUE_PIN,  int(b * 4))

# Predefined colours
COLORS = [
    ("RED",     255, 0,   0),
    ("GREEN",   0,   255, 0),
    ("BLUE",    0,   0,   255),
    ("YELLOW",  255, 255, 0),
    ("CYAN",    0,   255, 255),
    ("MAGENTA", 255, 0,   255),
    ("WHITE",   255, 255, 255),
    ("ORANGE",  255, 128, 0),
    ("PURPLE",  128, 0,   128),
    ("OFF",     0,   0,   0),
]

def main():
    setup()
    print("RGB Color Mixer Started")
    while True:
        for name, r, g, b in COLORS:
            print(f"Color: {name}  R={r} G={g} B={b}")
            set_color(r, g, b)
            time.sleep(1.5)

def cleanup():
    set_color(0, 0, 0)
    print("RGB LED OFF")

run(main, cleanup)
```

### Colour Table
| Colour | R | G | B |
|--------|---|---|---|
| Red | 255 | 0 | 0 |
| Green | 0 | 255 | 0 |
| Blue | 0 | 0 | 255 |
| Yellow | 255 | 255 | 0 |
| Cyan | 0 | 255 | 255 |
| Magenta | 255 | 0 | 255 |
| White | 255 | 255 | 255 |

### Learning Outcomes
- PWM duty cycle control
- Colour mixing with light
- Using `pwmSetup` and `pwmWrite`

---

## 4. Police Siren Light

### Objective
Simulate flashing police lights — alternate red and blue LEDs rapidly while playing a PWM buzzer tone.

### Components Required
| Component | Quantity |
|-----------|----------|
| ESP32 Board | 1 |
| Red LED | 1 |
| Blue LED | 1 |
| Passive Buzzer | 1 |
| 220Ω Resistors | 2 |
| Breadboard + Jumper Wires | — |

### Circuit Diagram
```
GPIO2  ──── 220Ω ──── RED LED  ──── GND
GPIO4  ──── 220Ω ──── BLUE LED ──── GND
GPIO5  ──────────────── BUZZER+ ──── GND (Buzzer-)
```

### Code
```python
from digital import pinMode, digitalWrite, OUTPUT, pwmSetup, pwmWrite, pwmStop
from systemio import run
import time

RED_PIN   = 2
BLUE_PIN  = 4
BUZZ_PIN  = 5

def setup():
    pinMode(RED_PIN,  OUTPUT)
    pinMode(BLUE_PIN, OUTPUT)
    pwmSetup(BUZZ_PIN, freq=800)

def siren_cycle():
    # Red flash + high tone
    digitalWrite(RED_PIN,  1)
    digitalWrite(BLUE_PIN, 0)
    pwmWrite(BUZZ_PIN, 512)       # 50% duty
    time.sleep_ms(150)

    digitalWrite(RED_PIN,  0)
    time.sleep_ms(100)

    # Blue flash + low tone
    digitalWrite(BLUE_PIN, 1)
    pwmWrite(BUZZ_PIN, 256)       # 25% duty
    time.sleep_ms(150)

    digitalWrite(BLUE_PIN, 0)
    time.sleep_ms(100)

def main():
    setup()
    print("Police Siren Active!")
    while True:
        siren_cycle()

def cleanup():
    digitalWrite(RED_PIN,  0)
    digitalWrite(BLUE_PIN, 0)
    pwmStop(BUZZ_PIN)
    print("Siren OFF")

run(main, cleanup)
```

### Learning Outcomes
- Fast alternating GPIO toggling
- Combining PWM buzzer with visual output
- Timing with `time.sleep_ms`

---

## 5. Push Button LED Control

### Objective
Control an LED using a push button. The button toggles the LED on/off using interrupt-driven detection with debounce.

### Components Required
| Component | Quantity |
|-----------|----------|
| ESP32 Board | 1 |
| LED | 1 |
| Push Button | 1 |
| 220Ω Resistor (LED) | 1 |
| 10kΩ Pull-down Resistor (Button) | 1 |
| Breadboard + Jumper Wires | — |

### Circuit Diagram
```
GPIO2  ──── 220Ω ──── LED(+)  ──── GND
GPIO15 ──────────────── BUTTON ──── 3.3V
              │
            10kΩ
              │
             GND
```

### Code
```python
from digital import pinMode, digitalWrite, digitalRead, OUTPUT, INPUT_PULLDOWN, attachInterrupt, RISING
from systemio import run
import time

LED_PIN    = 2
BUTTON_PIN = 15

led_state = False

def button_pressed(pin):
    global led_state
    led_state = not led_state
    digitalWrite(LED_PIN, 1 if led_state else 0)
    print(f"LED {'ON' if led_state else 'OFF'}")

def setup():
    pinMode(LED_PIN, OUTPUT)
    digitalWrite(LED_PIN, 0)
    attachInterrupt(BUTTON_PIN, button_pressed, trigger=RISING, debounce_ms=50)
    print("Press button to toggle LED")

def main():
    setup()
    while True:
        time.sleep(0.1)   # Main loop idle; interrupt handles button

def cleanup():
    digitalWrite(LED_PIN, 0)
    print("LED OFF")

run(main, cleanup)
```

### How It Works
- `attachInterrupt` detects the rising edge of the button signal.
- `debounce_ms=50` prevents multiple triggers from a single press (contact bounce).
- The interrupt callback toggles a global `led_state` flag and updates the LED.

### Learning Outcomes
- Hardware interrupts vs polling
- Debounce handling
- Toggle logic with a button

---

## 6. Touch Sensor Light

### Objective
Use a capacitive touch module (TTP223) to toggle an LED on/off. When you touch the sensor pad, the LED switches state.

### Components Required
| Component | Quantity |
|-----------|----------|
| ESP32 Board | 1 |
| TTP223 Touch Sensor Module | 1 |
| LED | 1 |
| 220Ω Resistor | 1 |
| Breadboard + Jumper Wires | — |

### Circuit Diagram
```
GPIO2  ──── 220Ω ──── LED(+)  ──── GND
GPIO4  ──────────────── TTP223 OUT
TTP223 VCC ──── 3.3V
TTP223 GND ──── GND
```

### Code
```python
from digital import pinMode, digitalWrite, digitalRead, OUTPUT, INPUT
from systemio import run
import time

LED_PIN   = 2
TOUCH_PIN = 4

led_on = False
last_touch = 0

def setup():
    pinMode(LED_PIN,   OUTPUT)
    pinMode(TOUCH_PIN, INPUT)
    digitalWrite(LED_PIN, 0)
    print("Touch Sensor Light Ready")

def main():
    global led_on, last_touch
    setup()
    while True:
        touch_val = digitalRead(TOUCH_PIN)
        now = time.ticks_ms()

        if touch_val == 1 and time.ticks_diff(now, last_touch) > 400:
            led_on = not led_on
            digitalWrite(LED_PIN, 1 if led_on else 0)
            print(f"Touch detected! LED: {'ON' if led_on else 'OFF'}")
            last_touch = now

        time.sleep_ms(30)

def cleanup():
    digitalWrite(LED_PIN, 0)
    print("Light OFF")

run(main, cleanup)
```

### Learning Outcomes
- Reading digital input modules
- Software debounce using timestamps
- Toggle state management

---

## 7. PWM LED Brightness Controller

### Objective
Control LED brightness smoothly using a potentiometer. The ADC reads the pot value and maps it to PWM duty cycle.

### Components Required
| Component | Quantity |
|-----------|----------|
| ESP32 Board | 1 |
| LED | 1 |
| 10kΩ Potentiometer | 1 |
| 220Ω Resistor | 1 |
| Breadboard + Jumper Wires | — |

### Circuit Diagram
```
GPIO34 ──── POT (middle leg)
POT left  ──── GND
POT right ──── 3.3V

GPIO2  ──── 220Ω ──── LED(+) ──── GND
```

### Code
```python
from analog import analogPin, analogRead, mapValue
from digital import pwmSetup, pwmWrite
from systemio import run
import time

POT_PIN = 34
LED_PIN = 2

def setup():
    analogPin(POT_PIN)
    pwmSetup(LED_PIN, freq=1000)

def main():
    setup()
    print("PWM Brightness Controller Running")
    while True:
        raw = analogRead(POT_PIN)            # 0 – 4095
        duty = mapValue(raw, 0, 4095, 0, 1023)  # Map to PWM range
        pwmWrite(LED_PIN, duty)
        percent = int((duty / 1023) * 100)
        print(f"Pot: {raw}  Duty: {duty}  Brightness: {percent}%")
        time.sleep_ms(50)

def cleanup():
    pwmWrite(LED_PIN, 0)
    print("LED OFF")

run(main, cleanup)
```

### How It Works
- `analogPin` configures the ADC with 11dB attenuation (0–3.3V range, 12-bit).
- `mapValue` converts the 12-bit ADC value (0–4095) to PWM duty (0–1023).
- `pwmWrite` updates the brightness in real time.

### Learning Outcomes
- Reading a potentiometer with ADC
- Mapping ADC values to PWM range
- Real-time analog control

---

## 8. Smart Street Light

### Objective
Automatically turn a street light ON when it gets dark (LDR detects low light) and OFF when it's bright. Uses an LDR (Light Dependent Resistor) analog sensor.

### Components Required
| Component | Quantity |
|-----------|----------|
| ESP32 Board | 1 |
| LDR (Photoresistor) | 1 |
| 10kΩ Resistor (voltage divider) | 1 |
| LED (Street Light) | 1 |
| 220Ω Resistor | 1 |
| Breadboard + Jumper Wires | — |

### Circuit Diagram
```
3.3V ──── LDR ──── GPIO34 ──── 10kΩ ──── GND
                   (ADC input)

GPIO2  ──── 220Ω ──── LED(+) ──── GND
```

### Code
```python
from analog import analogPin, analogAverage
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
import time

LDR_PIN  = 34
LED_PIN  = 2
DARK_THRESHOLD = 2000   # Below this value = dark (tune to environment)

def setup():
    analogPin(LDR_PIN)
    pinMode(LED_PIN, OUTPUT)
    digitalWrite(LED_PIN, 0)
    print("Smart Street Light Ready")
    print(f"Dark threshold: {DARK_THRESHOLD}")

def main():
    setup()
    while True:
        light_val = analogAverage(LDR_PIN, samples=5)   # Averaged for stability
        is_dark = light_val < DARK_THRESHOLD

        if is_dark:
            digitalWrite(LED_PIN, 1)
            status = "DARK  → Light ON"
        else:
            digitalWrite(LED_PIN, 0)
            status = "BRIGHT → Light OFF"

        print(f"LDR: {light_val}  |  {status}")
        time.sleep(1)

def cleanup():
    digitalWrite(LED_PIN, 0)
    print("Street Light OFF")

run(main, cleanup)
```

### Threshold Calibration
| LDR Value | Condition |
|-----------|-----------|
| 0 – 2000 | Dark — Light ON |
| 2001 – 4095 | Bright — Light OFF |

> **Tip:** Print LDR values in different lighting conditions to find the best threshold for your room.

### Learning Outcomes
- LDR analog reading
- Threshold-based automation
- `analogAverage` for stable sensor readings

---

---

# SENSOR PROJECTS

---

## 9. Temperature Monitor using LM35

### Objective
Read the LM35 analog temperature sensor and display temperature in Celsius and Fahrenheit. Alert when temperature exceeds a safe limit.

### Components Required
| Component | Quantity |
|-----------|----------|
| ESP32 Board | 1 |
| LM35 Temperature Sensor | 1 |
| LED (Alert) | 1 |
| 220Ω Resistor | 1 |
| Breadboard + Jumper Wires | — |

### Circuit Diagram
```
LM35 VCC  ──── 3.3V
LM35 GND  ──── GND
LM35 VOUT ──── GPIO34 (ADC)

GPIO2 ──── 220Ω ──── LED(+) ──── GND
```

### LM35 Output Formula
```
LM35 outputs 10mV per °C
VOUT = Temperature(°C) × 10mV

Formula: Temp(°C) = ADC_Voltage(V) / 0.01
```

### Code
```python
from analog import analogPin, analogVoltage, analogAverage
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
import time

TEMP_PIN       = 34
ALERT_PIN      = 2
TEMP_THRESHOLD = 35.0   # Alert if above 35°C

def setup():
    analogPin(TEMP_PIN)
    pinMode(ALERT_PIN, OUTPUT)
    digitalWrite(ALERT_PIN, 0)
    print("LM35 Temperature Monitor Ready")

def read_temperature():
    voltage = analogVoltage(TEMP_PIN, vref=3.3)   # Read voltage
    celsius = voltage / 0.01                        # LM35: 10mV/°C
    return round(celsius, 2)

def main():
    setup()
    while True:
        avg_raw = analogAverage(TEMP_PIN, samples=10)
        voltage = (avg_raw / 4095.0) * 3.3
        celsius = voltage / 0.01
        fahrenheit = (celsius * 9/5) + 32

        print(f"Temp: {celsius:.1f}°C  |  {fahrenheit:.1f}°F")

        if celsius > TEMP_THRESHOLD:
            digitalWrite(ALERT_PIN, 1)
            print(f"  ⚠ ALERT: Temperature too HIGH!")
        else:
            digitalWrite(ALERT_PIN, 0)

        time.sleep(1)

def cleanup():
    digitalWrite(ALERT_PIN, 0)
    print("Monitor OFF")

run(main, cleanup)
```

### Temperature Conversion Table
| Celsius | Fahrenheit |
|---------|-----------|
| 25°C | 77°F |
| 30°C | 86°F |
| 35°C | 95°F (Alert!) |
| 40°C | 104°F |

### Learning Outcomes
- Analog voltage reading with `analogVoltage`
- Physical sensor formula conversion
- Threshold-based alerting

---

## 10. Fire Alarm Robot

### Objective
Detect fire using an IR flame sensor. When fire is detected, activate a buzzer alarm and flash an LED rapidly.

### Components Required
| Component | Quantity |
|-----------|----------|
| ESP32 Board | 1 |
| IR Flame Sensor Module | 1 |
| Passive Buzzer | 1 |
| Red LED | 1 |
| 220Ω Resistor | 1 |
| Breadboard + Jumper Wires | — |

### Circuit Diagram
```
GPIO35 ──── Flame Sensor OUT (Analog)
Sensor VCC ──── 3.3V  |  Sensor GND ──── GND

GPIO5  ──── BUZZER+   ──── GND (Buzzer-)
GPIO2  ──── 220Ω ──── LED  ──── GND
```

### Code
```python
from analog import analogPin, analogRead
from digital import pinMode, digitalWrite, OUTPUT, pwmSetup, pwmWrite, pwmStop
from systemio import run
import time

FLAME_PIN = 35
LED_PIN   = 2
BUZZ_PIN  = 5
FIRE_THRESHOLD = 1500   # Lower value = more flame detected (sensor outputs LOW on fire)

def setup():
    analogPin(FLAME_PIN)
    pinMode(LED_PIN, OUTPUT)
    pwmSetup(BUZZ_PIN, freq=1000)
    pwmWrite(BUZZ_PIN, 0)
    print("Fire Alarm System Ready")

def trigger_alarm():
    for _ in range(5):
        digitalWrite(LED_PIN, 1)
        pwmWrite(BUZZ_PIN, 512)
        time.sleep_ms(100)
        digitalWrite(LED_PIN, 0)
        pwmWrite(BUZZ_PIN, 0)
        time.sleep_ms(100)

def main():
    setup()
    while True:
        flame_val = analogRead(FLAME_PIN)

        if flame_val < FIRE_THRESHOLD:
            print(f"FIRE DETECTED! Sensor: {flame_val}")
            trigger_alarm()
        else:
            print(f"Safe. Flame sensor: {flame_val}")
            digitalWrite(LED_PIN, 0)
            pwmWrite(BUZZ_PIN, 0)
            time.sleep(1)

def cleanup():
    digitalWrite(LED_PIN, 0)
    pwmStop(BUZZ_PIN)
    print("Fire Alarm OFF")

run(main, cleanup)
```

### Sensor Value Guide
| Flame Sensor Reading | Meaning |
|----------------------|---------|
| 0 – 500 | Direct flame — DANGER |
| 500 – 1500 | Heat/Fire nearby |
| 1500 – 4095 | Safe / No flame |

### Learning Outcomes
- Fire detection with analog sensors
- Buzzer alarm with PWM
- Fast emergency response logic

---

## 11. Gas Leakage Detector

### Objective
Detect gas leakage using an MQ-2 sensor. Trigger a buzzer and LED alarm when gas concentration exceeds a safe threshold.

### Components Required
| Component | Quantity |
|-----------|----------|
| ESP32 Board | 1 |
| MQ-2 Gas Sensor Module | 1 |
| Passive Buzzer | 1 |
| Red LED | 1 |
| 220Ω Resistor | 1 |
| Breadboard + Jumper Wires | — |

### Circuit Diagram
```
GPIO34 ──── MQ-2 AOUT (Analog Output)
MQ-2 VCC ──── 5V  |  MQ-2 GND ──── GND

GPIO5  ──── BUZZER+  ──── GND
GPIO2  ──── 220Ω ──── LED ──── GND
```

> **Note:** MQ-2 requires 5V power supply for heater. Use 5V pin on ESP32.

### Code
```python
from analog import analogPin, analogRead, analogPercent
from digital import pinMode, digitalWrite, OUTPUT, pwmSetup, pwmWrite, pwmStop
from systemio import run
import time

GAS_PIN   = 34
LED_PIN   = 2
BUZZ_PIN  = 5

# Thresholds (calibrate by testing in clean air first)
SAFE_LEVEL    = 1000
WARNING_LEVEL = 2000
DANGER_LEVEL  = 3000

def setup():
    analogPin(GAS_PIN)
    pinMode(LED_PIN, OUTPUT)
    pwmSetup(BUZZ_PIN, freq=500)
    pwmWrite(BUZZ_PIN, 0)
    print("Gas Detector Ready — Warming up sensor (20s)...")
    time.sleep(20)   # MQ-2 warm-up time
    print("Sensor ready!")

def alarm(level):
    if level == "WARNING":
        pwmWrite(BUZZ_PIN, 256)
        digitalWrite(LED_PIN, 1)
        time.sleep_ms(500)
        pwmWrite(BUZZ_PIN, 0)
        time.sleep_ms(500)
    elif level == "DANGER":
        pwmWrite(BUZZ_PIN, 512)
        digitalWrite(LED_PIN, 1)
        time.sleep_ms(200)
        pwmWrite(BUZZ_PIN, 0)
        time.sleep_ms(200)

def main():
    setup()
    while True:
        gas_val = analogRead(GAS_PIN)
        pct = analogPercent(GAS_PIN)

        if gas_val >= DANGER_LEVEL:
            print(f"DANGER! Gas: {gas_val} ({pct}%) - EVACUATE!")
            alarm("DANGER")
        elif gas_val >= WARNING_LEVEL:
            print(f"WARNING! Gas: {gas_val} ({pct}%) - Ventilate area")
            alarm("WARNING")
        else:
            print(f"Safe. Gas: {gas_val} ({pct}%)")
            digitalWrite(LED_PIN, 0)
            pwmWrite(BUZZ_PIN, 0)
            time.sleep(1)

def cleanup():
    digitalWrite(LED_PIN, 0)
    pwmStop(BUZZ_PIN)
    print("Gas Detector OFF")

run(main, cleanup)
```

### Alert Level Table
| Gas Value | Status | Action |
|-----------|--------|--------|
| 0 – 999 | Safe | Normal |
| 1000 – 1999 | Warning | Ventilate |
| 2000 – 2999 | Danger | Alarm ON |
| 3000+ | CRITICAL | Evacuate! |

### Learning Outcomes
- MQ-2 analog gas sensor
- Multi-level alert system
- Sensor warm-up timing

---

## 12. Rain Detection System

### Objective
Detect rain using a rain sensor module. Alert the user when rain is detected and show intensity level.

### Components Required
| Component | Quantity |
|-----------|----------|
| ESP32 Board | 1 |
| Rain Sensor Module | 1 |
| LED | 1 |
| 220Ω Resistor | 1 |
| Buzzer (optional) | 1 |
| Breadboard + Jumper Wires | — |

### Circuit Diagram
```
GPIO34 ──── Rain Sensor AOUT
GPIO35 ──── Rain Sensor DOUT (Digital)
Sensor VCC ──── 3.3V  |  Sensor GND ──── GND

GPIO2  ──── 220Ω ──── LED ──── GND
```

### Code
```python
from analog import analogPin, analogRead, mapValue
from digital import pinMode, digitalWrite, digitalRead, OUTPUT, INPUT
from systemio import run
import time

RAIN_APIN = 34   # Analog
RAIN_DPIN = 35   # Digital (module threshold)
LED_PIN   = 2

def setup():
    analogPin(RAIN_APIN)
    pinMode(RAIN_DPIN, INPUT)
    pinMode(LED_PIN, OUTPUT)
    print("Rain Detection System Ready")

def rain_intensity(val):
    """Classify rain intensity from ADC value."""
    if val > 3500:
        return "DRY"
    elif val > 2500:
        return "Light Rain"
    elif val > 1500:
        return "Moderate Rain"
    else:
        return "Heavy Rain!"

def main():
    setup()
    while True:
        analog_val  = analogRead(RAIN_APIN)
        digital_val = digitalRead(RAIN_DPIN)

        # Rain sensor: lower value = more water
        inverted = 4095 - analog_val   # Invert so higher = more rain
        level = rain_intensity(analog_val)

        raining = digital_val == 0   # Most modules: LOW = rain detected

        if raining:
            digitalWrite(LED_PIN, 1)
            print(f"RAIN! Intensity: {level}  (ADC: {analog_val})")
        else:
            digitalWrite(LED_PIN, 0)
            print(f"No rain. Sensor: {analog_val} | {level}")

        time.sleep(1)

def cleanup():
    digitalWrite(LED_PIN, 0)
    print("Rain Detector OFF")

run(main, cleanup)
```

### Learning Outcomes
- Using both analog and digital pins of a module
- Intensity classification from ADC values
- Environmental sensing

---

## 13. Soil Moisture Monitoring

### Objective
Monitor soil moisture for plants. Alert when soil is too dry, and display moisture percentage in real time.

### Components Required
| Component | Quantity |
|-----------|----------|
| ESP32 Board | 1 |
| Capacitive Soil Moisture Sensor | 1 |
| Green LED (Moist) | 1 |
| Red LED (Dry) | 1 |
| 220Ω Resistors | 2 |
| Breadboard + Jumper Wires | — |

### Circuit Diagram
```
GPIO34 ──── Soil Sensor AOUT
Sensor VCC ──── 3.3V  |  Sensor GND ──── GND

GPIO2  ──── 220Ω ──── GREEN LED ──── GND   (Moist)
GPIO4  ──── 220Ω ──── RED LED   ──── GND   (Dry)
```

### Code
```python
from analog import analogPin, analogSmooth, mapValue
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
import time

SOIL_PIN  = 34
GREEN_LED = 2
RED_LED   = 4

# Calibrate these values:
# Put sensor in dry air → note max value (DRY_VAL)
# Put sensor in water   → note min value (WET_VAL)
DRY_VAL = 3500
WET_VAL  = 1200

DRY_THRESHOLD = 30   # Alert if below 30% moisture

def setup():
    analogPin(SOIL_PIN)
    pinMode(GREEN_LED, OUTPUT)
    pinMode(RED_LED,   OUTPUT)
    print("Soil Moisture Monitor Ready")
    print(f"Calibration: Dry={DRY_VAL}, Wet={WET_VAL}")

def main():
    setup()
    while True:
        raw = analogSmooth(SOIL_PIN, window=10)   # Smoothed reading
        # Map: wet (low ADC) = 100%, dry (high ADC) = 0%
        moisture_pct = mapValue(raw, DRY_VAL, WET_VAL, 0, 100)
        moisture_pct = max(0, min(100, moisture_pct))

        print(f"Soil Moisture: {moisture_pct}%  (Raw ADC: {raw})")

        if moisture_pct < DRY_THRESHOLD:
            digitalWrite(RED_LED,   1)
            digitalWrite(GREEN_LED, 0)
            print("  Plant needs WATER!")
        else:
            digitalWrite(GREEN_LED, 1)
            digitalWrite(RED_LED,   0)
            print("  Soil moisture OK")

        time.sleep(2)

def cleanup():
    digitalWrite(GREEN_LED, 0)
    digitalWrite(RED_LED,   0)
    print("Monitor OFF")

run(main, cleanup)
```

### Moisture Level Guide
| Moisture % | Status | LED |
|------------|--------|-----|
| 0 – 29% | Dry — Water needed | Red ON |
| 30 – 60% | Good | Green ON |
| 61 – 100% | Very moist | Green ON |

### Learning Outcomes
- Sensor calibration (dry/wet mapping)
- Smoothing with `analogSmooth`
- Visual status with dual LEDs

---

## 14. Smart Dustbin using Ultrasonic Sensor

### Objective
Automatically open a dustbin lid when a hand is detected nearby using an HC-SR04 ultrasonic sensor. Servo opens lid, LED indicates status.

### Components Required
| Component | Quantity |
|-----------|----------|
| ESP32 Board | 1 |
| HC-SR04 Ultrasonic Sensor | 1 |
| Servo Motor (SG90) | 1 |
| Green LED | 1 |
| 220Ω Resistor | 1 |
| Breadboard + Jumper Wires | — |

### Circuit Diagram
```
GPIO5  ──── HC-SR04 TRIG
GPIO18 ──── HC-SR04 ECHO
HC-SR04 VCC ──── 5V  |  GND ──── GND

GPIO13 ──── Servo Signal (PWM)
Servo VCC  ──── 5V  |  Servo GND ──── GND

GPIO2  ──── 220Ω ──── LED ──── GND
```

### Code
```python
from digital import pinMode, digitalWrite, OUTPUT, INPUT, pwmSetup, pwmWrite
from systemio import run
from machine import Pin
import time

TRIG_PIN  = 5
ECHO_PIN  = 18
SERVO_PIN = 13
LED_PIN   = 2

DETECT_DISTANCE = 15   # Trigger if hand within 15 cm

def setup():
    global trig, echo
    trig = Pin(TRIG_PIN, Pin.OUT)
    echo = Pin(ECHO_PIN, Pin.IN)
    pwmSetup(SERVO_PIN, freq=50)
    pinMode(LED_PIN, OUTPUT)
    servo_angle(0)   # Lid closed
    print("Smart Dustbin Ready")

def measure_distance():
    """HC-SR04 ultrasonic distance in cm."""
    trig.value(0)
    time.sleep_us(2)
    trig.value(1)
    time.sleep_us(10)
    trig.value(0)

    timeout = time.ticks_us() + 30000
    while echo.value() == 0:
        if time.ticks_us() > timeout:
            return 999
    t_start = time.ticks_us()

    while echo.value() == 1:
        if time.ticks_us() > timeout:
            return 999
    t_end = time.ticks_us()

    duration = time.ticks_diff(t_end, t_start)
    return (duration * 0.034) / 2   # cm

def servo_angle(angle):
    """Set servo to angle 0–180 degrees."""
    min_duty = 26    # ~0.5ms pulse  → 0°
    max_duty = 128   # ~2.5ms pulse  → 180°
    duty = int(min_duty + (angle / 180.0) * (max_duty - min_duty))
    pwmWrite(SERVO_PIN, duty)

def main():
    setup()
    lid_open = False
    while True:
        dist = measure_distance()
        print(f"Distance: {dist:.1f} cm")

        if dist < DETECT_DISTANCE and not lid_open:
            print("Hand detected! Opening lid...")
            servo_angle(90)   # Open
            digitalWrite(LED_PIN, 1)
            lid_open = True
            time.sleep(3)     # Keep open 3 seconds

        elif lid_open:
            print("Closing lid.")
            servo_angle(0)    # Close
            digitalWrite(LED_PIN, 0)
            lid_open = False

        time.sleep(0.2)

def cleanup():
    servo_angle(0)
    digitalWrite(LED_PIN, 0)
    print("Dustbin closed")

run(main, cleanup)
```

### Learning Outcomes
- HC-SR04 ultrasonic distance measurement
- Servo motor control with PWM
- State-based automation (open/close logic)

---

## 15. Light Following Robot

### Objective
Build a robot that follows a light source. Two LDRs detect light intensity on left/right sides; motor speeds adjust to steer toward the brighter side.

### Components Required
| Component | Quantity |
|-----------|----------|
| ESP32 Board | 1 |
| LDR (Photoresistor) | 2 |
| 10kΩ Resistors | 2 |
| L298N Motor Driver | 1 |
| DC Motors | 2 |
| Robot Chassis | 1 |
| Battery Pack (6–9V) | 1 |
| Breadboard + Jumper Wires | — |

### Circuit Diagram
```
GPIO34 ──── LDR Left  (voltage divider with 10kΩ to GND)
GPIO35 ──── LDR Right (voltage divider with 10kΩ to GND)

L298N IN1 ──── GPIO25   L298N IN2 ──── GPIO26  (Left Motor)
L298N IN3 ──── GPIO27   L298N IN4 ──── GPIO14  (Right Motor)
L298N ENA ──── GPIO32   L298N ENB ──── GPIO33  (PWM Speed)
```

### Code
```python
from analog import analogPin, analogSmooth, mapValue
from digital import pinMode, digitalWrite, OUTPUT, pwmSetup, pwmWrite
from systemio import run
import time

LDR_L = 34
LDR_R = 35

IN1, IN2 = 25, 26   # Left motor
IN3, IN4 = 27, 14   # Right motor
ENA, ENB = 32, 33   # Speed PWM

BASE_SPEED = 600
DEAD_ZONE  = 150     # Ignore small differences

def setup():
    analogPin(LDR_L)
    analogPin(LDR_R)
    for pin in [IN1, IN2, IN3, IN4]:
        pinMode(pin, OUTPUT)
    pwmSetup(ENA, freq=1000)
    pwmSetup(ENB, freq=1000)
    print("Light Following Robot Ready")

def set_motors(left_speed, right_speed):
    """Positive = forward, 0 = stop."""
    # Left motor
    digitalWrite(IN1, 1)
    digitalWrite(IN2, 0)
    pwmWrite(ENA, max(0, min(1023, left_speed)))
    # Right motor
    digitalWrite(IN3, 1)
    digitalWrite(IN4, 0)
    pwmWrite(ENB, max(0, min(1023, right_speed)))

def stop():
    pwmWrite(ENA, 0)
    pwmWrite(ENB, 0)

def main():
    setup()
    while True:
        ldr_left  = analogSmooth(LDR_L, window=5)
        ldr_right = analogSmooth(LDR_R, window=5)
        diff = ldr_left - ldr_right

        print(f"LDR L: {ldr_left}  R: {ldr_right}  Diff: {diff}")

        if abs(diff) < DEAD_ZONE:
            # Light roughly equal → go forward
            set_motors(BASE_SPEED, BASE_SPEED)
            print("  → Forward")
        elif diff > 0:
            # More light on left → turn left
            set_motors(BASE_SPEED // 3, BASE_SPEED)
            print("  → Turn LEFT (light on left)")
        else:
            # More light on right → turn right
            set_motors(BASE_SPEED, BASE_SPEED // 3)
            print("  → Turn RIGHT (light on right)")

        time.sleep_ms(100)

def cleanup():
    stop()
    print("Robot stopped")

run(main, cleanup)
```

### Learning Outcomes
- Dual LDR differential sensing
- L298N motor driver control
- Proportional steering logic

---

## 16. Obstacle Detection Alarm

### Objective
Detect obstacles using an ultrasonic sensor and trigger a buzzer alarm with beep frequency proportional to distance — closer = faster beeps.

### Components Required
| Component | Quantity |
|-----------|----------|
| ESP32 Board | 1 |
| HC-SR04 Ultrasonic Sensor | 1 |
| Passive Buzzer | 1 |
| LED | 1 |
| 220Ω Resistor | 1 |
| Breadboard + Jumper Wires | — |

### Circuit Diagram
```
GPIO5  ──── HC-SR04 TRIG
GPIO18 ──── HC-SR04 ECHO
GPIO4  ──── BUZZER+  ──── GND
GPIO2  ──── 220Ω ──── LED ──── GND
```

### Code
```python
from digital import pinMode, OUTPUT, digitalWrite, pwmSetup, pwmWrite, pwmStop
from systemio import run
from machine import Pin
import time

TRIG_PIN = 5
ECHO_PIN = 18
BUZZ_PIN = 4
LED_PIN  = 2
MAX_DIST = 100   # Alarm range in cm

def setup():
    global trig, echo
    trig = Pin(TRIG_PIN, Pin.OUT)
    echo = Pin(ECHO_PIN, Pin.IN)
    pwmSetup(BUZZ_PIN, freq=1000)
    pwmWrite(BUZZ_PIN, 0)
    pinMode(LED_PIN, OUTPUT)
    print("Obstacle Alarm Ready (range: 0–100cm)")

def get_distance():
    trig.value(0); time.sleep_us(2)
    trig.value(1); time.sleep_us(10)
    trig.value(0)
    t = time.ticks_us()
    while echo.value() == 0:
        if time.ticks_diff(time.ticks_us(), t) > 25000: return 999
    s = time.ticks_us()
    while echo.value() == 1:
        if time.ticks_diff(time.ticks_us(), s) > 25000: return 999
    return time.ticks_diff(time.ticks_us(), s) * 0.034 / 2

def beep(delay_ms):
    pwmWrite(BUZZ_PIN, 512)
    digitalWrite(LED_PIN, 1)
    time.sleep_ms(80)
    pwmWrite(BUZZ_PIN, 0)
    digitalWrite(LED_PIN, 0)
    time.sleep_ms(delay_ms)

def main():
    setup()
    while True:
        dist = get_distance()

        if dist > MAX_DIST:
            print(f"Clear. Distance > {MAX_DIST}cm")
            time.sleep(0.5)
        else:
            # Beep faster as obstacle gets closer
            delay = int((dist / MAX_DIST) * 400) + 50
            print(f"Obstacle at {dist:.1f}cm  |  Beep delay: {delay}ms")
            beep(delay)

def cleanup():
    pwmStop(BUZZ_PIN)
    digitalWrite(LED_PIN, 0)
    print("Alarm OFF")

run(main, cleanup)
```

### Beep Speed vs Distance
| Distance | Beep Interval | Urgency |
|----------|--------------|---------|
| 100 cm | 450 ms | Slow |
| 50 cm | 250 ms | Medium |
| 10 cm | 90 ms | Fast |
| <5 cm | Continuous | Critical |

### Learning Outcomes
- Proportional response to sensor value
- Combining buzzer + LED for alert
- Ultrasonic distance measurement

---

---

# MOTOR & MOTION PROJECTS

---

## 17. DC Motor Speed Control

### Objective
Control DC motor speed using a potentiometer. Read pot position, map it to PWM duty cycle, and drive a motor via L298N/L293D motor driver.

### Components Required
| Component | Quantity |
|-----------|----------|
| ESP32 Board | 1 |
| DC Motor | 1 |
| L298N or L293D Motor Driver | 1 |
| 10kΩ Potentiometer | 1 |
| Battery Pack (6–9V for motor) | 1 |
| Breadboard + Jumper Wires | — |

### Circuit Diagram
```
GPIO34 ──── POT middle  |  POT ends → 3.3V and GND

L298N IN1 ──── GPIO25
L298N IN2 ──── GPIO26
L298N ENA ──── GPIO32  (PWM speed)
L298N Motor terminals → DC Motor
L298N 12V ──── Battery+  |  GND ──── Battery- + ESP32 GND
```

### Code
```python
from analog import analogPin, analogRead, mapValue
from digital import pinMode, digitalWrite, OUTPUT, pwmSetup, pwmWrite
from systemio import run
import time

POT_PIN = 34
IN1     = 25
IN2     = 26
ENA     = 32

def setup():
    analogPin(POT_PIN)
    pinMode(IN1, OUTPUT)
    pinMode(IN2, OUTPUT)
    pwmSetup(ENA, freq=1000)
    # Motor direction: forward
    digitalWrite(IN1, 1)
    digitalWrite(IN2, 0)
    print("DC Motor Speed Control Ready")
    print("Turn potentiometer to change speed")

def main():
    setup()
    while True:
        raw   = analogRead(POT_PIN)
        speed = mapValue(raw, 0, 4095, 0, 1023)
        pct   = int((speed / 1023) * 100)
        pwmWrite(ENA, speed)
        print(f"Pot: {raw}  |  Speed: {speed}/1023  ({pct}%)")
        time.sleep_ms(100)

def cleanup():
    pwmWrite(ENA, 0)
    digitalWrite(IN1, 0)
    digitalWrite(IN2, 0)
    print("Motor stopped")

run(main, cleanup)
```

### Speed Control Table
| Pot Position | ADC Value | PWM Duty | Motor Speed |
|-------------|-----------|----------|-------------|
| Min (GND) | 0 | 0 | Stopped |
| Quarter | ~1024 | ~256 | 25% |
| Half | ~2048 | ~512 | 50% |
| Three-quarter | ~3072 | ~768 | 75% |
| Max (3.3V) | 4095 | 1023 | 100% |

### Learning Outcomes
- L298N motor driver wiring
- Analog pot to PWM mapping
- Motor direction control with IN1/IN2

---

## 18. Servo Motor Angle Controller

### Objective
Control servo motor angle (0°–180°) using a potentiometer. Real-time analog-to-angle mapping.

### Components Required
| Component | Quantity |
|-----------|----------|
| ESP32 Board | 1 |
| SG90 Servo Motor | 1 |
| 10kΩ Potentiometer | 1 |
| Breadboard + Jumper Wires | — |

### Circuit Diagram
```
GPIO34 ──── POT middle  |  POT ends → 3.3V and GND

GPIO13 ──── Servo Signal (Yellow/Orange wire)
Servo Red  ──── 5V
Servo Brown ──── GND
```

### Servo PWM Specification
```
Frequency : 50 Hz (20ms period)
0°        : 0.5ms pulse  → duty ~26  (out of 1023)
90°       : 1.5ms pulse  → duty ~77
180°      : 2.5ms pulse  → duty ~128
```

### Code
```python
from analog import analogPin, analogRead, mapValue
from digital import pwmSetup, pwmWrite
from systemio import run
import time

POT_PIN   = 34
SERVO_PIN = 13

def setup():
    analogPin(POT_PIN)
    pwmSetup(SERVO_PIN, freq=50)
    print("Servo Angle Controller Ready")
    print("Turn potentiometer to control angle (0°–180°)")

def angle_to_duty(angle):
    """Convert degrees (0–180) to PWM duty cycle."""
    min_duty = 26     # 0.5ms at 50Hz → ~2.5%
    max_duty = 128    # 2.5ms at 50Hz → ~12.5%
    return int(min_duty + (angle / 180.0) * (max_duty - min_duty))

def set_servo(angle):
    angle = max(0, min(180, angle))
    duty = angle_to_duty(angle)
    pwmWrite(SERVO_PIN, duty)
    return angle

def main():
    setup()
    while True:
        raw   = analogRead(POT_PIN)
        angle = mapValue(raw, 0, 4095, 0, 180)
        actual = set_servo(angle)
        print(f"Pot: {raw}  →  Angle: {actual}°")
        time.sleep_ms(50)

def cleanup():
    set_servo(0)
    print("Servo at 0°")

run(main, cleanup)
```

### Learning Outcomes
- Servo PWM signal specification
- ADC to angle mapping
- Servo position control

---

## 19. Line Follower Robot

### Objective
Build a robot that follows a black line on white surface using two IR reflective sensors. If the robot drifts off the line, it self-corrects by adjusting motor speeds.

### Components Required
| Component | Quantity |
|-----------|----------|
| ESP32 Board | 1 |
| IR Line Sensor Module × 2 | 2 |
| L298N Motor Driver | 1 |
| DC Motors | 2 |
| Robot Chassis + Wheels | 1 set |
| Battery Pack (6–9V) | 1 |
| Breadboard + Jumper Wires | — |

### Circuit Diagram
```
GPIO34 ──── Left IR Sensor  AOUT
GPIO35 ──── Right IR Sensor AOUT
Sensors VCC ──── 3.3V  |  GND ──── GND

L298N IN1=GPIO25, IN2=GPIO26, ENA=GPIO32   (Left Motor)
L298N IN3=GPIO27, IN4=GPIO14, ENB=GPIO33   (Right Motor)
```

### Logic Table
| Left Sensor | Right Sensor | Action |
|-------------|-------------|--------|
| Black (HIGH) | Black (HIGH) | Forward |
| White (LOW) | Black (HIGH) | Turn Right |
| Black (HIGH) | White (LOW) | Turn Left |
| White (LOW) | White (LOW) | Stop |

### Code
```python
from analog import analogPin, analogRead
from digital import pinMode, digitalWrite, OUTPUT, pwmSetup, pwmWrite
from systemio import run
import time

IR_LEFT  = 34
IR_RIGHT = 35

IN1, IN2 = 25, 26
IN3, IN4 = 27, 14
ENA, ENB = 32, 33

SPEED     = 700
TURN_SLOW = 200
# Threshold: above = white, below = black
LINE_THRESHOLD = 2000

def setup():
    analogPin(IR_LEFT)
    analogPin(IR_RIGHT)
    for pin in [IN1, IN2, IN3, IN4]:
        pinMode(pin, OUTPUT)
    pwmSetup(ENA, freq=1000)
    pwmSetup(ENB, freq=1000)
    print("Line Follower Robot Ready")

def motor(l_speed, r_speed):
    fwd_l = l_speed >= 0
    fwd_r = r_speed >= 0
    digitalWrite(IN1, 1 if fwd_l else 0)
    digitalWrite(IN2, 0 if fwd_l else 1)
    digitalWrite(IN3, 1 if fwd_r else 0)
    digitalWrite(IN4, 0 if fwd_r else 1)
    pwmWrite(ENA, min(1023, abs(l_speed)))
    pwmWrite(ENB, min(1023, abs(r_speed)))

def stop():
    motor(0, 0)

def main():
    setup()
    while True:
        left_val  = analogRead(IR_LEFT)
        right_val = analogRead(IR_RIGHT)

        on_left  = left_val  < LINE_THRESHOLD   # True = sensor sees black line
        on_right = right_val < LINE_THRESHOLD

        if on_left and on_right:
            motor(SPEED, SPEED)
            print("→ Forward")
        elif not on_left and on_right:
            motor(TURN_SLOW, SPEED)
            print("← Turn Right")
        elif on_left and not on_right:
            motor(SPEED, TURN_SLOW)
            print("→ Turn Left")
        else:
            stop()
            print("■ Stop (lost line)")

        time.sleep_ms(30)

def cleanup():
    stop()
    print("Robot stopped")

run(main, cleanup)
```

### Learning Outcomes
- IR reflective sensor logic
- Differential motor control
- Boolean decision making for navigation

---

## 20. Bluetooth Controlled Car

### Objective
Control a robot car over Bluetooth using a smartphone. Commands sent via Serial Bluetooth terminal control forward, backward, left, right, and stop.

### Components Required
| Component | Quantity |
|-----------|----------|
| ESP32 Board (Bluetooth capable) | 1 |
| L298N Motor Driver | 1 |
| DC Motors | 2 |
| Robot Chassis | 1 |
| Battery Pack | 1 |
| Smartphone with BT Terminal App | 1 |

### Bluetooth Commands
| Command | Action |
|---------|--------|
| `F` | Forward |
| `B` | Backward |
| `L` | Turn Left |
| `R` | Turn Right |
| `S` | Stop |
| `1`–`9` | Speed 10%–90% |

### Code
```python
from digital import pinMode, digitalWrite, OUTPUT, pwmSetup, pwmWrite
from systemio import run
from machine import UART
import time

# ESP32 built-in Bluetooth via UART (use BLE or classic BT module)
# For HC-05/HC-06 Bluetooth module:
uart = UART(2, baudrate=9600, tx=17, rx=16)

IN1, IN2 = 25, 26
IN3, IN4 = 27, 14
ENA, ENB = 32, 33

speed = 700

def setup():
    for pin in [IN1, IN2, IN3, IN4]:
        pinMode(pin, OUTPUT)
    pwmSetup(ENA, freq=1000)
    pwmSetup(ENB, freq=1000)
    stop()
    print("Bluetooth Car Ready — Connect via BT terminal")

def motor(l, r):
    digitalWrite(IN1, 1 if l >= 0 else 0)
    digitalWrite(IN2, 0 if l >= 0 else 1)
    digitalWrite(IN3, 1 if r >= 0 else 0)
    digitalWrite(IN4, 0 if r >= 0 else 1)
    pwmWrite(ENA, min(1023, abs(l)))
    pwmWrite(ENB, min(1023, abs(r)))

def stop():
    motor(0, 0)

def process_command(cmd):
    global speed
    cmd = cmd.strip().upper()
    if cmd == 'F':
        motor(speed, speed);  print("Forward")
    elif cmd == 'B':
        motor(-speed, -speed); print("Backward")
    elif cmd == 'L':
        motor(0, speed);       print("Left")
    elif cmd == 'R':
        motor(speed, 0);       print("Right")
    elif cmd == 'S':
        stop();                print("Stop")
    elif cmd.isdigit():
        speed = int(int(cmd) * 113)   # 1–9 → 113–1017
        print(f"Speed set: {speed}/1023")

def main():
    setup()
    while True:
        if uart.any():
            data = uart.read(1)
            if data:
                cmd = data.decode('utf-8', 'ignore')
                process_command(cmd)
        time.sleep_ms(10)

def cleanup():
    stop()
    print("Car stopped")

run(main, cleanup)
```

### Setup Instructions
1. Wire HC-05/HC-06 TX → GPIO16, RX → GPIO17 (use voltage divider on RX).
2. Default Bluetooth password: `1234`.
3. Install "Serial Bluetooth Terminal" on smartphone.
4. Pair ESP32 and send commands.

### Learning Outcomes
- UART serial communication
- Bluetooth module interfacing
- Command parsing for robot control

---

## 21. IR Remote Controlled Robot

### Objective
Control a robot using a TV IR remote control. Decode NEC IR protocol signals to navigate the robot in four directions.

### Components Required
| Component | Quantity |
|-----------|----------|
| ESP32 Board | 1 |
| VS1838B IR Receiver Module | 1 |
| L298N Motor Driver | 1 |
| DC Motors | 2 |
| Robot Chassis | 1 |
| Any NEC IR Remote | 1 |
| Battery Pack | 1 |

### Circuit Diagram
```
GPIO15 ──── IR Receiver OUT
IR Receiver VCC ──── 3.3V  |  GND ──── GND

L298N IN1=GPIO25, IN2=GPIO26, ENA=GPIO32  (Left Motor)
L298N IN3=GPIO27, IN4=GPIO14, ENB=GPIO33  (Right Motor)
```

### Code
```python
from digital import pinMode, digitalRead, OUTPUT, INPUT, pwmSetup, pwmWrite, digitalWrite
from systemio import run
from machine import Pin
import time

IR_PIN = 15
IN1, IN2 = 25, 26
IN3, IN4 = 27, 14
ENA, ENB = 32, 33
SPEED = 700

# Map IR hex codes to actions (use test code to discover your remote's codes)
IR_COMMANDS = {
    0xFF629D: "FORWARD",
    0xFFA857: "BACKWARD",
    0xFF22DD: "LEFT",
    0xFFC23D: "RIGHT",
    0xFF02FD: "STOP",
}

def setup():
    global ir_pin
    ir_pin = Pin(IR_PIN, Pin.IN)
    for pin in [IN1, IN2, IN3, IN4]:
        pinMode(pin, OUTPUT)
    pwmSetup(ENA, freq=1000)
    pwmSetup(ENB, freq=1000)
    stop_motors()
    print("IR Remote Robot Ready")
    print("Point remote at receiver and press buttons")

def motor(l, r):
    digitalWrite(IN1, 1 if l >= 0 else 0)
    digitalWrite(IN2, 0 if l >= 0 else 1)
    digitalWrite(IN3, 1 if r >= 0 else 0)
    digitalWrite(IN4, 0 if r >= 0 else 1)
    pwmWrite(ENA, min(1023, abs(l)))
    pwmWrite(ENB, min(1023, abs(r)))

def stop_motors():
    motor(0, 0)

def decode_nec():
    """Minimal NEC IR decoder."""
    # Wait for start pulse (9ms LOW)
    t = time.ticks_us()
    while ir_pin.value() == 1:
        if time.ticks_diff(time.ticks_us(), t) > 15000:
            return None

    # Measure start pulse
    t = time.ticks_us()
    while ir_pin.value() == 0:
        pass
    start_low = time.ticks_diff(time.ticks_us(), t)

    if not (8000 < start_low < 10000):
        return None   # Not NEC start

    # Space (4.5ms HIGH)
    while ir_pin.value() == 1:
        pass

    # Read 32 bits
    bits = 0
    for i in range(32):
        while ir_pin.value() == 0:
            pass
        t = time.ticks_us()
        while ir_pin.value() == 1:
            pass
        bit_len = time.ticks_diff(time.ticks_us(), t)
        bits = (bits >> 1) | (0x80000000 if bit_len > 1000 else 0)

    return bits

def execute_command(action):
    if action == "FORWARD":
        motor(SPEED, SPEED)
    elif action == "BACKWARD":
        motor(-SPEED, -SPEED)
    elif action == "LEFT":
        motor(0, SPEED)
    elif action == "RIGHT":
        motor(SPEED, 0)
    elif action == "STOP":
        stop_motors()
    print(f"Action: {action}")

def main():
    setup()
    while True:
        if ir_pin.value() == 0:   # IR signal incoming
            code = decode_nec()
            if code:
                print(f"IR Code: {hex(code)}")
                action = IR_COMMANDS.get(code)
                if action:
                    execute_command(action)
                else:
                    print("Unknown code — add to IR_COMMANDS dict")
        time.sleep_ms(10)

def cleanup():
    stop_motors()
    print("Robot stopped")

run(main, cleanup)
```

> **Tip:** First run a simple IR test script to discover the hex codes for each button on your remote, then add them to `IR_COMMANDS`.

### Learning Outcomes
- NEC IR protocol decoding
- Timing-based signal measurement
- Remote-controlled robot navigation

---

## 22. Maze Solver Beginner Robot

### Objective
Build a robot that can navigate through a simple maze using left-hand-rule wall following. Uses two ultrasonic sensors (front and left) to make decisions.

### Components Required
| Component | Quantity |
|-----------|----------|
| ESP32 Board | 1 |
| HC-SR04 Ultrasonic Sensors | 2 |
| L298N Motor Driver | 1 |
| DC Motors | 2 |
| Robot Chassis | 1 |
| Battery Pack | 1 |
| Breadboard + Jumper Wires | — |

### Circuit Diagram
```
Front Sensor: TRIG=GPIO5,  ECHO=GPIO18
Left Sensor:  TRIG=GPIO19, ECHO=GPIO21

L298N IN1=GPIO25, IN2=GPIO26, ENA=GPIO32  (Left Motor)
L298N IN3=GPIO27, IN4=GPIO14, ENB=GPIO33  (Right Motor)
```

### Left-Hand Rule Algorithm
```
1. If left is open → turn left (follow wall)
2. Else if front is open → go forward
3. Else → turn right
4. If blocked all → turn around
```

### Code
```python
from digital import pinMode, OUTPUT, pwmSetup, pwmWrite, digitalWrite
from systemio import run
from machine import Pin
import time

# Sensor pins
TRIG_F, ECHO_F = 5,  18
TRIG_L, ECHO_L = 19, 21

IN1, IN2 = 25, 26
IN3, IN4 = 27, 14
ENA, ENB = 32, 33

SPEED      = 600
TURN_DELAY = 550   # ms to turn 90°
WALL_DIST  = 20    # cm — obstacle threshold

def setup():
    global tf, ef, tl, el
    tf = Pin(TRIG_F, Pin.OUT); ef = Pin(ECHO_F, Pin.IN)
    tl = Pin(TRIG_L, Pin.OUT); el = Pin(ECHO_L, Pin.IN)
    for pin in [IN1, IN2, IN3, IN4]:
        pinMode(pin, OUTPUT)
    pwmSetup(ENA, freq=1000)
    pwmSetup(ENB, freq=1000)
    stop()
    print("Maze Solver Ready")

def measure(trig, echo):
    trig.value(0); time.sleep_us(2)
    trig.value(1); time.sleep_us(10)
    trig.value(0)
    t = time.ticks_us()
    while echo.value() == 0:
        if time.ticks_diff(time.ticks_us(), t) > 25000: return 999
    s = time.ticks_us()
    while echo.value() == 1:
        if time.ticks_diff(time.ticks_us(), s) > 25000: return 999
    return time.ticks_diff(time.ticks_us(), s) * 0.034 / 2

def motor(l, r):
    digitalWrite(IN1, 1 if l >= 0 else 0); digitalWrite(IN2, 0 if l >= 0 else 1)
    digitalWrite(IN3, 1 if r >= 0 else 0); digitalWrite(IN4, 0 if r >= 0 else 1)
    pwmWrite(ENA, min(1023, abs(l))); pwmWrite(ENB, min(1023, abs(r)))

def stop():      motor(0, 0)
def forward():   motor(SPEED, SPEED)
def turn_right(): motor(SPEED, -SPEED); time.sleep_ms(TURN_DELAY); stop()
def turn_left():  motor(-SPEED, SPEED); time.sleep_ms(TURN_DELAY); stop()
def turn_around(): motor(SPEED, -SPEED); time.sleep_ms(TURN_DELAY * 2); stop()

def main():
    setup()
    while True:
        front_dist = measure(tf, ef)
        left_dist  = measure(tl, el)

        print(f"Front: {front_dist:.0f}cm  Left: {left_dist:.0f}cm")

        if left_dist > WALL_DIST:
            print("→ Turn LEFT (open)")
            turn_left()
            time.sleep_ms(200)
            forward()
        elif front_dist > WALL_DIST:
            print("→ Forward")
            forward()
        else:
            print("→ Turn RIGHT (blocked)")
            stop()
            turn_right()

        time.sleep_ms(100)

def cleanup():
    stop()
    print("Maze solver stopped")

run(main, cleanup)
```

### Decision Table (Left-Hand Rule)
| Left Wall | Front Wall | Action |
|-----------|-----------|--------|
| Open | Any | Turn Left |
| Blocked | Open | Go Forward |
| Blocked | Blocked | Turn Right |

### Learning Outcomes
- Multi-sensor robot navigation
- Left-hand wall-following algorithm
- Timed motor turns for angle estimation

---

## 23. Basic Robot Arm

### Objective
Control a 3-joint robot arm using three servo motors and three potentiometers. Each pot controls one joint (base, shoulder, elbow) independently in real time.

### Components Required
| Component | Quantity |
|-----------|----------|
| ESP32 Board | 1 |
| SG90 / MG90S Servo Motors | 3 |
| 10kΩ Potentiometers | 3 |
| 5V Power Supply (for servos) | 1 |
| Breadboard + Jumper Wires | — |

### Circuit Diagram
```
GPIO34 ──── POT1 (Base)
GPIO35 ──── POT2 (Shoulder)
GPIO32 ──── POT3 (Elbow)

GPIO13 ──── Servo1 Signal (Base)
GPIO14 ──── Servo2 Signal (Shoulder)
GPIO27 ──── Servo3 Signal (Elbow)

Servo Power: ALL servos VCC → External 5V, GND → Common GND
```

> **Important:** Use an external 5V supply for servos. Running 3 servos from ESP32's 3.3V pin will cause instability.

### Code
```python
from analog import analogPin, analogRead, mapValue
from digital import pwmSetup, pwmWrite
from systemio import run
import time

# ADC Pins for potentiometers
POT_BASE     = 34
POT_SHOULDER = 35
POT_ELBOW    = 32

# Servo PWM pins
SERVO_BASE     = 13
SERVO_SHOULDER = 14
SERVO_ELBOW    = 27

# Arm angle limits (degrees) — tune to physical arm
LIMITS = {
    'base':     (0, 180),
    'shoulder': (30, 150),   # Mechanical limit
    'elbow':    (0, 160),
}

def setup():
    for pin in [POT_BASE, POT_SHOULDER, POT_ELBOW]:
        analogPin(pin)
    for pin in [SERVO_BASE, SERVO_SHOULDER, SERVO_ELBOW]:
        pwmSetup(pin, freq=50)
    # Park arm at safe position
    set_servo(SERVO_BASE,     90)
    set_servo(SERVO_SHOULDER, 90)
    set_servo(SERVO_ELBOW,    90)
    time.sleep(1)
    print("Robot Arm Ready")
    print("Turn pots to move joints")

def angle_to_duty(angle):
    """Convert 0–180° to PWM duty (26–128 at 50Hz)."""
    return int(26 + (angle / 180.0) * 102)

def set_servo(pin, angle):
    angle = max(0, min(180, angle))
    pwmWrite(pin, angle_to_duty(angle))
    return angle

def read_angle(pot_pin, min_ang, max_ang):
    raw = analogRead(pot_pin)
    return mapValue(raw, 0, 4095, min_ang, max_ang)

def main():
    setup()
    prev = {'base': -1, 'shoulder': -1, 'elbow': -1}

    while True:
        base_ang     = read_angle(POT_BASE,     *LIMITS['base'])
        shoulder_ang = read_angle(POT_SHOULDER, *LIMITS['shoulder'])
        elbow_ang    = read_angle(POT_ELBOW,    *LIMITS['elbow'])

        # Only update if angle changed by more than 1°
        if abs(base_ang     - prev['base'])     > 1:
            set_servo(SERVO_BASE, base_ang)
            prev['base'] = base_ang

        if abs(shoulder_ang - prev['shoulder']) > 1:
            set_servo(SERVO_SHOULDER, shoulder_ang)
            prev['shoulder'] = shoulder_ang

        if abs(elbow_ang    - prev['elbow'])    > 1:
            set_servo(SERVO_ELBOW, elbow_ang)
            prev['elbow'] = elbow_ang

        print(f"Base:{base_ang:3d}°  Shoulder:{shoulder_ang:3d}°  Elbow:{elbow_ang:3d}°")
        time.sleep_ms(50)

def cleanup():
    set_servo(SERVO_BASE,     90)
    set_servo(SERVO_SHOULDER, 90)
    set_servo(SERVO_ELBOW,    90)
    print("Arm parked at 90°")

run(main, cleanup)
```

### Joint Control Summary
| Joint | Pot Pin | Servo Pin | Range |
|-------|---------|-----------|-------|
| Base (rotation) | GPIO 34 | GPIO 13 | 0°–180° |
| Shoulder (up/down) | GPIO 35 | GPIO 14 | 30°–150° |
| Elbow (bend) | GPIO 32 | GPIO 27 | 0°–160° |

### Extensions
- Add a 4th servo for a gripper (claw).
- Record angle sequences and play them back.
- Control via Bluetooth for remote arm operation.

### Learning Outcomes
- Multi-servo synchronous control
- Physical joint limit enforcement
- Dead-zone filtering to prevent servo jitter
- Robot arm kinematics basics

---

---

## QUICK REFERENCE — Library Functions Used

| Function | Library | Used In Projects |
|----------|---------|-----------------|
| `pinMode(pin, mode)` | digital | 1–16, 17–23 |
| `digitalWrite(pin, val)` | digital | 1–16 |
| `digitalRead(pin)` | digital | 5, 6, 12 |
| `togglePin(pin)` | digital | — |
| `blink(pin, times)` | digital | — |
| `pulse(pin, ms)` | digital | — |
| `pwmSetup(pin, freq)` | digital | 3, 4, 7, 13–23 |
| `pwmWrite(pin, duty)` | digital | 3, 4, 7, 13–23 |
| `pwmWritePercent(pin, %)` | digital | — |
| `pwmStop(pin)` | digital | 4, 10, 16 |
| `attachInterrupt(pin, cb)` | digital | 5 |
| `analogPin(pin)` | analog | 7–16, 17–18, 23 |
| `analogRead(pin)` | analog | 7–16 |
| `analogVoltage(pin)` | analog | 9 |
| `analogPercent(pin)` | analog | 11 |
| `analogAverage(pin, n)` | analog | 8, 9 |
| `analogSmooth(pin, w)` | analog | 13, 15 |
| `mapValue(x, ...)` | analog | 7, 8, 15, 17–18, 23 |
| `dacWrite(pin, val)` | analog | — |
| `dacWritePercent(pin, %)` | analog | — |
| `run(main, cleanup)` | systemio | ALL projects |

---

## SAFETY NOTES FOR STUDENTS

1. **Voltage Limits:** ESP32 GPIO pins operate at **3.3V**. Never connect 5V directly to GPIO pins.
2. **Motor Power:** Always use a **separate power supply** for motors. Motor current can damage the ESP32.
3. **Sensor Warm-Up:** Gas sensors (MQ-2) need **20 seconds** warm-up time before accurate readings.
4. **Servo Power:** Three or more servos should use an **external 5V supply**, not the ESP32's onboard regulator.
5. **Short Circuits:** Always double-check wiring before powering on. A short circuit can damage components permanently.
6. **ADC Pins:** Not all ESP32 GPIO pins support ADC. Safe ADC pins: **GPIO 32–39**. GPIO 34–39 are **input-only**.
7. **Cleanup Always:** Use `systemio.run(main, cleanup)` in every project to safely shut down motors and LEDs on program exit.

---

*Document prepared for School Robotics Students | ESP32 MicroPython | Based on analog.py, digital.py, systemio.py libraries*
