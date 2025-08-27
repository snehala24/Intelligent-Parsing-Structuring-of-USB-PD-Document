"""
pdf_processor.py
----------------
Class-based PDF processing system for USB PD specification parsing.
Addresses OOP principles and improves code organization.
"""
import pdfplumber
import json
import re
from typing import List, Dict, Optional, Tuple
from tqdm import tqdm


class PDFProcessor:
    """Main class for PDF processing operations"""
    
    def __init__(self, pdf_path: str, doc_title: str):
        self.pdf_path = pdf_path
        self.doc_title = doc_title
        self.toc_entries = []
        self.sections = []
    
    def extract_toc(self) -> List[Dict]:
        """Extract table of contents from PDF"""
        toc_extractor = TOCExtractor(self.pdf_path, self.doc_title)
        self.toc_entries = toc_extractor.extract()
        return self.toc_entries
    
    def parse_sections(self) -> List[Dict]:
        """Parse sections based on TOC entries"""
        if not self.toc_entries:
            raise ValueError("TOC must be extracted before parsing sections")
        
        section_parser = SectionParser(self.pdf_path, self.toc_entries)
        self.sections = section_parser.parse()
        return self.sections
    
    def save_toc_to_jsonl(self, filename: str = "usb_pd_toc.jsonl"):
        """Save TOC entries to JSONL file"""
        self._save_to_jsonl(self.toc_entries, filename)
    
    def save_sections_to_jsonl(self, filename: str = "usb_pd_spec.jsonl"):
        """Save sections to JSONL file"""
        self._save_to_jsonl(self.sections, filename)
    
    def _save_to_jsonl(self, data: List[Dict], filename: str):
        """Generic method to save data to JSONL format"""
        with open(filename, 'w', encoding='utf-8') as f:
            for obj in data:
                f.write(json.dumps(obj, ensure_ascii=False) + '\n')


class TOCExtractor:
    """Handles table of contents extraction"""
    
    def __init__(self, pdf_path: str, doc_title: str):
        self.pdf_path = pdf_path
        self.doc_title = doc_title
        self.seen = set()
    
    def extract(self) -> List[Dict]:
        """Extract TOC entries from PDF"""
        lines = self._extract_toc_text()
        return self._parse_toc_lines(lines)
    
    def _extract_toc_text(self, max_pages: int = 20) -> List[str]:
        """Extract text from first few pages of PDF for TOC analysis"""
        toc_text = ''
        
        with pdfplumber.open(self.pdf_path) as pdf:
            for i in range(min(max_pages, len(pdf.pages))):
                page = pdf.pages[i]
                text = page.extract_text() or ''
                toc_text += '\n' + text
        
        return [l.strip() for l in toc_text.split('\n') if l.strip()]
    
    def _parse_toc_lines(self, lines: List[str]) -> List[Dict]:
        """Parse TOC lines into structured entries"""
        toc_entries = []
        
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
                entry = self._parse_full_line_match(m_full)
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
                    entry = self._parse_title_page_match(prev_num, m_title_page)
                    if entry:
                        toc_entries.append(entry)
                prev_num = None
        
        return toc_entries
    
    def _is_valid_toc_entry(self, sec_id: str, title: str, page_no: int) -> bool:
        """Validate if a TOC entry should be included"""
        if page_no < 1 or page_no > 2000:
            return False
        
        skip_keywords = [
            "revision", "errata", "initial release", "figure",
            "table of contents", "list of tables", "list of figures"
        ]
        
        if any(kw in title.lower() for kw in skip_keywords):
            return False
        
        return True
    
    def _create_toc_entry(self, sec_id: str, title: str, page_no: int) -> Dict:
        """Create a standardized TOC entry dictionary"""
        level = sec_id.count('.') + 1
        parent = sec_id.rsplit('.', 1)[0] if '.' in sec_id else None
        
        return {
            "doc_title": self.doc_title,
            "section_id": sec_id,
            "title": title,
            "full_path": f"{sec_id} {title}",
            "page": page_no,
            "level": level,
            "parent_id": parent,
            "tags": []
        }
    
    def _parse_full_line_match(self, match) -> Optional[Dict]:
        """Parse a full line match from regex"""
        sec_id = match.group(1)
        title = match.group(3).strip()
        page_no = int(match.group(4))
        
        if not self._is_valid_toc_entry(sec_id, title, page_no):
            return None
        
        key = (sec_id, page_no)
        if key in self.seen:
            return None
        
        self.seen.add(key)
        return self._create_toc_entry(sec_id, title, page_no)
    
    def _parse_title_page_match(self, prev_num: str, match) -> Optional[Dict]:
        """Parse a title+page match from regex"""
        sec_id = prev_num
        title = match.group(1).strip()
        page_no = int(match.group(2))
        
        if not self._is_valid_toc_entry(sec_id, title, page_no):
            return None
        
        key = (sec_id, page_no)
        if key in self.seen:
            return None
        
        self.seen.add(key)
        return self._create_toc_entry(sec_id, title, page_no)


class SectionParser:
    """Handles section content parsing"""
    
    def __init__(self, pdf_path: str, toc_entries: List[Dict]):
        self.pdf_path = pdf_path
        self.toc_entries = toc_entries
    
    def parse(self) -> List[Dict]:
        """Parse section content based on TOC entries"""
        sections = []
        
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                total_pages = len(pdf.pages)
                
                for i, toc_entry in enumerate(tqdm(self.toc_entries, desc="Parsing sections")):
                    # pdfplumber zero-based
                    start_page = max(0, toc_entry['page'] - 1)
                    
                    # Determine end page for this section
                    if i + 1 < len(self.toc_entries):
                        end_page = min(self.toc_entries[i + 1]['page'] - 1, total_pages)
                    else:
                        end_page = total_pages
                    
                    # Extract content from page range
                    section_text = self._extract_page_range_content(
                        pdf, start_page, end_page, total_pages
                    )
                    
                    # Clean and prepare the entry
                    entry = toc_entry.copy()
                    entry['content'] = self._clean_content(section_text)
                    sections.append(entry)
                    
        except Exception as e:
            print(f"Error processing PDF: {e}")
            return []
        
        return sections
    
    def _extract_page_range_content(self, pdf, start_page: int, end_page: int, total_pages: int) -> str:
        """Extract content from a range of pages"""
        section_text = ""
        for page_idx in range(start_page, end_page):
            if page_idx < total_pages:
                page_text = pdf.pages[page_idx].extract_text() or ''
                section_text += page_text + '\n'
        return section_text
    
    def _clean_content(self, text: str) -> str:
        """Clean extracted text content"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
        # Remove page headers/footers (common patterns)
        text = re.sub(
            r'Universal Serial Bus Power Delivery Specification.*?\n', 
            '', 
            text
        )
        text = re.sub(r'Page \d+.*?\n', '', text)
        
        return text.strip()


class SectionValidator:
    """Handles section validation"""
    
    @staticmethod
    def validate_sections(sections: List[Dict]) -> Tuple[List[Dict], List[str]]:
        """Validate extracted sections"""
        valid_sections = []
        issues = []
        
        for section in sections:
            # Check required fields
            field_issue = SectionValidator._validate_section_fields(section)
            if field_issue:
                issues.append(field_issue)
                continue
            
            # Check data types
            type_issues = SectionValidator._validate_section_data_types(section)
            issues.extend(type_issues)
            
            valid_sections.append(section)
        
        return valid_sections, issues
    
    @staticmethod
    def _validate_section_fields(section: Dict) -> Optional[str]:
        """Validate required fields in a section"""
        required_fields = [
            'doc_title', 'section_id', 'title', 'full_path', 
            'page', 'level', 'parent_id', 'tags', 'content'
        ]
        missing_fields = [
            field for field in required_fields 
            if field not in section
        ]
        
        if missing_fields:
            return f"Section {section.get('section_id', 'unknown')}: missing fields {missing_fields}"
        return None
    
    @staticmethod
    def _validate_section_data_types(section: Dict) -> List[str]:
        """Validate data types in a section"""
        issues = []
        
        if not isinstance(section['page'], int) or section['page'] < 1:
            issues.append(f"Section {section['section_id']}: invalid page number")
            
        if not isinstance(section['level'], int) or section['level'] < 1:
            issues.append(f"Section {section['section_id']}: invalid level")
        
        return issues
