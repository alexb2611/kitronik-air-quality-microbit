# Kitronik Air Quality Board - BBC micro:bit Project

Environmental monitoring system using the Kitronik Air Quality Board with BBC micro:bit v2, featuring automatic RTC time setting and comprehensive sensor integration.

## Features

- 🕐 **Automatic RTC Time Setting** - No more manual time entry!
- 🌡️ **Environmental Monitoring** - Temperature, pressure, humidity, air quality
- 📺 **OLED Display** - Real-time data visualization  
- 💾 **Data Logging** - Store readings to onboard EEPROM
- 💡 **Status LEDs** - Visual system status indicators
- 🐍 **Pure Python** - MicroPython implementation

## Hardware

- **BBC micro:bit v2** - Main controller
- **Kitronik Air Quality Board** - Sensor and display platform
- **BME688 Sensor** - Environmental measurements
- **128x64 OLED Display** - Data visualization
- **Real Time Clock** - Battery-backed timekeeping
- **1Mb EEPROM** - Data storage

## Quick Start

1. **Flash the code**: Use [python.microbit.org](https://python.microbit.org) or Mu Editor
2. **Auto time-sync**: Run `time_injector.py` before flashing to inject current time
3. **Monitor data**: Watch readings on micro:bit display and OLED screen
4. **Log data**: Sensor readings automatically stored with timestamps

## Project Structure

```
microbit/
├── src/
│   ├── auto_rtc_setup.py           # Standalone RTC auto-setup
│   ├── kitronik_air_quality_complete.py  # Full system integration
│   └── time_injector.py            # Host computer time injection tool
├── docs/
│   └── hardware/                   # Hardware documentation
├── examples/                       # Code examples and tutorials
├── claude.md                       # Project knowledge base
└── README.md                       # This file
```

## Getting Started

### Option 1: Web Editor (Recommended)
1. Go to [python.microbit.org](https://python.microbit.org)
2. Copy code from `src/kitronik_air_quality_complete.py`
3. Update time values in the code with current time
4. Flash to micro:bit

### Option 2: Time Injector Script
1. Save your micro:bit code as a template
2. Run: `python time_injector.py your_template.py`
3. Flash the generated file with current time injected

## Development

- **Primary IDE**: [MicroPython Editor](https://python.microbit.org) (web-based)
- **Alternative**: [Mu Editor](https://codewith.mu) (offline)
- **Advanced**: Thonny or VS Code with micro:bit extensions

## Family Learning

This project is designed to be educational and engaging for young learners:
- Visual feedback with LEDs and display
- Real-world environmental monitoring
- Introduction to sensors and data logging
- Python programming concepts

## Contributing

This is a learning project - contributions, improvements, and educational enhancements welcome!

## Author

**Alex** - UK-based maker, father, and micro:bit enthusiast  
Created with assistance from Claude AI

## License

Open source - feel free to adapt and improve!

---

*Built with ❤️ for learning and environmental awareness*
