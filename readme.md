# USB Power Delivery Specification Parsing & Structuring System

## **Project Overview**
This project extracts, parses, and structures the **USB Power Delivery (USB PD) Specification** PDF into **JSONL format** and produces a **validation report** to ensure accuracy.

It was developed as part of a professional assignment to demonstrate **document parsing, PDF data extraction, JSON structuring, and validation skills**.

---

## **Objectives**
- Extract the **Table of Contents (TOC)** hierarchy from the USB PD specification PDF  
- Parse **all sections** and their content into structured JSONL  
- Maintain **hierarchical relationships**, **page mappings**, and **metadata**  
- **Validate** TOC vs parsed sections and output an **Excel report**  
- Achieve **90%+ accuracy** in extraction — final run achieved **100% match** ✅  

---

## **Folder Structure**
project_folder/
├── pdf_toc_parser.py # Extracts TOC from PDF and saves to JSONL
├── pdf_section_parser.py # Parses all sections based on TOC and saves content
├── validation_report.py # Validates TOC vs parsed sections, saves Excel report
├── jsonl_schema.py # JSONL schema definitions for TOC and Section files
├── usb_pd_spec.pdf # The USB PD Specification PDF (input)
├── usb_pd_toc.jsonl # Output: TOC hierarchy JSONL
├── usb_pd_spec.jsonl # Output: Complete sections JSONL
├── usb_pd_metadata.jsonl # Output: Document metadata
├── usb_pd_validation_report.xlsx # Output: Excel validation report
└── README.md # Project documentation


---

## **Installation & Setup**
1. **Install Python 3.8+**
2. **Install required libraries**:
pip install pdfplumber pandas openpyxl tqdm

3. Place the **USB PD PDF** (`usb_pd_spec.pdf`) in this project folder.

---

## **Usage Guide**

### **Step 1 → Extract TOC**
python pdf_toc_parser.py usb_pd_spec.pdf "USB Power Delivery Specification Rev 3.2 v1.1"

Generates:  
- `usb_pd_toc.jsonl`  
- `usb_pd_metadata.jsonl`  

---

### **Step 2 → Parse Sections**

python pdf_section_parser.py usb_pd_spec.pdf usb_pd_toc.jsonl

Generates:  
- `usb_pd_spec.jsonl` (TOC + section content)

---

### **Step 3 → Validate**


python validation_report.py

Generates:  
- `usb_pd_validation_report.xlsx`

---

### **Step 4 → View JSONL Schema**

python jsonl_schema.py

Prints the schema for TOC and section JSONL files.

---

## **Validation Success**
Your validation results were:

| Metric                | Value |
|-----------------------|-------|
| toc_section_count     | 250   |
| parsed_section_count  | 250   |
| missing_sections      | []    |
| extra_sections        | []    |
| order_errors          | []    |
| matched               | TRUE  |

✅ **Perfect Match** — No missing, extra, or out-of-order sections.

---

## **Deliverables**
- `usb_pd_toc.jsonl` → Clean TOC with hierarchy ✅  
- `usb_pd_spec.jsonl` → Parsed sections + content ✅  
- `usb_pd_metadata.jsonl` → Document metadata ✅  
- `usb_pd_validation_report.xlsx` → Structural validation report ✅  
- All scripts with schema & instructions ✅  
- `README.md` with complete usage guide ✅  

---

## **Features**
- **Clean TOC extraction** with:
  - Correct `section_id`, `title`, `page`, `level`, `parent_id`
  - Skips front matter (revision history, lists)
  - Avoids duplicates & OCR noise
- **Section text parsing** with start-end page detection  
- **Validation** of count/order/gaps/tables  
- **Metadata tracking**  
- **Modular, reusable code** with clear separation of steps  
- **Extensible** for NLP tagging or semantic search  

---

## **Requirements**
- Python 3.8+
- pdfplumber
- pandas
- openpyxl
- tqdm


---

## **Author**
**Snehala A**  
B.Tech AIML  
Sri Shakthi Institute of Engineering and Technology  

*Done by Snehala A*
