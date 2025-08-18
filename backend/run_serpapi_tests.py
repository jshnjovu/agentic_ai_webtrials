#!/usr/bin/env python3
"""
Test runner script for SERPAPI integration and unit tests.
This script runs all SERPAPI-related tests and provides a comprehensive summary.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

def run_command(command, description):
    """Run a command and return the result."""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}")
    print(f"Command: {command}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )
        
        if result.returncode == 0:
            print("✅ Command completed successfully")
            print(f"Output:\n{result.stdout}")
        else:
            print("❌ Command failed")
            print(f"Error:\n{result.stderr}")
            if result.stdout:
                print(f"Output:\n{result.stdout}")
        
        return result.returncode == 0, result.stdout, result.stderr
        
    except subprocess.TimeoutExpired:
        print("⏰ Command timed out after 5 minutes")
        return False, "", "Command timed out"
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        return False, "", str(e)

def check_environment():
    """Check if required environment variables are set."""
    print("\n🔍 Checking Environment Configuration")
    print("-" * 40)
    
    required_vars = ["SERPAPI_API_KEY"]
    optional_vars = ["SERPAPI_RATE_LIMIT_PER_MINUTE"]
    
    env_status = {}
    
    # Check required variables
    for var in required_vars:
        value = os.getenv(var)
        if value and value not in ["test_key", "your_serpapi_api_key_here"]:
            print(f"✅ {var}: Set (value hidden)")
            env_status[var] = "set"
        else:
            print(f"❌ {var}: Not set or invalid")
            env_status[var] = "missing"
    
    # Check optional variables
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"ℹ️  {var}: {value}")
            env_status[var] = "set"
        else:
            print(f"ℹ️  {var}: Not set (using default)")
            env_status[var] = "default"
    
    return env_status

def run_standalone_integration_test():
    """Run the standalone SERPAPI integration test."""
    test_file = Path("test_serpapi_integration.py")
    
    if not test_file.exists():
        print("❌ Standalone integration test file not found")
        return False, "", "Test file not found"
    
    command = f"python {test_file}"
    return run_command(command, "Running Standalone SERPAPI Integration Test")

def run_pytest_unit_tests():
    """Run pytest unit tests for SERPAPI."""
    test_dir = Path("tests/unit/test_services")
    test_file = test_dir / "test_serpapi_service.py"
    
    if not test_file.exists():
        print("❌ SERPAPI unit test file not found")
        return False, "", "Unit test file not found"
    
    command = f"python -m pytest {test_file} -v"
    return run_command(command, "Running SERPAPI Unit Tests")

def run_pytest_integration_tests():
    """Run pytest integration tests for SERPAPI."""
    test_file = Path("tests/integration/test_serpapi_integration.py")
    
    if not test_file.exists():
        print("❌ SERPAPI integration test file not found")
        return False, "", "Integration test file not found"
    
    command = f"python -m pytest {test_file} -v -m integration"
    return run_command(command, "Running SERPAPI Integration Tests")

def run_pytest_api_tests():
    """Run pytest API endpoint tests for SERPAPI."""
    test_file = Path("tests/unit/test_api/test_serpapi_business_search_api.py")
    
    if not test_file.exists():
        print("❌ SERPAPI API test file not found")
        return False, "", "API test file not found"
    
    command = f"python -m pytest {test_file} -v"
    return run_command(command, "Running SERPAPI API Endpoint Tests")

def run_all_pytest_tests():
    """Run all pytest tests that include SERPAPI."""
    command = "python -m pytest tests/ -v -k serpapi --tb=short"
    return run_command(command, "Running All SERPAPI-Related Pytest Tests")

def generate_test_summary(results):
    """Generate a summary of all test results."""
    print("\n" + "="*80)
    print("📊 SERPAPI TEST EXECUTION SUMMARY")
    print("="*80)
    
    total_tests = len(results)
    passed_tests = sum(1 for success, _, _ in results if success)
    failed_tests = total_tests - passed_tests
    
    print(f"Total Tests Executed: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%" if total_tests > 0 else "N/A")
    
    print("\n" + "-"*80)
    print("📋 DETAILED RESULTS")
    print("-"*80)
    
    test_names = [
        "Standalone Integration Test",
        "Unit Tests",
        "Integration Tests", 
        "API Endpoint Tests",
        "All Pytest Tests"
    ]
    
    for i, (success, stdout, stderr) in enumerate(results):
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{i+1}. {test_names[i]}: {status}")
        
        if not success and stderr:
            print(f"   Error: {stderr[:200]}{'...' if len(stderr) > 200 else ''}")
    
    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"serpapi_test_results_{timestamp}.json"
    
    summary_data = {
        "timestamp": datetime.now().isoformat(),
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "failed_tests": failed_tests,
        "success_rate": (passed_tests/total_tests)*100 if total_tests > 0 else 0,
        "results": [
            {
                "test_name": test_names[i],
                "success": success,
                "stdout": stdout,
                "stderr": stderr
            }
            for i, (success, stdout, stderr) in enumerate(results)
        ]
    }
    
    with open(results_file, 'w') as f:
        json.dump(summary_data, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: {results_file}")
    
    return passed_tests == total_tests

def main():
    """Main test execution function."""
    print("🧪 SERPAPI COMPREHENSIVE TEST SUITE")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check environment
    env_status = check_environment()
    
    if env_status.get("SERPAPI_API_KEY") == "missing":
        print("\n⚠️  WARNING: SERPAPI_API_KEY not set!")
        print("   Some tests may fail or be skipped.")
        print("   Set the environment variable to run full integration tests.")
    
    # Run all tests
    results = []
    
    # 1. Standalone integration test
    success, stdout, stderr = run_standalone_integration_test()
    results.append((success, stdout, stderr))
    
    # 2. Unit tests
    success, stdout, stderr = run_pytest_unit_tests()
    results.append((success, stdout, stderr))
    
    # 3. Integration tests
    success, stdout, stderr = run_pytest_integration_tests()
    results.append((success, stdout, stderr))
    
    # 4. API endpoint tests
    success, stdout, stderr = run_pytest_api_tests()
    results.append((success, stdout, stderr))
    
    # 5. All pytest tests with SERPAPI keyword
    success, stdout, stderr = run_all_pytest_tests()
    results.append((success, stdout, stderr))
    
    # Generate summary
    all_passed = generate_test_summary(results)
    
    print("\n" + "="*80)
    if all_passed:
        print("🎉 ALL SERPAPI TESTS PASSED SUCCESSFULLY!")
        print("   Your SERPAPI integration is working correctly.")
    else:
        print("💥 SOME SERPAPI TESTS FAILED!")
        print("   Check the detailed results above for issues.")
        print("   Review error messages and fix any problems.")
    
    print("="*80)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
