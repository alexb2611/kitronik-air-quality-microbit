#!/usr/bin/env python3
"""
Custom Test Runner for Kitronik Air Quality Board Project

A friendly test runner designed specifically for micro:bit development.
Provides clear feedback and educational output for learning.

Usage:
    python test_runner.py                    # Run all tests
    python test_runner.py --quick            # Run only fast tests
    python test_runner.py --hardware         # Include hardware tests
    python test_runner.py --watch            # Watch for file changes
    python test_runner.py --coverage         # Generate coverage report
    python test_runner.py --help             # Show help
"""

import sys
import os
import time
import argparse
import subprocess
from pathlib import Path

# Try to import rich for beautiful output
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("💡 Tip: Install 'rich' for beautiful output: pip install rich")

class MicrobitTestRunner:
    """Custom test runner for micro:bit projects"""
    
    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
        self.start_time = None
        self.test_results = {}
        
    def print_banner(self):
        """Print a welcoming banner"""
        if RICH_AVAILABLE:
            banner = Panel.fit(
                "[bold blue]🔬 Kitronik Air Quality Board Test Suite[/bold blue]\n"
                "[dim]Testing micro:bit code with confidence![/dim]",
                border_style="blue"
            )
            self.console.print(banner)
        else:
            print("🔬 Kitronik Air Quality Board Test Suite")
            print("=" * 50)
            print("Testing micro:bit code with confidence!")
            print()
    
    def print_info(self, message, style="info"):
        """Print informational message"""
        if RICH_AVAILABLE:
            styles = {
                "info": "[blue]ℹ️[/blue]",
                "success": "[green]✅[/green]", 
                "warning": "[yellow]⚠️[/yellow]",
                "error": "[red]❌[/red]"
            }
            self.console.print(f"{styles.get(style, '')} {message}")
        else:
            icons = {"info": "ℹ️", "success": "✅", "warning": "⚠️", "error": "❌"}
            print(f"{icons.get(style, '')} {message}")
    
    def check_environment(self):
        """Check if testing environment is set up correctly"""
        self.print_info("Checking test environment...", "info")
        
        issues = []
        
        # Check if we're in the right directory
        if not Path("test_air_quality_monitor.py").exists():
            issues.append("Not in tests directory - run from tests/ folder")
        
        # Check if src directory exists
        src_path = Path("../src")
        if not src_path.exists():
            issues.append("Source directory '../src' not found")
        
        # Check for test dependencies
        try:
            import unittest
        except ImportError:
            issues.append("unittest module not available")
        
        # Check for optional dependencies
        missing_optional = []
        try:
            import pytest
        except ImportError:
            missing_optional.append("pytest")
        
        if issues:
            for issue in issues:
                self.print_info(issue, "error")
            return False
        
        if missing_optional:
            self.print_info(f"Optional dependencies missing: {', '.join(missing_optional)}", "warning")
            self.print_info("Install with: pip install -r requirements-test.txt", "info")
        
        self.print_info("Environment looks good! 🚀", "success")
        return True
    
    def run_unittest_suite(self, test_pattern="test_*.py", verbose=True):
        """Run tests using unittest"""
        self.print_info("Running tests with unittest...", "info")
        
        try:
            # Import and run our main test suite
            from test_air_quality_monitor import run_all_tests
            
            self.start_time = time.time()
            success = run_all_tests()
            duration = time.time() - self.start_time
            
            self.test_results["unittest"] = {
                "success": success,
                "duration": duration
            }
            
            return success
            
        except ImportError as e:
            self.print_info(f"Could not import test suite: {e}", "error")
            return False
        except Exception as e:
            self.print_info(f"Test execution failed: {e}", "error")
            return False
    
    def run_pytest_suite(self, args=None):
        """Run tests using pytest if available"""
        try:
            import pytest
        except ImportError:
            self.print_info("pytest not available, skipping", "warning")
            return None
        
        self.print_info("Running tests with pytest...", "info")
        
        pytest_args = ["-v", "--tb=short"]
        if args:
            pytest_args.extend(args)
        
        try:
            self.start_time = time.time()
            result = pytest.main(pytest_args)
            duration = time.time() - self.start_time
            
            self.test_results["pytest"] = {
                "success": result == 0,
                "duration": duration,
                "return_code": result
            }
            
            return result == 0
            
        except Exception as e:
            self.print_info(f"pytest execution failed: {e}", "error")
            return False
    
    def run_coverage_analysis(self):
        """Run coverage analysis if pytest-cov is available"""
        try:
            import pytest_cov
        except ImportError:
            self.print_info("pytest-cov not available for coverage analysis", "warning")
            return
        
        self.print_info("Generating coverage report...", "info")
        
        try:
            result = subprocess.run([
                sys.executable, "-m", "pytest",
                "--cov=../src",
                "--cov-report=term-missing",
                "--cov-report=html:../coverage_html",
                "-v"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.print_info("Coverage report generated in ../coverage_html/", "success")
            else:
                self.print_info("Coverage generation failed", "error")
                
        except Exception as e:
            self.print_info(f"Coverage analysis failed: {e}", "error")
    
    def watch_for_changes(self):
        """Watch for file changes and re-run tests"""
        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler
        except ImportError:
            self.print_info("watchdog not available for file watching", "error")
            self.print_info("Install with: pip install watchdog", "info")
            return
        
        class TestHandler(FileSystemEventHandler):
            def __init__(self, runner):
                self.runner = runner
                self.last_run = 0
            
            def on_modified(self, event):
                if event.is_directory:
                    return
                
                if event.src_path.endswith(('.py', '.md')):
                    # Debounce - only run tests every 2 seconds
                    now = time.time()
                    if now - self.last_run > 2:
                        self.last_run = now
                        print(f"\n📁 File changed: {event.src_path}")
                        self.runner.run_quick_tests()
        
        self.print_info("👀 Watching for file changes... (Ctrl+C to stop)", "info")
        
        event_handler = TestHandler(self)
        observer = Observer()
        observer.schedule(event_handler, ".", recursive=True)
        observer.schedule(event_handler, "../src", recursive=True)
        observer.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            self.print_info("File watching stopped", "info")
        observer.join()
    
    def run_quick_tests(self):
        """Run only the fastest tests"""
        self.print_info("Running quick tests...", "info")
        
        # Run specific fast test classes
        try:
            from test_air_quality_monitor import TestRTCLogic, TestSensorDataProcessor, TestDisplayFormatter
            
            import unittest
            suite = unittest.TestSuite()
            
            for test_class in [TestRTCLogic, TestSensorDataProcessor, TestDisplayFormatter]:
                tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
                suite.addTests(tests)
            
            runner = unittest.TextTestRunner(verbosity=1)
            result = runner.run(suite)
            
            return result.wasSuccessful()
            
        except Exception as e:
            self.print_info(f"Quick tests failed: {e}", "error")
            return False
    
    def print_summary(self):
        """Print test summary"""
        if not self.test_results:
            return
        
        if RICH_AVAILABLE:
            table = Table(title="Test Results Summary")
            table.add_column("Test Runner", style="cyan")
            table.add_column("Status", style="magenta") 
            table.add_column("Duration", style="green")
            
            for runner, results in self.test_results.items():
                status = "✅ PASSED" if results["success"] else "❌ FAILED"
                duration = f"{results['duration']:.2f}s"
                table.add_row(runner, status, duration)
            
            self.console.print(table)
        else:
            print("\nTest Results Summary:")
            print("-" * 30)
            for runner, results in self.test_results.items():
                status = "PASSED" if results["success"] else "FAILED"
                duration = f"{results['duration']:.2f}s"
                print(f"{runner}: {status} ({duration})")
    
    def print_educational_tips(self):
        """Print educational tips about testing"""
        tips = [
            "💡 Tests help catch bugs before they reach your micro:bit",
            "🔧 Mocking allows testing without physical hardware",
            "📊 Coverage reports show which code isn't tested yet",
            "🚀 Green tests mean you can deploy with confidence",
            "👨‍👧‍👦 Great way to teach Albie about code quality!"
        ]
        
        if RICH_AVAILABLE:
            tip_panel = Panel(
                "\n".join(tips),
                title="[bold green]💡 Testing Tips[/bold green]",
                border_style="green"
            )
            self.console.print(tip_panel)
        else:
            print("\n💡 Testing Tips:")
            for tip in tips:
                print(f"  {tip}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Test runner for Kitronik Air Quality Board project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_runner.py                    # Run all tests
  python test_runner.py --quick            # Run only fast tests  
  python test_runner.py --coverage         # Generate coverage report
  python test_runner.py --watch            # Watch for changes
        """
    )
    
    parser.add_argument("--quick", action="store_true", 
                       help="Run only fast unit tests")
    parser.add_argument("--hardware", action="store_true",
                       help="Include hardware integration tests")
    parser.add_argument("--coverage", action="store_true",
                       help="Generate code coverage report")
    parser.add_argument("--watch", action="store_true",
                       help="Watch for file changes and re-run tests")
    parser.add_argument("--pytest", action="store_true",
                       help="Use pytest instead of unittest")
    parser.add_argument("--tips", action="store_true",
                       help="Show educational tips about testing")
    
    args = parser.parse_args()
    
    # Create test runner
    runner = MicrobitTestRunner()
    runner.print_banner()
    
    # Show tips if requested
    if args.tips:
        runner.print_educational_tips()
        return
    
    # Check environment
    if not runner.check_environment():
        sys.exit(1)
    
    # Handle watch mode
    if args.watch:
        runner.watch_for_changes()
        return
    
    # Run tests based on arguments
    success = True
    
    if args.quick:
        success = runner.run_quick_tests()
    elif args.pytest:
        pytest_args = []
        if args.coverage:
            pytest_args.extend(["--cov=../src", "--cov-report=term-missing"])
        success = runner.run_pytest_suite(pytest_args)
    else:
        # Default: run unittest suite
        success = runner.run_unittest_suite()
    
    # Generate coverage if requested (and not already done)
    if args.coverage and not args.pytest:
        runner.run_coverage_analysis()
    
    # Print summary
    runner.print_summary()
    
    # Educational tips
    if success:
        runner.print_info("🎉 All tests passed! Your code is ready for the micro:bit.", "success")
        runner.print_educational_tips()
    else:
        runner.print_info("❌ Some tests failed. Check the output above.", "error")
        runner.print_info("💡 Failed tests help you find and fix bugs early!", "info")
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
