# Thermoregulation System

An embedded IoT system built with the CRCibernetica IdeaBoard (ESP32) and CircuitPython that monitors and automatically regulates the water temperature of an axolotl aquarium, keeping it within the species' safe biological range (14°C–18°C).

---

## 🌡️ The Problem

Many aquatic and semi-aquatic species require precise water temperature ranges to thrive. In tropical environments like Costa Rica, where indoor temperatures average 25°C–28°C, maintaining cold water conditions without technological intervention is impossible. Species such as the axolotl (Ambystoma mexicanum) — the primary use case for this system — require temperatures between 14°C and 18°C; values above 22°C cause metabolic stress, fungal infections, and can be fatal. This system is designed to be configurable for any species with specific thermal requirements, simply by adjusting the thresholds in config.py.

## ✅ Features

- Continuous water temperature monitoring via DS18B20 waterproof sensor
- Automatic fan activation based on configurable temperature thresholds
- Proportional fan speed control (PWM) relative to temperature excess
- Hysteresis logic to prevent constant fan on/off cycling
- Real-time temperature and system status display on a 16×2 LCD
- Safe shutdown on keyboard interrupt (Ctrl-C)
- Critical temperature alert displayed on LCD

---

## 🔧 Hardware

| Component                       | Purpose                      | Quantity |
| ------------------------------- | ---------------------------- | -------- |
| CRCibernetica IdeaBoard (ESP32) | Main microcontroller         | 1        |
| DS18B20 Waterproof Sensor       | Water temperature sensing    | 1        |
| LCD 1602 I2C (PCF8574, 0x27)    | Real-time status display     | 1        |
| MOSFET PWM Module               | Fan speed control            | 1        |
| 5V Relay Module (DIYables)      | Master power switch for fans | 1        |
| XPG Vento 120 ARGB PWM (3-pack) | Evaporative cooling fans     | 3        |
| CPT Buck Converter (12V→5V, 3A) | Logic power supply           | 1        |
| 12V 2A Power Supply             | Main power source            | 1        |
| DC Barrel Jack Adapter          | Power distribution           | 1        |
| 4.7kΩ Resistor                  | DS18B20 1-Wire pull-up       | 1        |
| Breadboard (PB-105)             | Component interconnection    | 1        |
| Dupont Jumper Wires (M-M, M-F)  | Wiring                       | ~20      |

---

## 📐 Wiring

### Power Distribution

| From                       | To                    | Voltage |
| -------------------------- | --------------------- | ------- |
| Power Supply (barrel jack) | Barrel Jack Adapter   | 12V     |
| Barrel Jack Adapter `+`    | 12V rail (breadboard) | 12V     |
| Barrel Jack Adapter `−`    | GND rail (breadboard) | GND     |
| Buck IN+                   | 12V rail (breadboard) | 12V     |
| Buck IN−                   | GND rail (breadboard) | GND     |
| Buck OUT+ (yellow)         | 5V rail (breadboard)  | 5V      |
| Buck OUT− (black)          | GND rail (breadboard) | GND     |
| IdeaBoard `V+`             | 5V rail (breadboard)  | 5V      |
| IdeaBoard `GND`            | GND rail (breadboard) | GND     |

### DS18B20 Sensor

| Sensor Wire    | Connection                               |
| -------------- | ---------------------------------------- |
| Black (GND)    | GND rail (breadboard)                    |
| Red (VCC)      | Breadboard row → IdeaBoard `3.3V` pin    |
| Yellow (DATA)  | Breadboard row → IdeaBoard `IO5`         |
| 4.7kΩ resistor | Between Red row and Yellow row (pull-up) |

> ⚠️ **Note:** IO4 has boot-strapping conflicts on this ESP32. Use IO5 for reliable 1-Wire communication.

### LCD I2C (1602, PCF8574 backpack)

| LCD Pin | Connection                        |
| ------- | --------------------------------- |
| GND     | GND rail (breadboard)             |
| VDD     | 5V rail (breadboard)              |
| SDA     | Breadboard row → IdeaBoard `IO21` |
| SCL     | Breadboard row → IdeaBoard `IO22` |

> ⚠️ **Note:** The PCF8574 module has 5V pull-ups that conflict with CircuitPython's I2C validation. A software workaround using `digitalio.Pull.UP` pre-initialization is required. See `main.py` for implementation.

### MOSFET PWM Module

| MOSFET Pin    | Connection            |
| ------------- | --------------------- |
| DC+           | 12V rail (breadboard) |
| DC−           | GND rail (breadboard) |
| GND (control) | GND rail (breadboard) |
| PWM (signal)  | IdeaBoard `IO18`      |
| OUT+          | Relay `COM`           |
| OUT−          | GND rail (breadboard) |

### Relay Module (5V)

| Relay Pin | Connection                |
| --------- | ------------------------- |
| VCC/DC+   | 5V rail (breadboard)      |
| GND/DC−   | GND rail (breadboard)     |
| IN        | IdeaBoard `IO19`          |
| COM       | MOSFET `OUT+`             |
| NO        | Fan connector Pin 2 (12V) |

### XPG Vento 120 Fans (3x daisy-chained)

| Fan Pin            | Connection                   |
| ------------------ | ---------------------------- |
| Pin 1 (arrow, GND) | GND rail (breadboard)        |
| Pin 2 (12V)        | Relay `NO`                   |
| Pin 3 (tachometer) | Not connected                |
| Pin 4 (PWM signal) | Not connected                |
| ARGB connector     | Not connected (future phase) |

> Fans are connected in daisy-chain: Main → Fan B → Fan C

---

## 🌡️ Temperature Logic

| Condition            | Action                                            |
| -------------------- | ------------------------------------------------- |
| `temp < 16°C`        | Fans OFF, relay OFF, LCD: "Temp ideal :)"         |
| `16°C ≤ temp < 18°C` | Maintain current state (hysteresis zone)          |
| `18°C ≤ temp < 22°C` | Fans ON, proportional speed, LCD: "Ventilando..." |
| `temp ≥ 22°C`        | Fans ON at 100%, LCD: "ALERTA CRITICA!"           |

Fan speed is calculated proportionally:

```
speed = min(int(65535 * ((temp - 18) / 4)), 65535)
```

---

## 📁 Project Structure

```
sistema-termorregulacion/
├── src/
│   ├── main.py        ← Main control loop
│   └── config.py      ← Pin assignments and temperature thresholds
├── hardware/
│   └── conexiones.md  ← Detailed wiring checklist
├── docs/
│   └── avance1.docx   ← Academic project report (Avance 1)
├── .gitignore
└── README.md
```

---

## ⚙️ Configuration

Edit `config.py` to adjust pins and thresholds:

```python
PIN_SENSOR = board.IO5
PIN_RELAY  = board.IO19
PIN_PWM    = board.IO18
PIN_SDA    = board.IO21
PIN_SCL    = board.IO22

TEMP_IDEAL_MAX  = 18.0   # Fans activate above this
TEMP_IDEAL_MIN  = 16.0   # Fans deactivate below this
TEMP_CRITICA    = 22.0   # Critical alert threshold
INTERVALO_LECTURA = 5    # Seconds between readings
```

---

## 🚀 Running the System

Connect the IdeaBoard via USB and open the REPL:

```bash
mpremote connect /dev/cu.usbserial-XXXX
```

Then execute:

```python
import sys
sys.path.append('/ajolote')
exec(open('/ajolote/main.py').read())
```

Press `Ctrl-C` to stop. The system will safely shut down fans and display "Sistema detenido con exito" before exiting.

---

## 🗺️ Roadmap

- [x] Temperature monitoring (DS18B20)
- [x] Automatic fan control (MOSFET + relay)
- [x] Real-time LCD display
- [x] Proportional speed control
- [x] Safe shutdown on Ctrl-C
- [ ] Telegram alerts on critical temperature
- [ ] ARGB LED control based on temperature state
- [ ] WiFi dashboard for remote monitoring

---

## 🏫 Academic Context

This project was developed as part of the Software Engineering program at **Universidad CENFOTEC**, Costa Rica. It combines embedded systems, IoT, and environmental monitoring concepts to address a real-world biological challenge.

---

## ⚠️ Important Notes

- Never push `secrets.py` to GitHub — it contains WiFi credentials and Telegram tokens
- IO4 on this ESP32 has boot-strapping interference with 1-Wire protocol — use IO5 instead
- The LCD's PCF8574 module operates at 5V pull-ups; CircuitPython requires a software workaround to initialize the I2C bus correctly
