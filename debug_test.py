#!/usr/bin/env python3
"""
Debug test script for the Maltrail Connector
Use this to test specific functionality without running the full connector
"""

import os
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_config():
    """Test configuration loading"""
    print("Testing configuration...")
    try:
        from utils.config_variables import Config
        config = Config()
        print(f"Config loaded successfully: {config}")
        return True
    except Exception as e:
        print(f"Config error: {e}")
        return False

def test_github_client():
    """Test GitHub client initialization"""
    print("Testing GitHub client...")
    try:
        from utils.github_client import GithubClient
        from utils.config_variables import Config
        from pycti import OpenCTIConnectorHelper
        
        config = Config()
        helper = OpenCTIConnectorHelper(config.load)
        client = GithubClient(helper, config)
        print(f"GitHub client created successfully: {client}")
        return True
    except Exception as e:
        print(f"GitHub client error: {e}")
        return False

def test_stix_converter():
    """Test STIX converter"""
    print("Testing STIX converter...")
    try:
        from utils.stix_client import STIXConvertor
        from utils.config_variables import Config
        from pycti import OpenCTIConnectorHelper
        
        config = Config()
        helper = OpenCTIConnectorHelper(config.load)
        
        # Test with sample data
        sample_entity = {
            "references": ["https://example.com"],
            "observables": ["192.168.1.1", "malware.example.com"]
        }
        
        stix_convertor = STIXConvertor(helper, sample_entity["references"])
        print(f"STIX converter created successfully: {stix_convertor}")
        return True
    except Exception as e:
        print(f"STIX converter error: {e}")
        return False

def main():
    """Run all tests"""
    print("=== Maltrail Connector Debug Tests ===\n")
    
    tests = [
        ("Configuration", test_config),
        ("GitHub Client", test_github_client),
        ("STIX Converter", test_stix_converter)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"Running {test_name} test...")
        try:
            result = test_func()
            results.append((test_name, result))
            print(f"{test_name}: {'✓ PASS' if result else '✗ FAIL'}\n")
        except Exception as e:
            print(f"{test_name}: ✗ ERROR - {e}\n")
            results.append((test_name, False))
    
    print("=== Test Results ===")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("All tests passed! 🎉")
    else:
        print("Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()
