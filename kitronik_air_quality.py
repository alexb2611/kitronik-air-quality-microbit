
"""
MicroPython driver for the Kitronik Air Quality and Environmental Board.

This module provides a high-level interface to the hardware components
on the Kitronik board, including the BME688 sensor, the RTC, and the
OLED display.

It is designed to be used with the BBC micro:bit.
"""

from microbit import i2c, sleep
import os

# BME688 I2C address
BME688_I2C_ADDR = 0x77

# RTC I2C address
RTC_I2C_ADDR = 0x6F

# OLED I2C address
OLED_I2C_ADDR = 0x3C

class KitronikAirQualityBoard:
    """A class to represent the Kitronik Air Quality Board."""

    def __init__(self):
        """Initialise the hardware components.""" 
        # Check for BME688
        if BME688_I2C_ADDR not in i2c.scan():
            raise RuntimeError("BME688 not found on I2C bus.")

        # Check for RTC
        if RTC_I2C_ADDR not in i2c.scan():
            raise RuntimeError("RTC not found on I2C bus.")

        # Check for OLED
        if OLED_I2C_ADDR not in i2c.scan():
            raise RuntimeError("OLED not found on I2C bus.")

        # Initialise the BME688 sensor (simplified - actual driver needed for real data)
        self._bme688_init()

        # Initialise the OLED display (simplified - actual driver needed for real display)
        self._oled_init()

    def _bme688_init(self):
        """Initialise the BME688 sensor (simplified)."""
        # In a real scenario, this would involve reading calibration data and setting modes.
        # For now, we just ensure basic I2C communication doesn't fail.
        try:
            # Attempt a dummy write to check I2C bus response
            i2c.write(BME688_I2C_ADDR, b'\x00\x00') # Write to a dummy register
            sleep(10) # Give sensor time to respond
        except OSError:
            raise RuntimeError("Failed to communicate with BME688 during init.")

    def _oled_init(self):
        """Initialise the OLED display (simplified)."""
        # A full SSD1306 driver is complex. For now, we just ensure basic I2C communication.
        try:
            # Attempt a dummy write to check I2C bus response
            i2c.write(OLED_I2C_ADDR, b'\x00\x00') # Write to a dummy command register
            sleep(10) # Give display time to respond
            print("OLED Init: Attempted basic I2C communication.")
        except OSError:
            raise RuntimeError("Failed to communicate with OLED during init.")

    def read_sensor(self):
        """Read the sensor data from the BME688 (returns dummy data for now)."""
        # A real BME688 driver would involve complex register reads and calculations.
        # For testing the main script flow, we return plausible dummy values.
        try:
            # Attempt a dummy read to check I2C bus response
            i2c.read(BME688_I2C_ADDR, 1) # Read 1 byte from a dummy register
            sleep(10) # Simulate sensor reading time

            return {
                'temperature': 25000,  # 25.0 C
                'pressure': 10132500,  # 1013.25 hPa
                'humidity': 50000,     # 50.0 %
                'air_quality': 75      # Dummy IAQ
            }
        except OSError:
            print("Sensor read failed (I2C error). Returning None.")
            return None

    def _bcd_to_int(self, bcd_value):
        """Convert BCD to integer."""
        return (bcd_value >> 4) * 10 + (bcd_value & 0x0F)

    def _int_to_bcd(self, int_value):
        """Convert integer to BCD."""
        return ((int_value // 10) << 4) | (int_value % 10)

    def read_rtc(self):
        """Read the time from the RTC (PCF8523 compatible)."""
        try:
            # Set register pointer to 0x00 (seconds register)
            i2c.write(RTC_I2C_ADDR, b'\x00')
            # Read 7 bytes (seconds, minutes, hours, weekday, day, month, year)
            data = i2c.read(RTC_I2C_ADDR, 7)
            
            second = self._bcd_to_int(data[0] & 0x7F) # Mask out CH bit
            minute = self._bcd_to_int(data[1] & 0x7F) # Mask out unused bit
            hour = self._bcd_to_int(data[2] & 0x3F)   # Mask out 12/24 hour mode bit
            weekday = self._bcd_to_int(data[3] & 0x07) # Mask out unused bits
            day = self._bcd_to_int(data[4] & 0x3F)    # Mask out unused bits
            month = self._bcd_to_int(data[5] & 0x1F)  # Mask out unused bits
            year = self._bcd_to_int(data[6])

            # PCF8523 year is 0-99, assuming 2000+ for now
            return (2000 + year, month, day, hour, minute, second, weekday)
        except OSError:
            print("RTC read failed (I2C error). Returning None.")
            return None

    def write_rtc(self, year, month, day, hour, minute, second):
        """Write the time to the RTC (PCF8523 compatible)."""
        try:
            # PCF8523 registers start at 0x00 for seconds
            # Data order: seconds, minutes, hours, weekday, day, month, year
            # Control registers (0x07-0x09) are not set here, assuming default.
            
            # Convert to BCD
            bcd_second = self._int_to_bcd(second)
            bcd_minute = self._int_to_bcd(minute)
            bcd_hour = self._int_to_bcd(hour)
            # Weekday is often 1-7, but PCF8523 uses 0-6. We'll just write a dummy 0 for now.
            bcd_weekday = 0 # self._int_to_bcd(weekday % 7) if weekday is not None else 0
            bcd_day = self._int_to_bcd(day)
            bcd_month = self._int_to_bcd(month)
            bcd_year = self._int_to_bcd(year % 100) # Only last two digits of year

            # Write to register 0x00 (seconds) and subsequent registers
            i2c.write(RTC_I2C_ADDR, bytearray([
                0x00, # Start writing from register 0x00
                bcd_second, 
                bcd_minute, 
                bcd_hour, 
                bcd_weekday, 
                bcd_day, 
                bcd_month, 
                bcd_year
            ]))
            print("RTC write attempted.")
        except OSError:
            print("RTC write failed (I2C error).")
            pass

    def write_display(self, text, line=0):
        """Write text to the OLED display (prints to serial for now)."""
        # A full SSD1306 driver is complex and requires font data.
        # For now, we just print to serial to avoid freezing and show intent.
        print("OLED Display (line {}): {}".format(line, text))
        # try:
        #     # Placeholder for actual OLED commands (DO NOT USE AS IS)
        #     # This would involve setting cursor, sending data bytes, etc.
        #     i2c.write(OLED_I2C_ADDR, b'\x40' + text.encode('utf-8')) # Example: data mode + text
        # except OSError:
        #     print("OLED write failed (I2C error).")
        #     pass

    def clear_display(self):
        """Clear the OLED display (prints to serial for now)."""
        print("OLED Display: Clear screen requested.")
        # try:
        #     # Placeholder for actual OLED clear commands (DO NOT USE AS IS)
        #     i2c.write(OLED_I2C_ADDR, b'\x00\xAE') # Example: Display OFF command
        # except OSError:
        #     print("OLED clear failed (I2C error).")
        #     pass
