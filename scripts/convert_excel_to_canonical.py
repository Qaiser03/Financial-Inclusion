"""Utility script to convert existing Excel files to canonical CSV/TXT format"""

import pandas as pd
import sys
from pathlib import Path

def convert_scopus_excel_to_csv(excel_path: str, output_path: str):
    """Convert Scopus Excel export to CSV"""
    print(f"Reading {excel_path}...")
    df = pd.read_excel(excel_path)
    print(f"Found {len(df)} records")
    
    print(f"Writing to {output_path}...")
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"Conversion complete!")

def convert_wos_excel_to_txt(excel_path: str, output_path: str):
    """Convert Web of Science Excel export to tab-delimited TXT"""
    print(f"Reading {excel_path}...")
    df = pd.read_excel(excel_path)
    print(f"Found {len(df)} records")
    
    print(f"Writing to {output_path}...")
    df.to_csv(output_path, sep='\t', index=False, encoding='utf-8')
    print(f"Conversion complete!")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python convert_excel_to_canonical.py <excel_file> <output_file> [scopus|wos]")
        print("\nExample:")
        print("  python convert_excel_to_canonical.py scopus.xlsx data/raw/scopus_fi.csv scopus")
        print("  python convert_excel_to_canonical.py WoS.xlsx data/raw/wos_fi.txt wos")
        sys.exit(1)
    
    excel_path = sys.argv[1]
    output_path = sys.argv[2]
    file_type = sys.argv[3] if len(sys.argv) > 3 else 'scopus'
    
    # Create output directory if needed
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    if file_type.lower() == 'scopus':
        convert_scopus_excel_to_csv(excel_path, output_path)
    elif file_type.lower() == 'wos':
        convert_wos_excel_to_txt(excel_path, output_path)
    else:
        print(f"Unknown file type: {file_type}. Use 'scopus' or 'wos'")
        sys.exit(1)
