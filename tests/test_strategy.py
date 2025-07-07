"""
Testing Strategy for Kitronik Air Quality Board Project

This demonstrates how to build testable micro:bit code by separating
pure logic from hardware dependencies.

Key Principles:
1. Separate business logic from hardware I/O
2. Use dependency injection for hardware components
3. Test pure functions with standard Python unittest
4. Mock hardware interactions for integration tests
5. Keep micro:bit code simple and tested logic complex
"""

import unittest
from unittest.mock import Mock, patch
from datetime import datetime, date
import sys
import os

# Add src directory to Python path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

class RTCLogic:
    """Pure logic for RTC operations - no hardware dependencies"""
    
    @staticmethod
    def bcd_to_int(bcd_value):
        """Convert BCD (Binary Coded Decimal) to integer"""
        return (bcd_value >> 4) * 10 + (bcd_value & 0x0F)
    
    @staticmethod
    def int_to_bcd(int_value):
        """Convert integer to BCD format"""
        if int_value < 0 or int_value > 99:
            raise ValueError("Value must be between 0 and 99")
        return ((int_value // 10) << 4) | (int_value % 10)
    
    @staticmethod
    def calculate_weekday(year, month, day):
        """Calculate day of week (1=Monday, 7=Sunday)"""
        # Zeller's congruence algorithm
        if month < 3:
            month += 12
            year -= 1
        
        # Zeller's congruence returns 0=Saturday, 1=Sunday, 2=Monday...
        zeller_result = (day + (13 * (month + 1)) // 5 + year + 
                        year // 4 - year // 100 + year // 400) % 7
        
        # Convert to ISO format: 1=Monday, 2=Tuesday..., 7=Sunday
        return ((zeller_result + 5) % 7) + 1
    
    @staticmethod
    def is_valid_time(year, month, day, hour, minute, second):
        """Validate time components"""
        try:
            datetime(year, month, day, hour, minute, second)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def time_needs_setting(rtc_time, current_year=None):
        """Determine if RTC time needs updating"""
        if rtc_time is None:
            return True
        
        year = rtc_time[0] if isinstance(rtc_time, tuple) else rtc_time.get('year')
        current_year = current_year or datetime.now().year
        
        # If RTC year is before 2024 or more than 1 year in future, needs setting
        return year < 2024 or year > current_year + 1

class SensorDataProcessor:
    """Pure logic for processing sensor data"""
    
    @staticmethod
    def convert_temperature(raw_temp, calibration_offset=0):
        """Convert raw temperature reading to Celsius"""
        # Simplified conversion - real BME688 requires complex calibration
        celsius = (raw_temp / 1000.0) + calibration_offset
        return round(celsius, 1)
    
    @staticmethod
    def convert_pressure(raw_pressure):
        """Convert raw pressure to Pascals"""
        return raw_pressure / 100.0
    
    @staticmethod
    def convert_humidity(raw_humidity):
        """Convert raw humidity to percentage"""
        humidity = raw_humidity / 1000.0
        return max(0, min(100, humidity))  # Clamp to 0-100%
    
    @staticmethod
    def calculate_heat_index(temp_celsius, humidity_percent):
        """Calculate heat index (feels-like temperature)"""
        if temp_celsius < 27:  # Heat index only meaningful above 27°C
            return temp_celsius
        
        # Convert to Fahrenheit for calculation
        temp_f = (temp_celsius * 9/5) + 32
        
        # Rothfusz equation (simplified)
        hi = (0.5 * (temp_f + 61.0 + ((temp_f - 68.0) * 1.2) + 
                    (humidity_percent * 0.094)))
        
        # Convert back to Celsius
        return round((hi - 32) * 5/9, 1)
    
    @staticmethod
    def air_quality_description(iaq_score):
        """Convert IAQ score to human-readable description"""
        if iaq_score <= 50:
            return "Excellent"
        elif iaq_score <= 100:
            return "Good"
        elif iaq_score <= 150:
            return "Lightly Polluted"
        elif iaq_score <= 200:
            return "Moderately Polluted"
        elif iaq_score <= 300:
            return "Heavily Polluted"
        else:
            return "Severely Polluted"

class DataLogger:
    """Pure logic for data logging and analysis"""
    
    def __init__(self):
        self.data = []
    
    def add_reading(self, timestamp, temperature, humidity, pressure, air_quality):
        """Add a sensor reading"""
        reading = {
            'timestamp': timestamp,
            'temperature': temperature,
            'humidity': humidity,
            'pressure': pressure,
            'air_quality': air_quality
        }
        self.data.append(reading)
        return reading
    
    def get_recent_readings(self, count=10):
        """Get the most recent N readings"""
        return self.data[-count:] if self.data else []
    
    def calculate_average_temperature(self, hours=24):
        """Calculate average temperature over specified hours"""
        if not self.data:
            return None
        
        # For testing, just use last N readings as proxy for time period
        recent = self.get_recent_readings(hours)
        temps = [r['temperature'] for r in recent]
        return round(sum(temps) / len(temps), 1) if temps else None
    
    def detect_air_quality_trend(self):
        """Detect if air quality is improving, worsening, or stable"""
        if len(self.data) < 3:
            return "insufficient_data"
        
        recent_readings = self.data[-3:]
        air_qualities = [r['air_quality'] for r in recent_readings]
        
        if air_qualities[-1] > air_qualities[0] + 10:
            return "worsening"
        elif air_qualities[-1] < air_qualities[0] - 10:
            return "improving"
        else:
            return "stable"

class DisplayFormatter:
    """Pure logic for formatting display output"""
    
    @staticmethod
    def format_time_display(hour, minute):
        """Format time for display"""
        return f"{hour:02d}:{minute:02d}"
    
    @staticmethod
    def format_date_display(day, month, year=None):
        """Format date for display"""
        if year:
            return f"{day:02d}/{month:02d}/{year}"
        return f"{day:02d}/{month:02d}"
    
    @staticmethod
    def format_temperature(temp_celsius, unit='C'):
        """Format temperature for display"""
        if unit.upper() == 'F':
            temp_f = (temp_celsius * 9/5) + 32
            return f"{temp_f:.1f}°F"
        return f"{temp_celsius:.1f}°C"
    
    @staticmethod
    def format_pressure(pressure_pa):
        """Format pressure for display"""
        if pressure_pa > 1000:
            return f"{pressure_pa/1000:.1f}kPa"
        return f"{pressure_pa:.0f}Pa"
    
    @staticmethod
    def truncate_for_display(text, max_length=16):
        """Truncate text to fit display width"""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."


# Example of hardware abstraction for testability
class HardwareInterface:
    """Abstract interface for hardware components"""
    
    def read_rtc(self):
        """Read current time from RTC"""
        raise NotImplementedError
    
    def write_rtc(self, year, month, day, hour, minute, second):
        """Write time to RTC"""
        raise NotImplementedError
    
    def read_sensor(self):
        """Read sensor data"""
        raise NotImplementedError
    
    def write_display(self, text, line=0):
        """Write text to display"""
        raise NotImplementedError

class MockHardware(HardwareInterface):
    """Mock hardware for testing"""
    
    def __init__(self):
        self.rtc_time = None
        self.sensor_data = {
            'temperature': 25.0,
            'humidity': 45.0,
            'pressure': 101325.0,
            'air_quality': 75
        }
        self.display_content = []
        self.i2c_errors = False
    
    def read_rtc(self):
        if self.i2c_errors:
            raise Exception("I2C communication error")
        return self.rtc_time
    
    def write_rtc(self, year, month, day, hour, minute, second):
        if self.i2c_errors:
            raise Exception("I2C communication error")
        self.rtc_time = (year, month, day, hour, minute, second, 1)
    
    def read_sensor(self):
        if self.i2c_errors:
            raise Exception("Sensor communication error")
        return self.sensor_data.copy()
    
    def write_display(self, text, line=0):
        if len(self.display_content) <= line:
            self.display_content.extend([''] * (line + 1 - len(self.display_content)))
        self.display_content[line] = text

# Main application class that uses dependency injection
class AirQualityMonitor:
    """Main application class - testable via dependency injection"""
    
    def __init__(self, hardware_interface):
        self.hardware = hardware_interface
        self.data_logger = DataLogger()
        self.rtc_logic = RTCLogic()
        self.sensor_processor = SensorDataProcessor()
        self.display_formatter = DisplayFormatter()
    
    def setup_rtc_if_needed(self, current_time=None):
        """Set up RTC with current time if needed"""
        if current_time is None:
            current_time = datetime.now()
        
        try:
            rtc_time = self.hardware.read_rtc()
            
            if self.rtc_logic.time_needs_setting(rtc_time, current_time.year):
                self.hardware.write_rtc(
                    current_time.year, current_time.month, current_time.day,
                    current_time.hour, current_time.minute, current_time.second
                )
                return True  # RTC was updated
            return False  # RTC was already correct
            
        except Exception as e:
            print(f"RTC setup failed: {e}")
            return False
    
    def take_reading(self):
        """Take a sensor reading and log it"""
        try:
            raw_data = self.hardware.read_sensor()
            rtc_time = self.hardware.read_rtc()
            
            # Process the raw data
            temperature = self.sensor_processor.convert_temperature(raw_data['temperature'])
            humidity = self.sensor_processor.convert_humidity(raw_data['humidity'])
            pressure = self.sensor_processor.convert_pressure(raw_data['pressure'])
            air_quality = raw_data['air_quality']
            
            # Log the reading
            reading = self.data_logger.add_reading(
                rtc_time, temperature, humidity, pressure, air_quality
            )
            
            return reading
            
        except Exception as e:
            print(f"Reading failed: {e}")
            return None
    
    def update_display(self):
        """Update the display with current readings"""
        recent_reading = self.data_logger.get_recent_readings(1)
        if not recent_reading:
            self.hardware.write_display("No data", 0)
            return
        
        reading = recent_reading[0]
        
        # Format display lines
        temp_text = self.display_formatter.format_temperature(reading['temperature'])
        humidity_text = f"H: {reading['humidity']:.1f}%"
        pressure_text = self.display_formatter.format_pressure(reading['pressure'])
        air_quality_text = f"AQ: {self.sensor_processor.air_quality_description(reading['air_quality'])}"
        
        # Write to display
        self.hardware.write_display(f"T: {temp_text}", 0)
        self.hardware.write_display(humidity_text, 1)
        self.hardware.write_display(pressure_text, 2)
        self.hardware.write_display(air_quality_text, 3)



