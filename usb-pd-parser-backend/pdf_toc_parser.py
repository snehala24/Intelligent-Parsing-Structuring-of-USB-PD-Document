import re
import pdfplumber


def extract_toc_text(pdf_path, max_pages=20):
    """Extract text from first few pages of PDF for TOC analysis"""
    toc_text = ''
    
    with pdfplumber.open(pdf_path) as pdf:
        for i in range(min(max_pages, len(pdf.pages))):
            page = pdf.pages[i]
            text = page.extract_text() or ''
            toc_text += '\n' + text
    
    return [l.strip() for l in toc_text.split('\n') if l.strip()]


def is_valid_toc_entry(sec_id, title, page_no):
    """Validate if a TOC entry should be included"""
    # Skip junk pages & front matter
    if page_no < 1 or page_no > 2000:
        return False
    
    skip_keywords = [
        "revision", "errata", "initial release", "figure",
        "table of contents", "list of tables", "list of figures"
    ]
    
    if any(kw in title.lower() for kw in skip_keywords):
        return False
    
    return True


def create_toc_entry(doc_title, sec_id, title, page_no):
    """Create a standardized TOC entry dictionary"""
    level = sec_id.count('.') + 1
    parent = sec_id.rsplit('.', 1)[0] if '.' in sec_id else None
    
    return {
        "doc_title": doc_title,
        "section_id": sec_id,
        "title": title,
        "full_path": f"{sec_id} {title}",
        "page": page_no,
        "level": level,
        "parent_id": parent,
        "tags": []
    }


def parse_full_line_match(match, doc_title, seen):
    """Parse a full line match from regex"""
    sec_id = match.group(1)
    title = match.group(3).strip()
    page_no = int(match.group(4))
    
    if not is_valid_toc_entry(sec_id, title, page_no):
        return None
    
    key = (sec_id, page_no)
    if key in seen:
        return None
    
    seen.add(key)
    return create_toc_entry(doc_title, sec_id, title, page_no)


def parse_title_page_match(prev_num, match, doc_title, seen):
    """Parse a title+page match from regex"""
    sec_id = prev_num
    title = match.group(1).strip()
    page_no = int(match.group(2))
    
    if not is_valid_toc_entry(sec_id, title, page_no):
        return None
    
    key = (sec_id, page_no)
    if key in seen:
        return None
    
    seen.add(key)
    return create_toc_entry(doc_title, sec_id, title, page_no)


def extract_toc_from_pdf(pdf_path, doc_title):
    """Extract table of contents from PDF with reduced complexity"""
    toc_entries = []
    seen = set()  # to avoid duplicates
    
    # Extract text from PDF
    lines = extract_toc_text(pdf_path)
    
    # Compile regex patterns
    full_line_re = re.compile(
        r'^(\d+(\.\d+)*)(?:\s+)(.+?)(?:\.{2,}\s*|\s+)(\d+)$'
    )
    num_only_re = re.compile(r'^(\d+(\.\d+)*)$')
    title_page_re = re.compile(r'^(.+?)(?:\.{2,}\s*|\s+)(\d+)$')
    
    prev_num = None
    
    for line in lines:
        # Try full line match first
        m_full = full_line_re.match(line)
        if m_full:
            entry = parse_full_line_match(m_full, doc_title, seen)
            if entry:
                toc_entries.append(entry)
            prev_num = None
            continue
        
        # Handle number-only lines
        m_num = num_only_re.match(line)
        if m_num:
            prev_num = m_num.group(1)
            continue
        
        # Handle title+page after number line
        if prev_num:
            m_title_page = title_page_re.match(line)
            if m_title_page:
                entry = parse_title_page_match(
                    prev_num, m_title_page, doc_title, seen
                )
                if entry:
                    toc_entries.append(entry)
            prev_num = None
    
    return toc_entries


if __name__ == "__main__":
    import sys
    import json
    
    if len(sys.argv) < 3:
        print("Usage: python pdf_toc_parser.py <pdf_file> <document_title>")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    doc_title = sys.argv[2]
    
    toc_entries = extract_toc_from_pdf(pdf_file, doc_title)
    
    # Save to JSONL
    with open("usb_pd_toc.jsonl", "w", encoding="utf-8") as f:
        for obj in toc_entries:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")
    
    # Metadata file
    meta = {
        "doc_title": doc_title,
        "section_count": len(toc_entries)
    }
    with open("usb_pd_metadata.jsonl", "w", encoding="utf-8") as f:
        f.write(json.dumps(meta, ensure_ascii=False) + "\n")
    
    print(f"✅ Extracted {len(toc_entries)} TOC entries.")
    print("💾 Saved to usb_pd_toc.jsonl and usb_pd_metadata.jsonl")
