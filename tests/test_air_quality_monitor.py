"""
Comprehensive Unit Tests for Air Quality Monitor using pytest.

Run with: pytest -v

These tests demonstrate:
1. Testing pure logic functions with pytest assertions.
2. Mocking hardware dependencies with pytest fixtures and pytest-mock.
3. Integration testing with dependency injection.
4. Edge case and parameterized testing.
5. Error handling testing.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock
import sys
import os

# Import our testable classes from the strategy file
from test_strategy import (
    RTCLogic, SensorDataProcessor, DataLogger, DisplayFormatter,
    MockHardware, AirQualityMonitor
)

# Pytest Fixture for Mock Hardware
@pytest.fixture
def mock_hardware():
    """Provides a fresh MockHardware instance for each test."""
    return MockHardware()

@pytest.fixture
def monitor(mock_hardware):
    """Provides an AirQualityMonitor instance with a mock hardware interface."""
    return AirQualityMonitor(mock_hardware)

# 1. Tests for RTCLogic
class TestRTCLogic:
    """Test RTC logic functions using pytest features."""

    @pytest.mark.parametrize("bcd, expected_int", [
        (0x23, 23),
        (0x59, 59),
        (0x00, 0),
        (0x99, 99)
    ])
    def test_bcd_to_int_conversion(self, bcd, expected_int):
        """Test BCD to integer conversion with various inputs."""
        assert RTCLogic.bcd_to_int(bcd) == expected_int

    @pytest.mark.parametrize("integer, expected_bcd", [
        (23, 0x23),
        (59, 0x59),
        (0, 0x00),
        (99, 0x99)
    ])
    def test_int_to_bcd_conversion(self, integer, expected_bcd):
        """Test integer to BCD conversion."""
        assert RTCLogic.int_to_bcd(integer) == expected_bcd

    def test_int_to_bcd_out_of_range(self):
        """Test that BCD conversion raises ValueError for out-of-range inputs."""
        with pytest.raises(ValueError):
            RTCLogic.int_to_bcd(-1)
        with pytest.raises(ValueError):
            RTCLogic.int_to_bcd(100)

    def test_bcd_round_trip(self):
        """Test that BCD conversion is reversible for all valid inputs."""
        for i in range(100):
            bcd = RTCLogic.int_to_bcd(i)
            back_to_int = RTCLogic.bcd_to_int(bcd)
            assert i == back_to_int, f"Round trip failed for {i}"

    @pytest.mark.parametrize("year, month, day, expected_weekday", [
        (2024, 1, 1, 1),   # Monday
        (2025, 7, 4, 5),   # Friday
        (2024, 2, 29, 4),  # Leap day, Thursday
    ])
    def test_weekday_calculation(self, year, month, day, expected_weekday):
        """Test weekday calculation for known dates."""
        assert RTCLogic.calculate_weekday(year, month, day) == expected_weekday

    @pytest.mark.parametrize("time_tuple, expected_validity", [
        ((2024, 12, 25, 10, 30, 45), True),
        ((2025, 1, 1, 0, 0, 0), True),
        ((2024, 13, 1, 10, 30, 45), False),  # Invalid month
        ((2024, 2, 30, 10, 30, 45), False),   # Invalid day
        ((2023, 2, 29, 10, 30, 45), False),  # Invalid leap day
        ((2024, 12, 25, 25, 30, 45), False),  # Invalid hour
        ((2024, 12, 25, 10, 60, 45), False),  # Invalid minute
    ])
    def test_time_validation(self, time_tuple, expected_validity):
        """Test time validation for various valid and invalid times."""
        assert RTCLogic.is_valid_time(*time_tuple) == expected_validity

    @pytest.mark.parametrize("rtc_time, current_year, needs_setting", [
        ((2020, 1, 1, 12, 0, 0, 1), 2025, True),   # Old year
        ((2025, 7, 4, 14, 30, 0, 5), 2025, False), # Current year
        (None, 2025, True),                        # No time set
        ((2030, 1, 1, 12, 0, 0, 1), 2025, True),   # Future year
    ])
    def test_time_needs_setting(self, rtc_time, current_year, needs_setting):
        """Test logic for determining if the RTC needs to be set."""
        assert RTCLogic.time_needs_setting(rtc_time, current_year) == needs_setting

# 2. Tests for SensorDataProcessor
class TestSensorDataProcessor:
    """Test sensor data processing functions."""

    def test_temperature_conversion(self):
        """Test temperature conversion with and without calibration."""
        assert SensorDataProcessor.convert_temperature(25000) == 25.0
        assert SensorDataProcessor.convert_temperature(25000, -1.5) == 23.5
        assert SensorDataProcessor.convert_temperature(-5000) == -5.0

    def test_pressure_conversion(self):
        """Test pressure conversion."""
        assert SensorDataProcessor.convert_pressure(10132500) == 101325.0

    @pytest.mark.parametrize("raw_humidity, expected_humidity", [
        (45000, 45.0),
        (-5000, 0.0),    # Clamped to 0
        (105000, 100.0)  # Clamped to 100
    ])
    def test_humidity_conversion_with_clamping(self, raw_humidity, expected_humidity):
        """Test humidity conversion, including clamping at boundaries."""
        assert SensorDataProcessor.convert_humidity(raw_humidity) == expected_humidity

    def test_heat_index_calculation(self):
        """Test heat index calculation logic."""
        # Below threshold, should return original temperature
        assert SensorDataProcessor.calculate_heat_index(20.0, 50) == 20.0
        # Above threshold, should be higher
        assert SensorDataProcessor.calculate_heat_index(35.0, 80) > 35.0

    @pytest.mark.parametrize("score, description", [
        (25, "Excellent"),
        (75, "Good"),
        (125, "Lightly Polluted"),
        (175, "Moderately Polluted"),
        (250, "Heavily Polluted"),
        (400, "Severely Polluted")
    ])
    def test_air_quality_descriptions(self, score, description):
        """Test mapping of IAQ score to human-readable descriptions."""
        assert SensorDataProcessor.air_quality_description(score) == description

# 3. Tests for DataLogger
class TestDataLogger:
    """Test data logging and analysis functionality."""

    @pytest.fixture
    def logger(self):
        """Provides a fresh DataLogger instance for each test."""
        return DataLogger()

    def test_add_reading(self, logger):
        """Test that a reading can be added to the logger."""
        timestamp = (2025, 7, 4, 14, 30, 0, 5)
        reading = logger.add_reading(timestamp, 25.5, 45.0, 101325.0, 75)
        assert len(logger.data) == 1
        assert reading['temperature'] == 25.5

    def test_get_recent_readings(self, logger):
        """Test retrieving a subset of recent readings."""
        for i in range(20):
            logger.add_reading((2025, 7, 4, 14, i, 0, 5), 25.0 + i, 45.0, 101325.0, 75)
        
        recent = logger.get_recent_readings(5)
        assert len(recent) == 5
        assert recent[-1]['temperature'] == 44.0  # 25.0 + 19

    def test_calculate_average_temperature(self, logger):
        """Test temperature averaging."""
        assert logger.calculate_average_temperature() is None  # No data
        
        temperatures = [20.0, 22.0, 24.0, 26.0, 28.0]
        for i, temp in enumerate(temperatures):
            logger.add_reading((2025, 7, 4, 14, i, 0, 5), temp, 45.0, 101325.0, 75)
        
        expected_avg = sum(temperatures) / len(temperatures)
        assert logger.calculate_average_temperature(5) == round(expected_avg, 1)

    @pytest.mark.parametrize("air_qualities, expected_trend", [
        ([], "insufficient_data"),
        ([75, 76, 77], "stable"),
        ([50, 60, 71], "worsening"),
        ([100, 80, 60], "improving")
    ])
    def test_air_quality_trend_detection(self, logger, air_qualities, expected_trend):
        """Test air quality trend detection logic."""
        for i, aq in enumerate(air_qualities):
            logger.add_reading((2025, 7, 4, 14, i, 0, 5), 25.0, 45.0, 101325.0, aq)
        
        assert logger.detect_air_quality_trend() == expected_trend

# 4. Tests for DisplayFormatter
class TestDisplayFormatter:
    """Test display formatting functions."""

    def test_format_time_display(self):
        assert DisplayFormatter.format_time_display(9, 5) == "09:05"
        assert DisplayFormatter.format_time_display(14, 30) == "14:30"

    def test_format_date_display(self):
        assert DisplayFormatter.format_date_display(4, 7) == "04/07"
        assert DisplayFormatter.format_date_display(4, 7, 2025) == "04/07/2025"

    def test_format_temperature(self):
        assert DisplayFormatter.format_temperature(25.5) == "25.5°C"
        assert DisplayFormatter.format_temperature(25.0, 'F') == "77.0°F"

    def test_format_pressure(self):
        assert DisplayFormatter.format_pressure(999) == "999Pa"
        assert DisplayFormatter.format_pressure(101325) == "101.3kPa"

    def test_truncate_for_display(self):
        assert DisplayFormatter.truncate_for_display("Hello", 10) == "Hello"
        assert DisplayFormatter.truncate_for_display("Hello World!", 10) == "Hello W..."

# 5. Integration Tests for AirQualityMonitor
@pytest.mark.integration
class TestAirQualityMonitorIntegration:
    """Integration tests using a mock hardware fixture."""

    def test_rtc_setup_when_needed(self, monitor, mock_hardware):
        """Test that the RTC is set up correctly when its time is invalid."""
        mock_hardware.rtc_time = (2020, 1, 1, 12, 0, 0, 1)  # Old time
        test_time = datetime(2025, 7, 4, 14, 30, 0)
        
        updated = monitor.setup_rtc_if_needed(test_time)
        
        assert updated is True
        assert mock_hardware.rtc_time[0] == 2025  # Year updated

    def test_rtc_setup_when_not_needed(self, monitor, mock_hardware):
        """Test that the RTC is not re-set when its time is already valid."""
        mock_hardware.rtc_time = (2025, 7, 4, 14, 30, 0, 5)
        test_time = datetime(2025, 7, 4, 14, 30, 0)
        
        updated = monitor.setup_rtc_if_needed(test_time)
        
        assert updated is False

    def test_sensor_reading_and_logging(self, monitor, mock_hardware):
        """Test the full workflow of taking and logging a sensor reading."""
        mock_hardware.sensor_data = {
            'temperature': 25500, 'humidity': 45000,
            'pressure': 10132500, 'air_quality': 75
        }
        mock_hardware.rtc_time = (2025, 7, 4, 14, 30, 0, 5)
        
        reading = monitor.take_reading()
        
        assert reading is not None
        assert reading['temperature'] == 25.5
        assert reading['humidity'] == 45.0
        assert len(monitor.data_logger.data) == 1

    def test_display_update(self, monitor, mock_hardware):
        """Test that the display is updated correctly after a reading."""
        monitor.take_reading()  # Get some data
        monitor.update_display()
        
        assert len(mock_hardware.display_content) == 4
        assert "T:" in mock_hardware.display_content[0]
        assert "AQ:" in mock_hardware.display_content[3]

    def test_error_handling_with_i2c_failures(self, monitor, mock_hardware):
        """Test that the system handles I2C errors gracefully."""
        mock_hardware.i2c_errors = True
        
        # RTC setup should fail gracefully
        assert monitor.setup_rtc_if_needed() is False
        # Sensor reading should fail gracefully
        assert monitor.take_reading() is None

# 6. Edge Case Tests
@pytest.mark.edge_case
class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_leap_year_handling(self):
        """Test date validation for leap and non-leap years."""
        assert RTCLogic.is_valid_time(2024, 2, 29, 12, 0, 0) is True
        assert RTCLogic.is_valid_time(2023, 2, 29, 12, 0, 0) is False

    def test_extreme_sensor_values(self):
        """Test clamping of extreme sensor values."""
        assert SensorDataProcessor.convert_humidity(150000) == 100.0  # Clamped
        assert SensorDataProcessor.convert_humidity(-10000) == 0.0   # Clamped

    def test_year_2038_problem(self):
        """Test that dates beyond the 32-bit timestamp limit are handled."""
        weekday = RTCLogic.calculate_weekday(2050, 1, 1)
        assert 1 <= weekday <= 7