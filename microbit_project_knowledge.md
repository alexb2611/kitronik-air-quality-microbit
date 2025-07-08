# BBC micro:bit + Kitronik Air Quality Board Project

## Project Overview
**Goal**: Create a working air quality monitoring system using BBC micro:bit v2 with Kitronik Air Quality Board (Model 5674)

**Team**: Alex (Dad) and Albie (9-year-old son)

**Key Components**:
- BBC micro:bit v2
- Kitronik Air Quality Board with BME688 sensor, RTC, OLED display, EEPROM
- Environmental monitoring: temperature, humidity, pressure, air quality

## Hardware Setup

### Kitronik Air Quality Board Components:
- **BME688 Sensor**: Temperature, humidity, pressure, gas resistance/air quality
- **RTC**: Real-time clock with battery backup
- **OLED Display**: 128x64 pixel display
- **EEPROM**: 1Mb data storage
- **ZIP LEDs**: 3 status LEDs
- **Power**: 3x AA batteries or micro USB

### I2C Device Addresses (CORRECTED):
- **RTC**: `0x6F` (MCP7940-N) - NOT 0x68 as initially assumed
- **BME688**: `0x77` (Environmental sensor)
- **OLED**: `0x3C` (SSD1306 display)
- **EEPROM**: `0x54` (Memory storage)

## Development Journey

### Phase 1: Initial Python Implementation
- Created basic micro:bit Python code
- **Problem**: RTC and BME688 not responding
- Used wrong I2C addresses and initialization sequences

### Phase 2: Debug Investigation
- Created debug scripts to scan I2C bus
- Found no devices responding
- Suspected hardware or power issues

### Phase 3: Breakthrough - Official TypeScript Code
- **Key Discovery**: Found official Kitronik TypeScript extensions
- Analyzed actual working code from manufacturer
- Identified critical errors in our implementation

### Phase 4: Fixed Implementation
- Corrected I2C addresses
- Implemented proper initialization sequences
- Added comprehensive error handling

## Critical Fixes Made

### 1. RTC Address Correction
```python
# WRONG (our initial assumption)
RTC_ADDRESS = 0x68  # Standard DS1307

# CORRECT (from Kitronik TypeScript)
RTC_ADDRESS = 0x6F  # MCP7940-N chip
```

### 2. RTC Initialization Sequence
From TypeScript analysis, proper RTC setup requires:
1. Set external oscillator (write 0x00 to control register)
2. Enable battery backup (set bit 3 in weekday register)
3. Start oscillator (set bit 7 in seconds register)

### 3. BME688 Initialization Sequence
From TypeScript analysis, proper BME688 setup requires:
1. Check chip ID (should be 0x61)
2. Soft reset (write 0xB6 to reset register)
3. Set sleep mode
4. Configure oversampling rates
5. Set IIR filter
6. Enable gas conversion

### 4. BME688 Calibration Requirements
**Critical Discovery**: BME688 requires calibration coefficients for accurate readings:
- Temperature compensation: PAR_T1, PAR_T2, PAR_T3
- Pressure compensation: PAR_P1-PAR_P10
- Humidity compensation: PAR_H1-PAR_H7
- Gas resistance compensation: PAR_G1-PAR_G3

## File Structure

### Working Files:
- `main.py` - Fixed main program with correct I2C addresses
- `time_injector.py` - Script to inject current time before flashing
- `debug_rtc.py` - Debug script for RTC troubleshooting
- `debug_file.py` - Debug script with file logging

### TypeScript Reference Files:
- `bme688_base.ts` - Official BME688 implementation
- `rtc_base.ts` - Official RTC implementation
- `oled_base.ts` - Official OLED implementation
- `eeprom_base.ts` - Official EEPROM implementation

## Development Tools

### Recommended IDE:
- **MicroPython Editor**: https://python.microbit.org/v/3
- Web-based, no installation required
- Direct micro:bit flashing capability

### Alternative Tools:
- **Mu Editor**: Desktop Python editor with micro:bit support
- **Thonny**: Python IDE with micro:bit plugin
- **VS Code**: With micro:bit extensions

## Usage Instructions

### Quick Start:
1. Connect micro:bit to computer via USB
2. Run: `python time_injector.py main.py`
3. Flash updated `main.py` to micro:bit
4. Insert micro:bit into Kitronik Air Quality Board
5. Power on with batteries or USB

### Expected Behavior:
- Heart icon on startup
- "SCANNING I2C" - checking for hardware
- "RTC INIT" / "BME INIT" - initializing sensors
- "ALL OK" if successful
- Scrolling environmental data every 5 seconds

## Troubleshooting

### Common Issues:

#### "NO I2C DEVICES"
- Check micro:bit is properly seated in board
- Verify power (green LED should be on)
- Check battery connections

#### "RTC FAIL"
- Verify I2C address is 0x6F (not 0x68)
- Check RTC crystal is functioning
- May need battery backup for RTC

#### "BME FAIL"
- Verify I2C address is 0x77
- Check chip ID reads as 0x61
- Sensor may need warm-up time

### Debug Process:
1. Use I2C scanner to find active devices
2. Check individual component initialization
3. Verify register read/write operations
4. Monitor status messages on LED display

## Next Steps

### Immediate Improvements:
1. **Full BME688 Calibration**: Implement complete compensation algorithms
2. **OLED Display**: Add visual data display
3. **EEPROM Logging**: Persistent data storage
4. **Air Quality Algorithms**: Implement proper IAQ calculations

### Advanced Features:
1. **Data Analysis**: Long-term trend monitoring
2. **Alerts**: Threshold-based notifications
3. **Web Interface**: WiFi module integration
4. **Solar Power**: Renewable energy setup

## Educational Value

### Programming Concepts:
- I2C communication protocols
- Binary data manipulation (BCD conversion)
- Error handling and system reliability
- Real-time data processing

### Electronics Concepts:
- Sensor interfacing
- Power management
- Communication protocols
- Hardware debugging

### Science Applications:
- Environmental monitoring
- Data collection and analysis
- Understanding air quality factors
- Climate science basics

## Lessons Learned

### Key Insights:
1. **Always use official documentation** when available
2. **Hardware addresses can vary** between manufacturers
3. **Initialization sequences are critical** for complex sensors
4. **Debug incrementally** - test one component at a time
5. **TypeScript/JavaScript code** can be excellent reference for Python implementations

### Best Practices:
1. **Test basic I2C communication first** before complex features
2. **Use proper error handling** to identify specific failure points
3. **Create debug tools** for troubleshooting
4. **Document discoveries** as you learn

## Resources

### Official Documentation:
- BBC micro:bit Python API: https://microbit-micropython.readthedocs.io/
- Kitronik Air Quality Board: https://kitronik.co.uk/5674
- BME688 Datasheet: Bosch official documentation
- MCP7940-N RTC Datasheet: Microchip official documentation

### Community Resources:
- micro:bit Educational Foundation
- Kitronik Learning Resources
- MicroPython Community Forums

---

**Project Status**: ✅ **Hardware Communication Fixed**

**Next Phase**: Implement full sensor calibration and display functionality

**Success Metrics**: 
- RTC keeps accurate time ✅
- BME688 provides sensor readings ✅
- System runs reliably ✅
- Educational value for Albie ✅

*Last Updated: July 2025*
