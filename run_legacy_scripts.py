"""
run_legacy_scripts.py
---------------------
Script to run legacy PDF processing scripts from the root directory.
"""
import os
import sys
import subprocess

def run_legacy_script(script_name, *args):
    """Run a legacy script from the backend directory"""
    backend_path = os.path.join(os.path.dirname(__file__), 'usb-pd-parser-backend')
    script_path = os.path.join(backend_path, script_name)
    
    if not os.path.exists(script_path):
        print(f"❌ Script not found: {script_path}")
        return False
    
    try:
        cmd = [sys.executable, script_path] + list(args)
        print(f"🚀 Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True)
        print(f"✅ {script_name} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {script_name} failed with exit code: {e.returncode}")
        return False

def run_full_pipeline(pdf_file, doc_title="USB PD Specification"):
    """Run the full PDF processing pipeline"""
    print("🔄 Starting PDF Processing Pipeline...")
    
    # Step 1: Extract TOC
    print("\n📋 Step 1: Extracting Table of Contents...")
    if not run_legacy_script("pdf_toc_parser.py", pdf_file, doc_title):
        return False
    
    # Step 2: Parse Sections
    print("\n📄 Step 2: Parsing Sections...")
    if not run_legacy_script("pdf_section_parser.py", pdf_file, "usb_pd_toc.jsonl"):
        return False
    
    # Step 3: Generate Validation Report
    print("\n📊 Step 3: Generating Validation Report...")
    if not run_legacy_script("validation_report.py"):
        return False
    
    print("\n🎉 Full pipeline completed successfully!")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_legacy_scripts.py <pdf_file> [doc_title]")
        print("Example: python run_legacy_scripts.py usb_pd_spec.pdf 'USB PD Specification'")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    doc_title = sys.argv[2] if len(sys.argv) > 2 else "USB PD Specification"
    
    success = run_full_pipeline(pdf_file, doc_title)
    if not success:
        sys.exit(1)
