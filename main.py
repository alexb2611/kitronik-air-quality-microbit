
"""
Hardware Test Script for the Kitronik Air Quality Board.

This script runs on the BBC micro:bit and tests the functionality of the
Kitronik Air Quality and Environmental Board. It cycles through tests for
the RTC, the BME688 sensor, and the OLED display, providing feedback on
both the OLED screen and the micro:bit's LED matrix.

To use, copy this file to your micro:bit's root directory, along with the
`src` folder containing the `kitronik_air_quality.py` driver.
"""

from microbit import display, button_a, sleep
from kitronik_air_quality import KitronikAirQualityBoard

# --- Helper Functions ---

def display_message(oled, microbit_icon, line1, line2="", delay=2000):
    """Display a message on both the OLED and the micro:bit display."""
    print("TEST: " + line1 + " - " + line2) # Print to serial for debugging
    display.show(microbit_icon)
    oled.clear_display()
    oled.write_display(line1, 0)
    if line2:
        oled.write_display(line2, 1)
    sleep(delay)

# --- Main Test Sequence ---

def run_hardware_tests():
    """Run a sequence of tests to verify hardware functionality."""
    # 1. Initialise the board
    try:
        board = KitronikAirQualityBoard()
        display_message(board, "Y", "Board Init: OK")
    except Exception as e:
        display.show("N")
        print("Error initialising board: " + str(e))
        return

    # 2. Test the RTC
    try:
        # Set the time
        board.write_rtc(2025, 7, 5, 10, 30, 0)
        # Read the time back
        year, month, day, hour, minute, second, weekday = board.read_rtc()
        
        time_str = "{:02}:{:02}:{:02}".format(hour, minute, second)
        date_str = "{:02}/{:02}/{}".format(day, month, year)

        if year == 2025 and month == 7 and day == 5:
            display_message(board, "Y", "RTC Test: OK", date_str)
        else:
            display_message(board, "N", "RTC Test: FAIL", date_str)

    except Exception as e:
        display_message(board, "N", "RTC Test: ERROR", str(e))

    # 3. Test the BME688 Sensor
    try:
        data = board.read_sensor()
        if data:
            temp = data['temperature']
            pressure = data['pressure']
            humidity = data['humidity']
            
            # Display some readings
            display_message(board, "Y", "Sensor: OK", "Temp: {:.1f}C".format(temp/1000))
            display_message(board, "Y", "Sensor: OK", "Pres: {:.0f}Pa".format(pressure/100))
            display_message(board, "Y", "Sensor: OK", "Humi: {:.1f}%".format(humidity/1000))
        else:
            display_message(board, "N", "Sensor: FAIL")

    except Exception as e:
        display_message(board, "N", "Sensor: ERROR", str(e))

    # 4. Test the OLED Display
    try:
        display_message(board, "Y", "OLED Test: OK", "Cycling lines...")
        for i in range(4):
            board.write_display("Line {}".format(i), i)
            sleep(500)
        display_message(board, "Y", "OLED Test: OK", "Fill screen...")
        for i in range(4):
            board.write_display("################", i)
        sleep(1000)

    except Exception as e:
        display_message(board, "N", "OLED Test: ERROR", str(e))

    # 5. Test Completion
    display.show("Y")
    board.clear_display()
    board.write_display("All tests OK!", 0)
    board.write_display("Press A to run", 1)
    board.write_display("again.", 2)

# --- Main Loop ---

if __name__ == "__main__":
    display.show("Y")
    while True:
        if button_a.was_pressed():
            run_hardware_tests()
        sleep(100)
