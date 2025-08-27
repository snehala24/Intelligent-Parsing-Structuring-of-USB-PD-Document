"""
validation_report.py
--------------------
Validates parsed JSONL against TOC, producing Excel report:
- Section counts, mismatches, gaps, order errors
- Table counts (if present), extra info
Requires: pandas, openpyxl
"""
import json
import pandas as pd
import re

def load_jsonl(filename):
    data = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():  # Skip empty lines
                    data.append(json.loads(line))
    except FileNotFoundError:
        print(f"Error: {filename} not found")
        return pd.DataFrame()
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON in {filename}: {e}")
        return pd.DataFrame()
    return pd.DataFrame(data)

def detect_order_errors(toc_ids, parsed_ids):
    """Detect order errors between TOC and parsed sections"""
    order_errors = []
    for i, toc_id in enumerate(toc_ids):
        if toc_id in parsed_ids:
            parsed_idx = parsed_ids.index(toc_id)
            if parsed_idx != i:
                order_errors.append(
                    f"Section {toc_id} at position {parsed_idx}, expected {i}"
                )
    return order_errors


def count_tables_in_content(sections_df):
    """Count tables in section content"""
    table_re = r"(?i)(table\s+\d+)"  # Case insensitive
    parsed_tables = 0
    
    if 'content' in sections_df.columns:
        for content in sections_df['content']:
            if isinstance(content, str):
                matches = re.findall(table_re, content)
                parsed_tables += len(matches)
    
    return parsed_tables


def calculate_content_metrics(sections_df):
    """Calculate content-related metrics"""
    if 'content' not in sections_df.columns:
        return 0, 0
    
    avg_content_length = sections_df['content'].str.len().mean()
    empty_content_count = sections_df['content'].isna().sum()
    
    return avg_content_length, empty_content_count


def compare_toc_and_sections(toc_df, sections_df):
    """Compare TOC and sections with reduced complexity"""
    # Compare section_ids and order
    toc_ids = toc_df['section_id'].tolist()
    parsed_ids = sections_df['section_id'].tolist()
    
    missing = list(set(toc_ids) - set(parsed_ids))
    extra = list(set(parsed_ids) - set(toc_ids))
    order_errors = detect_order_errors(toc_ids, parsed_ids)
    
    # Count tables in TOC titles
    toc_tables = 0
    if 'title' in toc_df.columns:
        toc_tables = toc_df['title'].str.contains(
            'Table', case=False, na=False
        ).sum()
    
    # Count tables in section content
    parsed_tables = count_tables_in_content(sections_df)
    
    # Calculate content metrics
    avg_content_length, empty_content_count = calculate_content_metrics(sections_df)
    
    results = [{
        "toc_section_count": len(toc_ids),
        "parsed_section_count": len(parsed_ids),
        "toc_table_count": toc_tables,
        "parsed_table_count": parsed_tables,
        "missing_sections": missing,
        "extra_sections": extra,
        "order_errors": order_errors,
        "gaps": missing,  # Keep for backward compatibility
        "matched": len(missing) == 0 and len(extra) == 0 and len(order_errors) == 0,
        "avg_content_length": avg_content_length,
        "empty_content_sections": empty_content_count
    }]
    
    return pd.DataFrame(results)

def generate_detailed_report(toc_df, sections_df, validation_df):
    """Generate detailed comparison report"""
    with pd.ExcelWriter(
        'usb_pd_validation_report.xlsx', 
        engine='openpyxl'
    ) as writer:
        # Main validation summary
        validation_df.to_excel(
            writer, 
            sheet_name='Validation Summary', 
            index=False
        )
        
        # Section-by-section comparison
        if not toc_df.empty and not sections_df.empty:
            comparison = pd.merge(
                toc_df[['section_id', 'title', 'page', 'level']], 
                sections_df[['section_id', 'title', 'page', 'level']], 
                on='section_id', 
                how='outer', 
                suffixes=('_toc', '_parsed')
            )
            comparison.to_excel(
                writer, 
                sheet_name='Section Comparison', 
                index=False
            )
        
        # Content statistics
        if 'content' in sections_df.columns:
            content_stats = pd.DataFrame({
                'section_id': sections_df['section_id'],
                'title': sections_df['title'],
                'content_length': sections_df['content'].str.len(),
                'has_content': sections_df['content'].notna() & (sections_df['content'] != ''),
                'word_count': sections_df['content'].str.split().str.len()
            })
            content_stats.to_excel(
                writer, 
                sheet_name='Content Statistics', 
                index=False
            )

if __name__ == '__main__':
    print("Loading JSONL files...")
    toc_df = load_jsonl('usb_pd_toc.jsonl')
    sections_df = load_jsonl('usb_pd_spec.jsonl')
    
    if toc_df.empty or sections_df.empty:
        print("Error: Could not load required JSONL files")
        exit(1)
    
    print("Comparing TOC and sections...")
    validation = compare_toc_and_sections(toc_df, sections_df)
    
    print("Generating detailed report...")
    generate_detailed_report(toc_df, sections_df, validation)
    
    print("Validation report saved as 'usb_pd_validation_report.xlsx'.")
    
    # Print summary
    if not validation.empty:
        result = validation.iloc[0]
        print(f"\n📊 VALIDATION SUMMARY:")
        print(f"TOC Sections: {result['toc_section_count']}")
        print(f"Parsed Sections: {result['parsed_section_count']}")
        print(f"Missing: {len(result['missing_sections'])}")
        print(f"Extra: {len(result['extra_sections'])}")
        print(f"Order Errors: {len(result['order_errors'])}")
        status = '✅ PERFECT' if result['matched'] else '❌ ISSUES FOUND'
        print(f"Match Status: {status}")