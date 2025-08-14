from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import shutil, subprocess, json, os, sys

app = FastAPI()

# ✅ Allow CORS for your local frontend
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
    allow_methods=["*"],  # GET, POST, OPTIONS
    allow_headers=["*"],
)

# ✅ Use the same Python interpreter as the FastAPI server
python_executable = sys.executable

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    pdf_filename = "uploaded.pdf"

    # 1️⃣ Save the uploaded PDF
    with open(pdf_filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 2️⃣ Run parsing pipeline with correct Python environment
    try:
        subprocess.run([python_executable, "pdf_toc_parser.py", pdf_filename, "USB PD Specification"], check=True)
        subprocess.run([python_executable, "pdf_section_parser.py", pdf_filename, "usb_pd_toc.jsonl"], check=True)
        subprocess.run([python_executable, "validation_report.py"], check=True)
    except subprocess.CalledProcessError as e:
        return {"error": f"Processing failed: {e}"}

    # 3️⃣ Load TOC results and return for frontend preview
    toc_file = "usb_pd_toc.jsonl"
    if os.path.exists(toc_file):
        with open(toc_file, "r", encoding="utf-8") as f:
            results = [json.loads(line) for line in f]
        return results  # send full list; frontend can paginate
    else:
        return {"error": "TOC file not found after processing"}

@app.get("/results")
def get_results():
    toc_file = "usb_pd_toc.jsonl"
    if os.path.exists(toc_file):
        with open(toc_file, "r", encoding="utf-8") as f:
            results = [json.loads(line) for line in f]
        return results
    else:
        return {"error": "Results file not found"}

@app.get("/download/{filename}")
def download_file(filename: str):
    # ✅ Security: Only allow specific filenames
    allowed_files = [
        "usb_pd_toc.jsonl",
        "usb_pd_spec.jsonl",
        "usb_pd_validation_report.xlsx"
    ]
    if filename not in allowed_files:
        return {"error": "File not allowed"}

    file_path = os.path.join(os.getcwd(), filename)
    if not os.path.exists(file_path):
        return {"error": "File not found"}

    # ✅ Force download in browser
    return FileResponse(
        file_path,
        media_type='application/octet-stream',
        filename=filename
    )
