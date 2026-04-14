#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(__file__))

from numerology_utils import calculate_astawara, get_wewaran

def test_astawara_function():
    print("=== TEST ASTAWARA FUNCTION ===")
    
    # Data untuk 16/01/1962
    wuku_num = 10   # Sungsang
    day_idx = 2     # Selasa
    hari_name = 'Selasa'
    
    print(f"Input: wuku_num={wuku_num}, day_idx={day_idx}, hari_name='{hari_name}'")
    
    # Test calculate_astawara function
    result = calculate_astawara(wuku_num, day_idx, hari_name)
    print(f"calculate_astawara result: {result}")
    
    # Test get_wewaran directly
    w0 = max(0, wuku_num - 1)
    value = ((w0 * 7) + day_idx) % 8
    final_value = value + 1
    
    print(f"Manual calculation:")
    print(f"  w0 = {w0}")
    print(f"  ((w0 * 7) + day_idx) % 8 = (({w0} * 7) + {day_idx}) % 8 = {value}")
    print(f"  final_value = {value} + 1 = {final_value}")
    
    direct_result = get_wewaran('Astawara', final_value)
    print(f"get_wewaran('Astawara', {final_value}) = {direct_result}")
    
    # Check Excel data directly
    import pandas as pd
    excel_path = '/Users/baktanarta/Documents/numerulogi/desk_wewaran.xlsx'
    if os.path.exists(excel_path):
        df = pd.read_excel(excel_path, engine='openpyxl')
        astawara_data = df[df['kategori'] == 'Astawara']
        print(f"\nAstawara data from Excel:")
        print(astawara_data[['nilai', 'nama']].sort_values('nilai'))
        
        # Check specific value
        match = df[(df['kategori'] == 'Astawara') & (df['nilai'] == final_value)]
        if not match.empty:
            nama = match.iloc[0]['nama']
            print(f"\nExcel lookup for Astawara nilai={final_value}: {nama}")
        else:
            print(f"\nNo match found for Astawara nilai={final_value}")

if __name__ == "__main__":
    test_astawara_function()
