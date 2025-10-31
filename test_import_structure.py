#!/usr/bin/env python3
"""
Test script to verify import structure without full application initialization
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_import_structure():
    """Test that the import structure is correct"""
    try:
        # Test basic imports without triggering full app initialization
        import api.services.create.shared as shared_module
        print("✅ Shared module imported successfully")
        
        # Check if the required functions exist
        required_functions = [
            'create_video_generation_job',
            'validate_step', 
            'regenerate_single_image',
            'regenerate_single_video',
            'validate_project_and_get_cost',
            'create_generation_job',
            'deduct_credits_and_update_status',
            'handle_generation_failure',
            'format_job_status',
            'get_generation_progress'
        ]
        
        missing_functions = []
        for func_name in required_functions:
            if not hasattr(shared_module, func_name):
                missing_functions.append(func_name)
        
        if missing_functions:
            print(f"❌ Missing functions: {missing_functions}")
            return False
        else:
            print("✅ All required functions found in shared module")
            return True
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_import_structure()
    if success:
        print("\n🎉 Import structure is correct! The missing functions have been added.")
        print("The segmentation fault is likely due to missing dependencies (jose, librosa),")
        print("not the import structure itself.")
    sys.exit(0 if success else 1)
