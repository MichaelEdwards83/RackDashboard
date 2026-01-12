# Hardware Wiring Guide

This guide details how to wire the sensors and LEDs to your Raspberry Pi 5 (or Pi 4) GPIO header.

> [!CAUTION]
> **Check Voltages!**
> - **DS18B20 Sensors**: Connect VCC to **3.3V**. Connecting to 5V *might* work but is risky for the Pi's 3.3V logic pins.
> - **WS2812B LEDs**: Connect VCC to **5V**. The Data line (3.3V) usually drives them fine, but for long runs you may need a logic level shifter (3.3V -> 5V).

## Pinout Summary

| Component | Pin Function | GPIO # | Physical Pin |
| :--- | :--- | :--- | :--- |
| **Sensors** | 1-Wire Data | **GPIO 4** | Pin 7 |
| **LEDs** | PCM/PWM | **GPIO 18** | Pin 12 |
| **Ground** | GND | - | Pin 6, 9, 14, etc. |
| **3.3V Power** | 3V3 | - | Pin 1, 17 |
| **5V Power** | 5V | - | Pin 2, 4 |

## 1. Temperature Sensors (DS18B20)

You have a **Split Configuration** with two groups of sensors to simplify wiring runs.

### Group A: Probes 1, 2, 3
- **Data Pin**: Connect to **GPIO 4 (Pin 7)**.
- **Resistor**: Connect a 4.7kΩ resistor between Data (GPIO 4) and 3.3V power.

### Group B: Probes 4, 5
- **Data Pin**: Connect to **GPIO 17 (Pin 11)**.
- **Resistor**: Connect a 4.7kΩ resistor between Data (GPIO 17) and 3.3V power.

### Common Power
- **Red (VCC)**: All sensors connect to **3.3V (Pin 1)**.
- **Black (GND)**: All sensors connect to **Ground (Pin 6 or 9)**.

### Required Software Config
You must enable both pins in `/boot/firmware/config.txt`:

```ini
# At the bottom of the file:
dtoverlay=w1-gpio,gpiopin=4
dtoverlay=w1-gpio,gpiopin=17
```
*(Reboot required after editing)*

## 2. LED Strip (WS2812B)

**Wiring:**
1.  **Red (5V)**: Connect to **5V (Pin 2)** *or external 5V PSU if >10 LEDs*.
2.  **White (GND)**: Connect to **Ground (Pin 9)**.
    - *If using external PSU, connect PSU ground to Pi ground.*
3.  **Green (Data)**: Connect to **GPIO 10 (Pin 19)** (SPI0 MOSI).

## Diagram

```
       Raspberry Pi GPIO Header
       ------------------------
[3V3]  1  o o  2  [5V]  ----> Red Wire (LEDs)
[SDA]  3  o o  4  [5V]
[GP4]  7  o o  6  [GND] ----> Black Wire (Sensors) & White Wire (LEDs)
       |
       +--> Data (Sensors) + Resistor
...
[GP10] 19 o o 20
       |
       +--> Data (LEDs)
```
