# Hardware Documentation

This directory contains hardware-related documentation for the Kitronik Air Quality Board project.

## Files to Add

- `kitronik-air-quality-board-datasheet.pdf` - Official datasheet (from Kitronik)
- `microbit-v2-hardware.pdf` - BBC micro:bit v2 hardware documentation
- `pinout-diagrams.md` - Pin assignments and connections
- `component-specifications.md` - Detailed component specs
- `assembly-guide.md` - How to connect everything

## Component Overview

### Kitronik Air Quality Board (Model 5674)
- **BME688 Sensor**: Environmental monitoring (temp, humidity, pressure, air quality)
- **OLED Display**: 128x64 pixel monochrome display
- **Real Time Clock**: Battery-backed timekeeping
- **EEPROM**: 1Mb data storage
- **ZIP LEDs**: 3 programmable status indicators
- **Power Management**: 3xAA batteries or USB power

### Pin Assignments
- **P0, P1, P2**: General purpose I/O (broken out to pads)
- **P8**: ZIP LED control (NeoPixel compatible)
- **P19, P20**: I2C bus (SCL, SDA) - connects all onboard components

### I2C Device Addresses
- **0x68**: Real Time Clock (RTC)
- **0x77** (or 0x76): BME688 Environmental Sensor
- **0x3C**: SSD1306 OLED Display
- **0x50**: EEPROM Memory

## Power Requirements

- **Operating Voltage**: 3.3V (regulated onboard)
- **Power Sources**: 
  - 3x AA batteries (NiMH rechargeable recommended)
  - Micro USB connector
  - Solar panel input (with blocking diode)
- **Current Draw**: Up to 100mA maximum on breakout pins

## Environmental Specifications

### BME688 Operating Ranges
- **Temperature**: -40°C to +85°C
- **Pressure**: 300hPa to 1100hPa  
- **Humidity**: 0% to 100% RH
- **Air Quality Index**: 0-500 (0=Excellent, 500=Extremely Polluted)
- **eCO2**: 250-40000+ ppm (estimated)

## Assembly Notes

1. Insert BBC micro:bit firmly into edge connector
2. Ensure correct orientation (micro:bit USB port faces away from board)
3. Use NiMH rechargeable batteries if using solar charging
4. All I2C devices share the same bus (P19/P20)
