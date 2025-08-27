"""
main_improved.py
----------------
Improved FastAPI server using class-based PDF processor.
Addresses all code quality issues and follows best practices.
"""
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import shutil
import subprocess
import json
import os
import sys
from typing import List, Dict, Optional

# Add the backend folder to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'usb-pd-parser-backend'))

from pdf_processor import PDFProcessor, SectionValidator


class PDFProcessingService:
    """Service class for PDF processing operations"""
    
    def __init__(self):
        self.python_executable = sys.executable
    
    def process_pdf(self, pdf_filename: str, doc_title: str) -> Dict:
        """Process PDF using the new class-based processor"""
        try:
            # Use the new class-based processor
            processor = PDFProcessor(pdf_filename, doc_title)
            
            # Extract TOC
            toc_entries = processor.extract_toc()
            processor.save_toc_to_jsonl()
            
            # Parse sections
            sections = processor.parse_sections()
            
            # Validate sections
            valid_sections, issues = SectionValidator.validate_sections(sections)
            
            if issues:
                print(f"Validation issues found: {len(issues)}")
                for issue in issues[:5]:  # Show first 5 issues
                    print(f"  - {issue}")
            
            processor.save_sections_to_jsonl()
            
            # Generate validation report using legacy script
            self._generate_validation_report()
            
            return {
                "success": True,
                "toc_count": len(toc_entries),
                "sections_count": len(valid_sections),
                "validation_issues": len(issues)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_validation_report(self):
        """Generate validation report using legacy script"""
        try:
            backend_path = os.path.join(os.path.dirname(__file__), 'usb-pd-parser-backend')
            subprocess.run([
                self.python_executable, 
                os.path.join(backend_path, "validation_report.py")
            ], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Warning: Validation report generation failed: {e}")


class FileService:
    """Service class for file operations"""
    
    @staticmethod
    def save_uploaded_file(file: UploadFile, filename: str) -> bool:
        """Save uploaded file to disk"""
        try:
            with open(filename, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            return True
        except Exception as e:
            print(f"Error saving file: {e}")
            return False
    
    @staticmethod
    def load_jsonl_results(filename: str) -> Optional[List[Dict]]:
        """Load results from JSONL file"""
        if not os.path.exists(filename):
            return None
        
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return [json.loads(line) for line in f]
        except Exception as e:
            print(f"Error loading JSONL file: {e}")
            return None
    
    @staticmethod
    def is_allowed_download(filename: str) -> bool:
        """Check if file download is allowed"""
        allowed_files = [
            "usb_pd_toc.jsonl",
            "usb_pd_spec.jsonl",
            "usb_pd_validation_report.xlsx"
        ]
        return filename in allowed_files


# Initialize FastAPI app
app = FastAPI(title="USB PD Specification Parser", version="2.0.0")

# Configure CORS
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost",
    "http://127.0.0.1"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
pdf_service = PDFProcessingService()
file_service = FileService()


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload and process PDF file"""
    pdf_filename = "uploaded.pdf"
    
    # Save uploaded file
    if not file_service.save_uploaded_file(file, pdf_filename):
        return {"error": "Failed to save uploaded file"}
    
    # Process PDF
    result = pdf_service.process_pdf(pdf_filename, "USB PD Specification")
    
    if not result["success"]:
        return {"error": result["error"]}
    
    # Load TOC results for frontend preview
    toc_results = file_service.load_jsonl_results("usb_pd_toc.jsonl")
    
    if toc_results is None:
        return {"error": "TOC file not found after processing"}
    
    return {
        "success": True,
        "results": toc_results,
        "stats": result
    }


@app.get("/results")
def get_results():
    """Get processing results"""
    results = file_service.load_jsonl_results("usb_pd_toc.jsonl")
    
    if results is None:
        return {"error": "Results file not found"}
    
    return results


@app.get("/download/{filename}")
def download_file(filename: str):
    """Download processed files"""
    if not file_service.is_allowed_download(filename):
        return {"error": "File not allowed"}
    
    file_path = os.path.join(os.getcwd(), filename)
    
    if not os.path.exists(file_path):
        return {"error": "File not found"}
    
    return FileResponse(
        file_path,
        media_type='application/octet-stream',
        filename=filename
    )


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "services": {
            "pdf_processor": "available",
            "file_service": "available"
        }
    }


if __name__ == "__main__":
    import uvicorn
    import logging
    
    # Suppress asyncio warnings on Windows
    logging.getLogger("asyncio").setLevel(logging.ERROR)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
