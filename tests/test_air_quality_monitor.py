"""
Comprehensive Unit Tests for Air Quality Monitor

Run with: python -m pytest test_air_quality_monitor.py -v
Or: python -m unittest test_air_quality_monitor.py -v

These tests demonstrate:
1. Testing pure logic functions
2. Mocking hardware dependencies  
3. Integration testing with dependency injection
4. Edge case testing
5. Error handling testing
"""

import unittest
from unittest.mock import Mock, patch
from datetime import datetime
import sys
import os

# Import our testable classes
try:
    from test_strategy import (
        RTCLogic, SensorDataProcessor, DataLogger, DisplayFormatter,
        MockHardware, AirQualityMonitor
    )
except ImportError:
    print("Error: Could not import test_strategy module")
    print("Make sure test_strategy.py is in the same directory")
    sys.exit(1)


class TestRTCLogic(unittest.TestCase):
    """Test RTC logic functions"""
    
    def test_bcd_conversion(self):
        """Test BCD to integer conversion"""
        # Test normal cases
        self.assertEqual(RTCLogic.bcd_to_int(0x23), 23)
        self.assertEqual(RTCLogic.bcd_to_int(0x59), 59)
        self.assertEqual(RTCLogic.bcd_to_int(0x00), 0)
        
        # Test edge cases
        self.assertEqual(RTCLogic.bcd_to_int(0x99), 99)
    
    def test_int_to_bcd_conversion(self):
        """Test integer to BCD conversion"""
        # Test normal cases
        self.assertEqual(RTCLogic.int_to_bcd(23), 0x23)
        self.assertEqual(RTCLogic.int_to_bcd(59), 0x59)
        self.assertEqual(RTCLogic.int_to_bcd(0), 0x00)
        
        # Test edge cases
        self.assertEqual(RTCLogic.int_to_bcd(99), 0x99)
        
        # Test error cases
        with self.assertRaises(ValueError):
            RTCLogic.int_to_bcd(-1)
        with self.assertRaises(ValueError):
            RTCLogic.int_to_bcd(100)
    
    def test_bcd_round_trip(self):
        """Test that BCD conversion is reversible"""
        for i in range(0, 100):
            bcd = RTCLogic.int_to_bcd(i)
            back_to_int = RTCLogic.bcd_to_int(bcd)
            self.assertEqual(i, back_to_int, f"Round trip failed for {i}")
    
    def test_weekday_calculation(self):
        """Test weekday calculation"""
        # Test known dates
        # 1st January 2024 was a Monday (1)
        self.assertEqual(RTCLogic.calculate_weekday(2024, 1, 1), 1)
        
        # 4th July 2025 is a Friday (5)
        self.assertEqual(RTCLogic.calculate_weekday(2025, 7, 4), 5)
        
        # Test leap year: 29th February 2024 was a Thursday (4)
        self.assertEqual(RTCLogic.calculate_weekday(2024, 2, 29), 4)
    
    def test_time_validation(self):
        """Test time validation"""
        # Valid times
        self.assertTrue(RTCLogic.is_valid_time(2024, 12, 25, 10, 30, 45))
        self.assertTrue(RTCLogic.is_valid_time(2025, 1, 1, 0, 0, 0))
        
        # Invalid times
        self.assertFalse(RTCLogic.is_valid_time(2024, 13, 1, 10, 30, 45))  # Month > 12
        self.assertFalse(RTCLogic.is_valid_time(2024, 2, 30, 10, 30, 45))   # Feb 30th
        self.assertFalse(RTCLogic.is_valid_time(2024, 12, 25, 25, 30, 45))  # Hour > 23
        self.assertFalse(RTCLogic.is_valid_time(2024, 12, 25, 10, 60, 45))  # Minute > 59
    
    def test_time_needs_setting(self):
        """Test RTC time setting logic"""
        # Time needs setting - old year
        old_time = (2020, 1, 1, 12, 0, 0, 1)
        self.assertTrue(RTCLogic.time_needs_setting(old_time, 2025))
        
        # Time OK - current year
        current_time = (2025, 7, 4, 14, 30, 0, 5)
        self.assertFalse(RTCLogic.time_needs_setting(current_time, 2025))
        
        # Time needs setting - None
        self.assertTrue(RTCLogic.time_needs_setting(None, 2025))
        
        # Time needs setting - too far in future
        future_time = (2030, 1, 1, 12, 0, 0, 1)
        self.assertTrue(RTCLogic.time_needs_setting(future_time, 2025))


class TestSensorDataProcessor(unittest.TestCase):
    """Test sensor data processing functions"""
    
    def test_temperature_conversion(self):
        """Test temperature conversion"""
        # Test normal conversion
        self.assertEqual(SensorDataProcessor.convert_temperature(25000), 25.0)
        self.assertEqual(SensorDataProcessor.convert_temperature(30500), 30.5)
        
        # Test with calibration offset
        self.assertEqual(SensorDataProcessor.convert_temperature(25000, -1.5), 23.5)
        
        # Test negative temperatures
        self.assertEqual(SensorDataProcessor.convert_temperature(-5000), -5.0)
    
    def test_pressure_conversion(self):
        """Test pressure conversion"""
        self.assertEqual(SensorDataProcessor.convert_pressure(10132500), 101325.0)
        self.assertEqual(SensorDataProcessor.convert_pressure(100000), 1000.0)
    
    def test_humidity_conversion(self):
        """Test humidity conversion with clamping"""
        # Normal case
        self.assertEqual(SensorDataProcessor.convert_humidity(45000), 45.0)
        
        # Test clamping
        self.assertEqual(SensorDataProcessor.convert_humidity(-5000), 0.0)  # Clamp to 0
        self.assertEqual(SensorDataProcessor.convert_humidity(105000), 100.0)  # Clamp to 100
    
    def test_heat_index_calculation(self):
        """Test heat index calculation"""
        # Below threshold - should return original temperature
        self.assertEqual(SensorDataProcessor.calculate_heat_index(20.0, 50), 20.0)
        
        # Above threshold - should calculate heat index
        heat_index = SensorDataProcessor.calculate_heat_index(35.0, 80)
        self.assertGreater(heat_index, 35.0)  # Should feel hotter
        self.assertIsInstance(heat_index, float)
    
    def test_air_quality_descriptions(self):
        """Test air quality description mapping"""
        self.assertEqual(SensorDataProcessor.air_quality_description(25), "Excellent")
        self.assertEqual(SensorDataProcessor.air_quality_description(75), "Good")
        self.assertEqual(SensorDataProcessor.air_quality_description(125), "Lightly Polluted")
        self.assertEqual(SensorDataProcessor.air_quality_description(175), "Moderately Polluted")
        self.assertEqual(SensorDataProcessor.air_quality_description(250), "Heavily Polluted")
        self.assertEqual(SensorDataProcessor.air_quality_description(400), "Severely Polluted")


class TestDataLogger(unittest.TestCase):
    """Test data logging functionality"""
    
    def setUp(self):
        """Set up test data logger"""
        self.logger = DataLogger()
    
    def test_add_reading(self):
        """Test adding sensor readings"""
        timestamp = (2025, 7, 4, 14, 30, 0, 5)
        reading = self.logger.add_reading(timestamp, 25.5, 45.0, 101325.0, 75)
        
        self.assertEqual(len(self.logger.data), 1)
        self.assertEqual(reading['temperature'], 25.5)
        self.assertEqual(reading['timestamp'], timestamp)
    
    def test_get_recent_readings(self):
        """Test getting recent readings"""
        # Add multiple readings
        for i in range(20):
            timestamp = (2025, 7, 4, 14, i, 0, 5)
            self.logger.add_reading(timestamp, 25.0 + i, 45.0, 101325.0, 75)
        
        # Test getting recent readings
        recent = self.logger.get_recent_readings(5)
        self.assertEqual(len(recent), 5)
        self.assertEqual(recent[-1]['temperature'], 44.0)  # Last reading
        
        # Test when requesting more than available
        recent_all = self.logger.get_recent_readings(100)
        self.assertEqual(len(recent_all), 20)
    
    def test_calculate_average_temperature(self):
        """Test temperature averaging"""
        # Test with no data
        self.assertIsNone(self.logger.calculate_average_temperature())
        
        # Add test data
        temperatures = [20.0, 22.0, 24.0, 26.0, 28.0]
        for i, temp in enumerate(temperatures):
            timestamp = (2025, 7, 4, 14, i, 0, 5)
            self.logger.add_reading(timestamp, temp, 45.0, 101325.0, 75)
        
        # Test average calculation
        avg = self.logger.calculate_average_temperature(5)
        expected_avg = sum(temperatures) / len(temperatures)
        self.assertEqual(avg, round(expected_avg, 1))
    
    def test_air_quality_trend_detection(self):
        """Test air quality trend detection"""
        # Test insufficient data
        self.assertEqual(self.logger.detect_air_quality_trend(), "insufficient_data")
        
        # Test stable trend
        for i in range(3):
            timestamp = (2025, 7, 4, 14, i, 0, 5)
            self.logger.add_reading(timestamp, 25.0, 45.0, 101325.0, 75)
        
        self.assertEqual(self.logger.detect_air_quality_trend(), "stable")
        
        # Reset and test worsening trend
        self.logger.data = []
        air_qualities = [50, 60, 70]  # Worsening (increasing)
        for i, aq in enumerate(air_qualities):
            timestamp = (2025, 7, 4, 14, i, 0, 5)
            self.logger.add_reading(timestamp, 25.0, 45.0, 101325.0, aq)
        
        self.assertEqual(self.logger.detect_air_quality_trend(), "worsening")
        
        # Reset and test improving trend
        self.logger.data = []
        air_qualities = [100, 80, 60]  # Improving (decreasing)
        for i, aq in enumerate(air_qualities):
            timestamp = (2025, 7, 4, 14, i, 0, 5)
            self.logger.add_reading(timestamp, 25.0, 45.0, 101325.0, aq)
        
        self.assertEqual(self.logger.detect_air_quality_trend(), "improving")


class TestDisplayFormatter(unittest.TestCase):
    """Test display formatting functions"""
    
    def test_time_formatting(self):
        """Test time display formatting"""
        self.assertEqual(DisplayFormatter.format_time_display(9, 5), "09:05")
        self.assertEqual(DisplayFormatter.format_time_display(14, 30), "14:30")
        self.assertEqual(DisplayFormatter.format_time_display(0, 0), "00:00")
    
    def test_date_formatting(self):
        """Test date display formatting"""
        # Without year
        self.assertEqual(DisplayFormatter.format_date_display(4, 7), "04/07")
        
        # With year
        self.assertEqual(DisplayFormatter.format_date_display(4, 7, 2025), "04/07/2025")
    
    def test_temperature_formatting(self):
        """Test temperature formatting"""
        # Celsius (default)
        self.assertEqual(DisplayFormatter.format_temperature(25.5), "25.5°C")
        
        # Fahrenheit
        self.assertEqual(DisplayFormatter.format_temperature(25.0, 'F'), "77.0°F")
        
        # Test case insensitive
        self.assertEqual(DisplayFormatter.format_temperature(0, 'f'), "32.0°F")
    
    def test_pressure_formatting(self):
        """Test pressure formatting"""
        # Pascals
        self.assertEqual(DisplayFormatter.format_pressure(999), "999Pa")
        
        # Kilopascals
        self.assertEqual(DisplayFormatter.format_pressure(101325), "101.3kPa")
    
    def test_text_truncation(self):
        """Test text truncation for display"""
        # Text within limit
        self.assertEqual(DisplayFormatter.truncate_for_display("Hello", 10), "Hello")
        
        # Text exactly at limit
        self.assertEqual(DisplayFormatter.truncate_for_display("Hello World!", 12), "Hello World!")
        
        # Text over limit
        self.assertEqual(DisplayFormatter.truncate_for_display("Hello World!", 10), "Hello W...")


class TestAirQualityMonitorIntegration(unittest.TestCase):
    """Integration tests using mock hardware"""
    
    def setUp(self):
        """Set up test environment"""
        self.mock_hardware = MockHardware()
        self.monitor = AirQualityMonitor(self.mock_hardware)
    
    def test_rtc_setup_when_needed(self):
        """Test RTC setup when time is invalid"""
        # Set RTC to old time
        self.mock_hardware.rtc_time = (2020, 1, 1, 12, 0, 0, 1)
        
        # Setup should update RTC
        test_time = datetime(2025, 7, 4, 14, 30, 0)
        updated = self.monitor.setup_rtc_if_needed(test_time)
        
        self.assertTrue(updated)
        self.assertEqual(self.mock_hardware.rtc_time[0], 2025)  # Year updated
    
    def test_rtc_setup_when_not_needed(self):
        """Test RTC setup when time is already correct"""
        # Set RTC to current time
        self.mock_hardware.rtc_time = (2025, 7, 4, 14, 30, 0, 5)
        
        # Setup should not update RTC
        test_time = datetime(2025, 7, 4, 14, 30, 0)
        updated = self.monitor.setup_rtc_if_needed(test_time)
        
        self.assertFalse(updated)
    
    def test_sensor_reading_and_logging(self):
        """Test taking and logging sensor readings"""
        # Set up mock data
        self.mock_hardware.sensor_data = {
            'temperature': 25500,  # 25.5°C after conversion
            'humidity': 45000,     # 45% after conversion
            'pressure': 10132500,  # 101325 Pa after conversion
            'air_quality': 75
        }
        self.mock_hardware.rtc_time = (2025, 7, 4, 14, 30, 0, 5)
        
        # Take reading
        reading = self.monitor.take_reading()
        
        # Verify reading was processed correctly
        self.assertIsNotNone(reading)
        self.assertEqual(reading['temperature'], 25.5)
        self.assertEqual(reading['humidity'], 45.0)
        self.assertEqual(reading['pressure'], 101325.0)
        self.assertEqual(reading['air_quality'], 75)
        
        # Verify it was logged
        self.assertEqual(len(self.monitor.data_logger.data), 1)
    
    def test_display_update(self):
        """Test display update functionality"""
        # First take a reading to have data
        self.monitor.take_reading()
        
        # Update display
        self.monitor.update_display()
        
        # Verify display was updated
        self.assertEqual(len(self.mock_hardware.display_content), 4)
        self.assertIn("T:", self.mock_hardware.display_content[0])
        self.assertIn("H:", self.mock_hardware.display_content[1])
        self.assertIn("AQ:", self.mock_hardware.display_content[3])
    
    def test_error_handling(self):
        """Test error handling with I2C failures"""
        # Enable I2C errors
        self.mock_hardware.i2c_errors = True
        
        # RTC setup should fail gracefully
        updated = self.monitor.setup_rtc_if_needed()
        self.assertFalse(updated)
        
        # Sensor reading should fail gracefully
        reading = self.monitor.take_reading()
        self.assertIsNone(reading)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""
    
    def test_leap_year_handling(self):
        """Test leap year date validation"""
        # Valid leap year date
        self.assertTrue(RTCLogic.is_valid_time(2024, 2, 29, 12, 0, 0))
        
        # Invalid leap year date
        self.assertFalse(RTCLogic.is_valid_time(2023, 2, 29, 12, 0, 0))
    
    def test_extreme_sensor_values(self):
        """Test handling of extreme sensor values"""
        # Extreme temperature
        temp = SensorDataProcessor.convert_temperature(100000)  # 100°C
        self.assertEqual(temp, 100.0)
        
        # Extreme humidity (should be clamped)
        humidity = SensorDataProcessor.convert_humidity(150000)  # 150%
        self.assertEqual(humidity, 100.0)  # Clamped to 100%
        
        # Very low humidity (should be clamped)
        humidity_low = SensorDataProcessor.convert_humidity(-10000)  # -10%
        self.assertEqual(humidity_low, 0.0)  # Clamped to 0%
    
    def test_year_2038_problem(self):
        """Test dates beyond 2038 (32-bit timestamp limit)"""
        # Should handle dates well beyond 2038
        weekday = RTCLogic.calculate_weekday(2050, 1, 1)
        self.assertIn(weekday, range(1, 8))  # Valid weekday


def run_all_tests():
    """Run all tests with detailed output"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestRTCLogic,
        TestSensorDataProcessor, 
        TestDataLogger,
        TestDisplayFormatter,
        TestAirQualityMonitorIntegration,
        TestEdgeCases
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {(result.testsRun - len(result.failures) - len(result.errors))/result.testsRun*100:.1f}%")
    
    if result.failures:
        print(f"\nFailures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split(chr(10))[-2]}")
    
    if result.errors:
        print(f"\nErrors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split(chr(10))[-2]}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    print("Running Air Quality Monitor Unit Tests")
    print("=" * 50)
    
    success = run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! Your code is ready for the micro:bit.")
    else:
        print("\n❌ Some tests failed. Please review the issues above.")
        sys.exit(1)
