#!/usr/bin/env python3
"""
Fast test runner for UnifiedAnalyzer + DomainAnalysis integration tests.
Runs tests with minimal overhead and maximum speed.
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Run the fast domain integration tests."""
    print("🚀 Running Fast Domain Integration Tests")
    print("=" * 50)
    
    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    # Check if we're in the right directory
    if not (backend_dir / "src").exists():
        print("❌ Error: Must run from backend directory")
        sys.exit(1)
    
    # Check environment variables
    required_vars = [
        "GOOGLE_GENERAL_API_KEY",
        "WHOIS_API_KEY", 
        "WHOIS_API_BASE_URL",
        "WHOIS_HISTORY_API_BASE_URL"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"⚠️  Warning: Missing environment variables: {missing_vars}")
        print("   Some tests may be skipped")
    
    # Run tests with optimized settings
    cmd = [
        "python", "-m", "pytest",
        "tests/unit/test_services/test_unified_domain_integration.py",
        "-v",  # Verbose output
        "-s",  # Show print statements
        "--tb=short",  # Short traceback
        "--disable-warnings",  # Disable warnings for speed
        "--maxfail=5",  # Stop after 5 failures
        "--durations=10",  # Show top 10 slowest tests
        "--durations-min=0.1",  # Only show tests taking >0.1s
        "-m", "fast",  # Only run fast tests
        "--cov=src.services.unified",  # Coverage for unified
        "--cov=src.services.domain_analysis",  # Coverage for domain analysis
        "--cov-report=term-missing",  # Show missing lines
        "--cov-fail-under=70",  # Fail if coverage < 70%
        "-n", "auto",  # Parallel execution
        "--timeout=120"  # 2 minute timeout per test
    ]
    
    print(f"🔧 Running: {' '.join(cmd)}")
    print()
    
    try:
        # Run the tests
        result = subprocess.run(cmd, check=False)
        
        print()
        print("=" * 50)
        
        if result.returncode == 0:
            print("✅ All tests passed!")
        else:
            print(f"❌ Tests failed with exit code: {result.returncode}")
        
        return result.returncode
        
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
