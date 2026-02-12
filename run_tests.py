#!/usr/bin/env python3
"""
Test Runner for InnoBridge Platform
Runs automated tests with coverage reporting
"""

import sys
import os
import subprocess

def run_tests():
    """Run all tests with coverage"""
    
    print("🧪 InnoBridge Platform - Automated Test Suite")
    print("=" * 60)
    
    # Check if pytest is installed
    try:
        import pytest
    except ImportError:
        print("❌ pytest not installed. Installing dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        import pytest
    
    # Run tests
    print("\n📝 Running tests...")
    print("-" * 60)
    
    # Test arguments
    args = [
        "-v",  # Verbose
        "--cov=.",  # Coverage for all files
        "--cov-report=html",  # HTML coverage report
        "--cov-report=term-missing",  # Terminal report with missing lines
        "tests/"  # Test directory
    ]
    
    # Run pytest
    exit_code = pytest.main(args)
    
    print("\n" + "=" * 60)
    
    if exit_code == 0:
        print("✅ All tests passed!")
        print("\n📊 Coverage report generated:")
        print("   - HTML: htmlcov/index.html")
        print("   - Open in browser to view detailed coverage")
    else:
        print("❌ Some tests failed!")
        print(f"   Exit code: {exit_code}")
    
    print("\n💡 Test Commands:")
    print("   - Run all tests: pytest")
    print("   - Run specific test: pytest tests/test_models.py")
    print("   - Run with markers: pytest -m unit")
    print("   - Run with coverage: pytest --cov")
    
    return exit_code

if __name__ == '__main__':
    sys.exit(run_tests())