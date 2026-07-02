# Wiring Checklist

Complete step-by-step wiring guide for the axolotl thermoregulation system.
Follow this checklist in order before powering the system.

---

## Breadboard Power Rails

| Connection | From                      | To                          | Voltage |
| ---------- | ------------------------- | --------------------------- | ------- |
| ☐          | Barrel Jack Adapter `+`   | 12V rail (red, breadboard)  | 12V     |
| ☐          | Barrel Jack Adapter `−`   | GND rail (blue, breadboard) | GND     |
| ☐          | Buck `IN+` (red wire)     | 12V rail (breadboard)       | 12V     |
| ☐          | Buck `IN−` (black wire)   | GND rail (breadboard)       | GND     |
| ☐          | Buck `OUT+` (yellow wire) | 5V rail (breadboard)        | 5V      |
| ☐          | Buck `OUT−` (black wire)  | GND rail (breadboard)       | GND     |

---

## IdeaBoard Power

| Connection | From                  | To                                     | Voltage |
| ---------- | --------------------- | -------------------------------------- | ------- |
| ☐          | 5V rail (breadboard)  | IdeaBoard `V+` (green terminal block)  | 5V      |
| ☐          | GND rail (breadboard) | IdeaBoard `GND` (green terminal block) | GND     |

---

## DS18B20 Temperature Sensor

| Connection | Wire   | From                 | To                                    |
| ---------- | ------ | -------------------- | ------------------------------------- |
| ☐          | Black  | Sensor GND           | GND rail (breadboard)                 |
| ☐          | Red    | Sensor VCC           | Breadboard row → IdeaBoard `3.3V` pin |
| ☐          | Yellow | Sensor DATA          | Breadboard row → IdeaBoard `IO5`      |
| ☐          | —      | 4.7kΩ resistor leg 1 | Same row as red wire (VCC)            |
| ☐          | —      | 4.7kΩ resistor leg 2 | Same row as yellow wire (DATA)        |

> ⚠️ Use IO5, not IO4 — IO4 has boot-strapping conflicts with the 1-Wire protocol.

---

## LCD 1602 I2C (PCF8574 backpack, address 0x27)

| Connection | Pin | From       | To                                |
| ---------- | --- | ---------- | --------------------------------- |
| ☐          | GND | LCD module | GND rail (breadboard)             |
| ☐          | VDD | LCD module | 5V rail (breadboard)              |
| ☐          | SDA | LCD module | Breadboard row → IdeaBoard `IO21` |
| ☐          | SCL | LCD module | Breadboard row → IdeaBoard `IO22` |

> ⚠️ The PCF8574 module has 5V pull-ups. CircuitPython requires a `digitalio.Pull.UP` pre-initialization workaround before creating the I2C bus. See `src/main.py`.

---

## MOSFET PWM Module

| Connection | Pin  | From               | To                    |
| ---------- | ---- | ------------------ | --------------------- |
| ☐          | DC+  | MOSFET power input | 12V rail (breadboard) |
| ☐          | DC−  | MOSFET power GND   | GND rail (breadboard) |
| ☐          | GND  | MOSFET control GND | GND rail (breadboard) |
| ☐          | PWM  | MOSFET signal      | IdeaBoard `IO18`      |
| ☐          | OUT+ | MOSFET output      | Relay `COM`           |
| ☐          | OUT− | MOSFET output GND  | GND rail (breadboard) |

---

## Relay Module (5V, DIYables)

| Connection | Pin     | From         | To                        |
| ---------- | ------- | ------------ | ------------------------- |
| ☐          | VCC/DC+ | Relay power  | 5V rail (breadboard)      |
| ☐          | GND/DC− | Relay GND    | GND rail (breadboard)     |
| ☐          | IN      | Relay signal | IdeaBoard `IO19`          |
| ☐          | COM     | Relay input  | MOSFET `OUT+`             |
| ☐          | NO      | Relay output | Fan connector Pin 2 (12V) |

---

## XPG Vento 120 Fans (3x daisy-chained)

| Connection | Pin                | From             | To                    |
| ---------- | ------------------ | ---------------- | --------------------- |
| ☐          | Pin 1 (arrow, GND) | Main fan GND     | MOSFET `OUT−`         |
| ☐          | Pin 2 (12V)        | Main fan 12V     | Relay `NO`            |
| ☐          | —                  | Main fan → Fan B | Daisy-chain connector |
| ☐          | —                  | Fan B → Fan C    | Daisy-chain connector |

> Pins 3 (tachometer) and 4 (PWM signal) are not connected.
> ARGB connector is not connected (planned for future phase).

---

## IdeaBoard Pin Summary

| Pin  | Function              | Connected To          |
| ---- | --------------------- | --------------------- |
| IO5  | DS18B20 DATA (1-Wire) | Sensor yellow wire    |
| IO18 | MOSFET PWM signal     | MOSFET PWM pin        |
| IO19 | Relay control signal  | Relay IN pin          |
| IO21 | I2C SDA               | LCD SDA               |
| IO22 | I2C SCL               | LCD SCL               |
| 3.3V | Sensor power          | DS18B20 red wire      |
| V+   | Board power           | 5V rail (breadboard)  |
| GND  | Common ground         | GND rail (breadboard) |

---

## Pre-Power Checklist

Before connecting the 12V power supply:

- ☐ 12V and 5V rails are separate (no cross-connection)
- ☐ All GND connections share the same blue rail
- ☐ DS18B20 pull-up resistor is in place
- ☐ IO5 jumper is confirmed (not IO4)
- ☐ `secrets.py` is NOT committed to GitHub
- ☐ Fans are connected in daisy-chain order: Main → B → C
