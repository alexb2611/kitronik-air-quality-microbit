# Testing Framework for Kitronik Air Quality Board

This directory contains comprehensive unit tests and testing infrastructure for the micro:bit air quality monitoring project.

## Testing Philosophy

**"Test early, test often, deploy with confidence!"**

Even for hobby projects, good testing practices:
- 🐛 **Catch bugs early** - Before they reach the micro:bit
- 🔧 **Enable refactoring** - Change code with confidence  
- 📚 **Document behaviour** - Tests show how code should work
- 🎓 **Educational value** - Great for teaching Albie about quality code
- 🚀 **Faster development** - Less time debugging on hardware

## Testing Strategy

### 1. **Separation of Concerns**
```
Pure Logic ←→ Hardware Interface ←→ Physical Hardware
     ↑              ↑                      ↑
   Easily         Mock for              Real I2C
   Testable       Testing               Devices
```

### 2. **Test Types**

**Unit Tests** 📦
- Test individual functions in isolation
- Fast execution, no hardware required
- Example: BCD conversion, data formatting

**Integration Tests** 🔗  
- Test components working together
- Use mock hardware interfaces
- Example: Sensor reading → processing → display

**Hardware Tests** 🔧
- Test against real hardware
- Slower, requires physical setup
- Example: Actual I2C communication

## Files Overview

- **`test_strategy.py`** - Testable architecture and mock objects
- **`test_air_quality_monitor.py`** - Comprehensive unit tests
- **`test_runner.py`** - Custom test runner with micro:bit focus
- **`test_hardware.py`** - Hardware integration tests (coming soon)
- **`pytest.ini`** - Pytest configuration
- **`requirements-test.txt`** - Testing dependencies

## Quick Start

### Option 1: Using unittest (built-in)
```bash
cd tests/
python test_air_quality_monitor.py
```

### Option 2: Using pytest (recommended)
```bash
# Install pytest first
pip install pytest pytest-cov

# Run all tests
pytest -v

# Run with coverage report
pytest --cov=../src --cov-report=html -v
```

### Option 3: Using our custom runner
```bash
python test_runner.py
```

## Test Results Example

```
Testing Air Quality Monitor - Comprehensive Suite
==================================================

test_rtc_logic.py::TestRTCLogic::test_bcd_conversion PASSED
test_rtc_logic.py::TestRTCLogic::test_weekday_calculation PASSED
test_sensor.py::TestSensorDataProcessor::test_temperature_conversion PASSED
test_integration.py::TestAirQualityMonitorIntegration::test_full_workflow PASSED

==================================================
Tests run: 42
Failures: 0
Errors: 0
Success rate: 100.0%

🎉 All tests passed! Your code is ready for the micro:bit.
```

## Test-Driven Development (TDD)

Perfect opportunity to teach Albie about TDD:

1. **🔴 Red** - Write a failing test first
2. **🟢 Green** - Write minimal code to make it pass  
3. **🔵 Refactor** - Improve the code while keeping tests green

### Example TDD Cycle:
```python
# 1. RED: Write failing test
def test_air_quality_alert():
    assert air_quality_needs_alert(250) == True  # Fails - function doesn't exist

# 2. GREEN: Write minimal code
def air_quality_needs_alert(iaq_score):
    return iaq_score > 200  # Just enough to pass

# 3. REFACTOR: Improve implementation
def air_quality_needs_alert(iaq_score, threshold=200):
    """Return True if air quality requires alert"""
    return isinstance(iaq_score, (int, float)) and iaq_score > threshold
```

## Testing Best Practices

### ✅ DO:
- **Test edge cases** - What happens with invalid input?
- **Test error conditions** - How does code handle I2C failures?
- **Use descriptive test names** - `test_rtc_setup_when_time_invalid()`
- **Keep tests independent** - Each test should work in isolation
- **Mock external dependencies** - Don't rely on actual hardware for unit tests

### ❌ DON'T:
- **Test implementation details** - Test behaviour, not internal code structure
- **Write tests that depend on each other** - Tests should run in any order
- **Skip testing because "it's just hobby code"** - Great habits start early!

## Educational Benefits

This testing approach teaches:

### For Albie (9 years old):
- **Logical thinking** - "If I give this input, what should happen?"
- **Problem decomposition** - Breaking big problems into testable pieces
- **Quality mindset** - "How do I know my code works?"

### For You:
- **Professional practices** - Industry-standard testing approaches
- **Debugging skills** - Tests help isolate problems quickly
- **Confidence** - Deploy changes knowing they work

## Hardware Testing Strategy

For testing with actual micro:bit hardware:

### Mock → Simulate → Real Hardware
1. **Unit tests** with mocks (fast feedback)
2. **Simulator testing** (if available)  
3. **Hardware validation** (final verification)

### Hardware Test Checklist:
- ✅ RTC time setting and reading
- ✅ BME688 sensor communication
- ✅ OLED display output
- ✅ EEPROM data storage
- ✅ ZIP LED control
- ✅ Error handling (disconnected sensors, etc.)

## Continuous Integration Ready

This testing framework is designed for CI/CD:

```yaml
# .github/workflows/test.yml (example)
name: Test Air Quality Monitor
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - name: Install dependencies
      run: pip install -r tests/requirements-test.txt
    - name: Run tests
      run: pytest tests/ --cov=src/ --cov-report=xml
    - name: Upload coverage
      uses: codecov/codecov-action@v1
```

## Running Tests in Development

### Daily Development Workflow:
```bash
# 1. Write or modify code
# 2. Run quick tests
pytest tests/test_air_quality_monitor.py::TestRTCLogic -v

# 3. Run all tests before committing
pytest -v

# 4. Check coverage
pytest --cov=../src --cov-report=term-missing

# 5. Commit with confidence!
git add .
git commit -m "Add RTC auto-setup with tests"
```

---

**Remember:** Good tests are the foundation of reliable code. They're especially valuable when working with hardware where debugging can be challenging!

*Happy testing! 🧪✨*
