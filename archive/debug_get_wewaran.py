#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(__file__))

from numerology_utils import get_wewaran
import pandas as pd

def debug_get_wewaran():
    print("=== Debug get_wewaran function ===")
    
    # Test specific case
    result = get_wewaran('Sadwara', 5)
    print(f"get_wewaran('Sadwara', 5) = '{result}'")
    
    # Check Excel directly
    excel_path = '/Users/baktanarta/Documents/numerulogi/desk_wewaran.xlsx'
    if os.path.exists(excel_path):
        df = pd.read_excel(excel_path, engine='openpyxl')
        
        print(f"\nExcel file loaded: {len(df)} rows")
        
        # Check specific row
        match = df[(df['kategori'] == 'Sadwara') & (df['nilai'] == 5)]
        print(f"Direct Excel query for Sadwara nilai=5:")
        print(match)
        
        if not match.empty:
            nama = match.iloc[0]['nama']
            print(f"Found nama: '{nama}' (type: {type(nama)})")
            print(f"Stripped nama: '{str(nama).strip()}'")
        
        # Check all Sadwara entries
        print(f"\nAll Sadwara entries:")
        sadwara_all = df[df['kategori'] == 'Sadwara']
        for _, row in sadwara_all.iterrows():
            print(f"  nilai={row['nilai']}, nama='{row['nama']}' (type: {type(row['nama'])})")

if __name__ == "__main__":
    debug_get_wewaran()
