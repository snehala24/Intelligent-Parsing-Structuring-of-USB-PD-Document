"""
jsonl_schema.py
---------------
Defines the JSONL schema for TOC and document sections for reference and validation.
"""

toc_schema = {
    "doc_title": "string",
    "section_id": "string",
    "title": "string",
    "full_path": "string",
    "page": "integer",
    "level": "integer",
    "parent_id": "string or null",
    "tags": "list of string"
}

section_schema = {
    **toc_schema,
    "content": "string"
}

print("JSONL TOC schema:", toc_schema)
print("JSONL Section schema:", section_schema)


