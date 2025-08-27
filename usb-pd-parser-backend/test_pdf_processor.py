"""
test_pdf_processor.py
---------------------
Unit tests for the PDF processor classes.
Improves code reliability and ensures functionality.
"""
import unittest
from unittest.mock import Mock, patch, mock_open
import json
from pdf_processor import PDFProcessor, TOCExtractor, SectionParser, SectionValidator


class TestTOCExtractor(unittest.TestCase):
    """Test cases for TOCExtractor class"""
    
    def setUp(self):
        self.extractor = TOCExtractor("test.pdf", "Test Document")
    
    def test_is_valid_toc_entry_valid(self):
        """Test valid TOC entry validation"""
        result = self.extractor._is_valid_toc_entry("1.2.3", "Valid Section", 50)
        self.assertTrue(result)
    
    def test_is_valid_toc_entry_invalid_page(self):
        """Test invalid page number validation"""
        result = self.extractor._is_valid_toc_entry("1.2.3", "Valid Section", 0)
        self.assertFalse(result)
        
        result = self.extractor._is_valid_toc_entry("1.2.3", "Valid Section", 3000)
        self.assertFalse(result)
    
    def test_is_valid_toc_entry_skip_keywords(self):
        """Test skip keywords validation"""
        result = self.extractor._is_valid_toc_entry("1.2.3", "Revision History", 50)
        self.assertFalse(result)
        
        result = self.extractor._is_valid_toc_entry("1.2.3", "Table of Contents", 50)
        self.assertFalse(result)
    
    def test_create_toc_entry(self):
        """Test TOC entry creation"""
        entry = self.extractor._create_toc_entry("1.2.3", "Test Section", 50)
        
        expected = {
            "doc_title": "Test Document",
            "section_id": "1.2.3",
            "title": "Test Section",
            "full_path": "1.2.3 Test Section",
            "page": 50,
            "level": 3,
            "parent_id": "1.2",
            "tags": []
        }
        
        self.assertEqual(entry, expected)
    
    def test_create_toc_entry_top_level(self):
        """Test top-level TOC entry creation"""
        entry = self.extractor._create_toc_entry("1", "Test Section", 50)
        
        self.assertEqual(entry["level"], 1)
        self.assertIsNone(entry["parent_id"])


class TestSectionValidator(unittest.TestCase):
    """Test cases for SectionValidator class"""
    
    def test_validate_section_fields_valid(self):
        """Test valid section field validation"""
        section = {
            "doc_title": "Test",
            "section_id": "1.2.3",
            "title": "Test Section",
            "full_path": "1.2.3 Test Section",
            "page": 50,
            "level": 3,
            "parent_id": "1.2",
            "tags": [],
            "content": "Test content"
        }
        
        result = SectionValidator._validate_section_fields(section)
        self.assertIsNone(result)
    
    def test_validate_section_fields_missing(self):
        """Test missing section field validation"""
        section = {
            "doc_title": "Test",
            "section_id": "1.2.3",
            "title": "Test Section",
            # Missing required fields
        }
        
        result = SectionValidator._validate_section_fields(section)
        self.assertIsNotNone(result)
        self.assertIn("missing fields", result)
    
    def test_validate_section_data_types_valid(self):
        """Test valid section data type validation"""
        section = {
            "section_id": "1.2.3",
            "page": 50,
            "level": 3
        }
        
        result = SectionValidator._validate_section_data_types(section)
        self.assertEqual(result, [])
    
    def test_validate_section_data_types_invalid(self):
        """Test invalid section data type validation"""
        section = {
            "section_id": "1.2.3",
            "page": -1,  # Invalid page
            "level": 0   # Invalid level
        }
        
        result = SectionValidator._validate_section_data_types(section)
        self.assertEqual(len(result), 2)
        self.assertIn("invalid page number", result[0])
        self.assertIn("invalid level", result[1])


class TestSectionParser(unittest.TestCase):
    """Test cases for SectionParser class"""
    
    def setUp(self):
        self.toc_entries = [
            {
                "section_id": "1.1",
                "title": "Test Section 1",
                "page": 10
            },
            {
                "section_id": "1.2", 
                "title": "Test Section 2",
                "page": 15
            }
        ]
        self.parser = SectionParser("test.pdf", self.toc_entries)
    
    def test_clean_content_empty(self):
        """Test cleaning empty content"""
        result = self.parser._clean_content("")
        self.assertEqual(result, "")
        
        result = self.parser._clean_content(None)
        self.assertEqual(result, "")
    
    def test_clean_content_whitespace(self):
        """Test cleaning excessive whitespace"""
        input_text = "Line 1\n\n\n\nLine 2\n\n\nLine 3"
        result = self.parser._clean_content(input_text)
        self.assertNotIn("\n\n\n", result)
    
    def test_clean_content_headers(self):
        """Test cleaning page headers"""
        input_text = "Universal Serial Bus Power Delivery Specification v1.1\nContent here\nPage 10\nMore content"
        result = self.parser._clean_content(input_text)
        self.assertNotIn("Universal Serial Bus Power Delivery Specification", result)
        self.assertNotIn("Page 10", result)


class TestPDFProcessor(unittest.TestCase):
    """Test cases for PDFProcessor class"""
    
    def setUp(self):
        self.processor = PDFProcessor("test.pdf", "Test Document")
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dumps')
    def test_save_to_jsonl(self, mock_json_dumps, mock_file):
        """Test saving data to JSONL format"""
        mock_json_dumps.return_value = '{"test": "data"}'
        
        test_data = [{"test": "data"}]
        self.processor._save_to_jsonl(test_data, "test.jsonl")
        
        mock_file.assert_called_once_with("test.jsonl", 'w', encoding='utf-8')
        mock_json_dumps.assert_called_once_with({"test": "data"}, ensure_ascii=False)
    
    def test_parse_sections_without_toc(self):
        """Test parsing sections without TOC"""
        with self.assertRaises(ValueError):
            self.processor.parse_sections()


if __name__ == '__main__':
    unittest.main()
