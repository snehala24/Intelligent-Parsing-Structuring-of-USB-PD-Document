"""
run_tests.py
------------
Script to run tests from the root directory with correct path handling.
"""
import os
import sys
import subprocess

def run_tests():
    """Run tests from the backend directory"""
    backend_path = os.path.join(os.path.dirname(__file__), 'usb-pd-parser-backend')
    
    # Change to backend directory
    os.chdir(backend_path)
    
    # Run tests
    try:
        result = subprocess.run([
            sys.executable, 
            "-m", 
            "pytest", 
            "test_pdf_processor.py", 
            "-v"
        ], check=True)
        print("✅ All tests passed!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Tests failed with exit code: {e.returncode}")
        return False
    
    return True

if __name__ == "__main__":
    print("🧪 Running PDF Processor Tests...")
    success = run_tests()
    if success:
        print("🎉 Test execution completed successfully!")
    else:
        print("💥 Test execution failed!")
        sys.exit(1)
