# systemio.py — System I/O Library

A MicroPython utility library for ESP32 that provides safe program execution with structured error handling, keyboard interrupt detection, and optional cleanup on exit.

---

## Dependencies

```python
import sys
```

---

## Functions

### `run(main_function, cleanup_function=None)`

Executes a main function with full exception handling. Catches keyboard interrupts and runtime errors, runs an optional cleanup routine, and ensures a controlled shutdown in all cases.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `main_function` | `callable` | — | The main program loop or function to execute |
| `cleanup_function` | `callable` | `None` | Optional function called on exit to release resources |

---

## Execution Flow

```
run() called
    │
    ├─► main_function() starts
    │       │
    │       ├─► Runs normally
    │       │
    │       ├─► KeyboardInterrupt (Ctrl+C)
    │       │       └─► cleanup_function() → "Program Stopped Safely"
    │       │
    │       └─► Exception (runtime error)
    │               └─► cleanup_function() → continues
    │
    └─► finally: "System Exit" always prints
```

---

## Console Output

| Event | Output |
|---|---|
| Program starts | `Program Started` |
| Ctrl+C detected | `Keyboard Interrupt Detected` → `Stopping Program Safely...` |
| Cleanup error | `Cleanup Error: <error>` |
| Successful stop | `Program Stopped Safely` |
| Runtime error | `Runtime Error: <error>` |
| Always on exit | `System Exit` |

---

## Usage Examples

### Basic Usage

```python
from systemio import run

def main():
    while True:
        print("Running...")

run(main)
```

---

### With Cleanup

```python
from systemio import run
from digital import pinMode, digitalWrite, OUTPUT

pinMode(2, OUTPUT)

def main():
    while True:
        digitalWrite(2, 1)

def cleanup():
    digitalWrite(2, 0)   # Turn off LED on exit
    print("GPIO cleaned up")

run(main, cleanup)
```

---

### Full ESP32 Example

```python
from systemio import run
from digital import *
from analog import *

analogPin(34)
pwmSetup(5, freq=1000)

def main():
    while True:
        pct = analogPercent(34)
        pwmWritePercent(5, pct)

def cleanup():
    pwmStop(5)
    print("PWM stopped")

run(main, cleanup)
```

---

## Notes

- If `cleanup_function` raises an exception, the error is printed but execution continues normally to the `finally` block.
- The `finally` block always runs, regardless of how the program exits, ensuring `System Exit` is always printed.
- If no `cleanup_function` is provided, errors and interrupts still exit gracefully — only the cleanup step is skipped.
- This library does not call `sys.exit()` or perform a hard reset; control returns to the MicroPython REPL after `run()` completes.
