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

def load_jsonl(filename):
    data = []
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line))
    return pd.DataFrame(data)

def compare_toc_and_sections(toc_df, sections_df):
    results = []
    # Compare section_ids and order
    toc_ids = toc_df['section_id'].tolist()
    parsed_ids = sections_df['section_id'].tolist()
    missing = list(set(toc_ids) - set(parsed_ids))
    extra = list(set(parsed_ids) - set(toc_ids))
    order_errors = [i+1 for i in range(len(toc_ids)-1) if toc_ids[i+1] not in parsed_ids[max(0,i-1):i+2]]
    
    # Table/count detection via regex (simple heuristic)
    table_re = r"(Table\s+\d+)"
    toc_tables = toc_df['title'].str.contains('Table').sum()
    parsed_tables = sections_df['content'].str.contains(table_re).sum()

    results.append({
        "toc_section_count": len(toc_ids),
        "parsed_section_count": len(parsed_ids),
        "toc_table_count": toc_tables,
        "parsed_table_count": parsed_tables,
        "missing_sections": missing,
        "extra_sections": extra,
        "order_errors": order_errors,
        "gaps": missing,
        "matched": len(missing)==0 and len(extra)==0 and len(order_errors)==0
    })
    return pd.DataFrame(results)

if __name__ == '__main__':
    toc_df = load_jsonl('usb_pd_toc.jsonl')
    sections_df = load_jsonl('usb_pd_spec.jsonl')
    validation = compare_toc_and_sections(toc_df, sections_df)
    validation.to_excel('usb_pd_validation_report.xlsx', index=False)
    print("Validation report saved as 'usb_pd_validation_report.xlsx'.")

