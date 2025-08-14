import re
import pdfplumber

def extract_toc_from_pdf(pdf_path, doc_title):
    toc_entries = []
    seen = set()  # to avoid duplicates
    toc_text = ''

    # Read first ~20 pages (covers full TOC in USB PD spec)
    with pdfplumber.open(pdf_path) as pdf:
        for i in range(min(20, len(pdf.pages))):
            page = pdf.pages[i]
            text = page.extract_text() or ''
            toc_text += '\n' + text

    lines = [l.strip() for l in toc_text.split('\n') if l.strip()]

    # Flexible patterns
    full_line_re = re.compile(r'^(\d+(\.\d+)*)(?:\s+)(.+?)(?:\.{2,}\s*|\s+)(\d+)$')
    num_only_re = re.compile(r'^(\d+(\.\d+)*)$')
    title_page_re = re.compile(r'^(.+?)(?:\.{2,}\s*|\s+)(\d+)$')

    prev_num = None
    skip_keywords = [
        "revision", "errata", "initial release", "figure",
        "table of contents", "list of tables", "list of figures"
    ]

    for line in lines:
        m_full = full_line_re.match(line)
        if m_full:
            sec_id = m_full.group(1)
            title = m_full.group(3).strip()
            page_no = int(m_full.group(4))

            # Skip junk pages & front matter
            if page_no < 1 or page_no > 2000:
                continue
            if any(kw in title.lower() for kw in skip_keywords):
                continue

            level = sec_id.count('.') + 1
            parent = sec_id.rsplit('.', 1)[0] if '.' in sec_id else None
            key = (sec_id, page_no)
            if key in seen:
                continue
            seen.add(key)

            toc_entries.append({
                "doc_title": doc_title,
                "section_id": sec_id,
                "title": title,
                "full_path": f"{sec_id} {title}",
                "page": page_no,
                "level": level,
                "parent_id": parent,
                "tags": []
            })
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
                sec_id = prev_num
                title = m_title_page.group(1).strip()
                page_no = int(m_title_page.group(2))

                if page_no < 1 or page_no > 2000:
                    prev_num = None
                    continue
                if any(kw in title.lower() for kw in skip_keywords):
                    prev_num = None
                    continue

                level = sec_id.count('.') + 1
                parent = sec_id.rsplit('.', 1)[0] if '.' in sec_id else None
                key = (sec_id, page_no)
                if key in seen:
                    prev_num = None
                    continue
                seen.add(key)

                toc_entries.append({
                    "doc_title": doc_title,
                    "section_id": sec_id,
                    "title": title,
                    "full_path": f"{sec_id} {title}",
                    "page": page_no,
                    "level": level,
                    "parent_id": parent,
                    "tags": []
                })

            prev_num = None

    return toc_entries

if __name__ == "__main__":
    import sys, json
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
