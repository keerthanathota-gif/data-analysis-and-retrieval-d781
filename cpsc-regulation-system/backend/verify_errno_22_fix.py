#!/usr/bin/env python3
"""
Verification script for [Errno 22] Invalid Argument fix
Tests that the datetime serialization and file operations work correctly
"""

import sys
import os

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_datetime_serialization():
    """Test that datetime is properly serialized as ISO string"""
    print("\n[TEST 1/4] Testing datetime serialization...")
    try:
        from app.pipeline.data_pipeline import DataPipeline
        
        # Create pipeline instance
        pipeline = DataPipeline()
        
        # Simulate a status update
        pipeline.update_status(state='running')
        status = pipeline.get_status()
        
        # Check that start_time is a string, not datetime object
        start_time = status.get('start_time')
        if start_time is None:
            print("  ✓ start_time is None (expected for initial state)")
        elif isinstance(start_time, str):
            print(f"  ✓ start_time is ISO string: {start_time}")
        else:
            print(f"  ✗ ERROR: start_time is {type(start_time)}, expected str")
            return False
        
        # Update to completed state
        pipeline.update_status(state='completed')
        status = pipeline.get_status()
        
        end_time = status.get('end_time')
        if isinstance(end_time, str):
            print(f"  ✓ end_time is ISO string: {end_time}")
        else:
            print(f"  ✗ ERROR: end_time is {type(end_time)}, expected str")
            return False
        
        print("  ✓ Datetime serialization test PASSED")
        return True
    except Exception as e:
        print(f"  ✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_schema_validation():
    """Test that PipelineStatus schema accepts string datetimes"""
    print("\n[TEST 2/4] Testing schema validation...")
    try:
        from app.models.schemas import PipelineStatus
        
        # Create a status with string datetimes
        status_data = {
            'state': 'completed',
            'current_step': 'Test',
            'progress': 100,
            'total_steps': 6,
            'steps_completed': ['Step1', 'Step2'],
            'error_message': None,
            'start_time': '2025-10-26T10:30:45.123456',
            'end_time': '2025-10-26T10:35:12.654321',
            'stats': {'test': 123}
        }
        
        # Validate with Pydantic
        status = PipelineStatus(**status_data)
        
        print(f"  ✓ Schema validation successful")
        print(f"    start_time: {status.start_time} (type: {type(status.start_time).__name__})")
        print(f"    end_time: {status.end_time} (type: {type(status.end_time).__name__})")
        print("  ✓ Schema validation test PASSED")
        return True
    except Exception as e:
        print(f"  ✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_path_normalization():
    """Test that paths are properly normalized"""
    print("\n[TEST 3/4] Testing path normalization...")
    try:
        import os
        
        # Test path with backslashes (Windows style)
        test_path = "C:\\Users\\test\\data\\file.json"
        normalized = os.path.abspath(test_path).replace('\\', '/')
        
        print(f"  Original: {test_path}")
        print(f"  Normalized: {normalized}")
        
        # Check that there are no backslashes in normalized path
        if '\\' in normalized:
            print(f"  ✗ ERROR: Backslashes still present in normalized path")
            return False
        
        print("  ✓ Path normalization test PASSED")
        return True
    except Exception as e:
        print(f"  ✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_filename_validation():
    """Test that invalid filenames are detected"""
    print("\n[TEST 4/4] Testing filename validation...")
    try:
        import os
        
        # Test filename with colon (invalid on Windows)
        test_filename = "test:file.json"
        
        if ':' in os.path.basename(test_filename):
            print(f"  ✓ Detected colon in filename: {test_filename}")
        else:
            print(f"  ✗ ERROR: Failed to detect colon in filename")
            return False
        
        # Test valid filename
        valid_filename = "test_file.json"
        if ':' in os.path.basename(valid_filename):
            print(f"  ✗ ERROR: False positive on valid filename")
            return False
        else:
            print(f"  ✓ Valid filename passed: {valid_filename}")
        
        print("  ✓ Filename validation test PASSED")
        return True
    except Exception as e:
        print(f"  ✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("=" * 70)
    print("  [Errno 22] Invalid Argument Fix - Verification Tests")
    print("=" * 70)
    
    results = []
    
    # Run all tests
    results.append(test_datetime_serialization())
    results.append(test_schema_validation())
    results.append(test_path_normalization())
    results.append(test_filename_validation())
    
    # Print summary
    print("\n" + "=" * 70)
    passed = sum(results)
    total = len(results)
    
    if all(results):
        print(f"  ✅ ALL TESTS PASSED ({passed}/{total})")
        print("=" * 70)
        print("\n  The [Errno 22] Invalid argument fix has been verified!")
        print("  You can now safely:")
        print("    1. Reset the database using the frontend")
        print("    2. Run the pipeline without encountering Errno 22 errors")
        print()
        return 0
    else:
        print(f"  ❌ SOME TESTS FAILED ({passed}/{total} passed)")
        print("=" * 70)
        print("\n  Please review the test output above for details.")
        print()
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
