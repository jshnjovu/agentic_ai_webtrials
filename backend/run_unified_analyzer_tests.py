#!/usr/bin/env python3
"""
Test runner for UnifiedAnalyzer service tests.
Executes unit and integration tests with detailed logging and analysis.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def run_tests(test_type="all", verbose=True, capture_output=False):
    """
    Run UnifiedAnalyzer tests with specified configuration.
    
    Args:
        test_type: "unit", "integration", or "all"
        verbose: Enable verbose output
        capture_output: Capture test output for analysis
    """
    
    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    print(f"🚀 Running UnifiedAnalyzer tests from: {backend_dir}")
    print(f"📊 Test type: {test_type}")
    print(f"🔍 Verbose: {verbose}")
    print(f"📝 Capture output: {capture_output}")
    print("=" * 80)
    
    # Build pytest command
    cmd = ["python", "-m", "pytest"]
    
    if verbose:
        cmd.extend(["-v", "-s"])
    
    if test_type == "unit":
        cmd.append("tests/unit/test_services/test_unified_analyzer.py")
    elif test_type == "integration":
        cmd.append("tests/integration/test_unified_analyzer_integration.py")
    elif test_type == "all":
        cmd.extend([
            "tests/unit/test_services/test_unified_analyzer.py",
            "tests/integration/test_unified_analyzer_integration.py"
        ])
    else:
        print(f"❌ Invalid test type: {test_type}")
        return False
    
    # Add markers for integration tests
    if test_type in ["integration", "all"]:
        cmd.extend(["-m", "integration"])
    
    # Add coverage if available
    try:
        import coverage
        cmd.extend(["--cov=src.services.unified", "--cov-report=term-missing"])
        print("📊 Coverage reporting enabled")
    except ImportError:
        print("⚠️ Coverage not available, skipping coverage report")
    
    print(f"🔧 Command: {' '.join(cmd)}")
    print("=" * 80)
    
    # Run tests
    start_time = time.time()
    
    try:
        if capture_output:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            # Print output
            if result.stdout:
                print("📤 STDOUT:")
                print(result.stdout)
            
            if result.stderr:
                print("📤 STDERR:")
                print(result.stderr)
            
            success = result.returncode == 0
            
        else:
            result = subprocess.run(cmd, timeout=300)
            success = result.returncode == 0
            
    except subprocess.TimeoutExpired:
        print("⏰ Tests timed out after 5 minutes")
        success = False
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        success = False
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    print("=" * 80)
    print(f"⏱️ Test execution completed in {execution_time:.2f}s")
    print(f"✅ Success: {success}")
    
    return success

def analyze_test_results():
    """Analyze test results and provide insights."""
    print("\n🔍 Analyzing test results...")
    
    # Check if tests directory exists
    tests_dir = Path("tests")
    if not tests_dir.exists():
        print("❌ Tests directory not found")
        return
    
    # Count test files
    unit_tests = list(tests_dir.glob("unit/test_services/test_unified_analyzer.py"))
    integration_tests = list(tests_dir.glob("integration/test_unified_analyzer_integration.py"))
    
    print(f"📁 Unit test files: {len(unit_tests)}")
    print(f"📁 Integration test files: {len(integration_tests)}")
    
    # Check test coverage
    if unit_tests:
        print("✅ Unit tests available")
    else:
        print("⚠️ Unit tests not found")
    
    if integration_tests:
        print("✅ Integration tests available")
    else:
        print("⚠️ Integration tests not found")
    
    # Check dependencies
    print("\n🔧 Checking dependencies...")
    
    try:
        import pytest
        print(f"✅ pytest {pytest.__version__} available")
    except ImportError:
        print("❌ pytest not available")
    
    try:
        import asyncio
        print(f"✅ asyncio available")
    except ImportError:
        print("❌ asyncio not available")
    
    try:
        from src.services.unified import UnifiedAnalyzer
        print("✅ UnifiedAnalyzer import successful")
    except ImportError as e:
        print(f"❌ UnifiedAnalyzer import failed: {e}")

def main():
    """Main test runner function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run UnifiedAnalyzer tests")
    parser.add_argument(
        "--type", 
        choices=["unit", "integration", "all"], 
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--capture",
        action="store_true",
        help="Capture test output for analysis"
    )
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Analyze test setup and dependencies"
    )
    
    args = parser.parse_args()
    
    print("🧪 UnifiedAnalyzer Test Runner")
    print("=" * 80)
    
    if args.analyze:
        analyze_test_results()
        return
    
    # Run tests
    success = run_tests(
        test_type=args.type,
        verbose=args.verbose,
        capture_output=args.capture
    )
    
    if success:
        print("\n🎉 All tests passed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
