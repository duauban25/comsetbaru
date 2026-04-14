#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(__file__))

from numerology_utils import (
    calculate_ekawara,
    calculate_dwiwara,
    calculate_triwara,
    calculate_caturwara,
    calculate_sadwara,
    calculate_astawara,
    calculate_sangawara,
    calculate_dasawara,
    weton_calculation
)
import pandas as pd

def final_test():
    print("=== FINAL TEST: Wewaran Integration with Excel ===")
    
    # Test dengan beberapa tanggal
    test_dates = ["1990-01-01", "1985-12-25", "2000-06-15"]
    
    for test_date in test_dates:
        print(f"\n--- Testing date: {test_date} ---")
        
        weton_info = weton_calculation(test_date)
        if not weton_info:
            print("Failed to calculate weton")
            continue
            
        hari_name = weton_info.get('hari', '')
        pasaran_name = weton_info.get('pasaran', '')
        wuku_name = weton_info.get('wuku', '')
        
        # Calculate neptu values
        neptu_hari = {'Senin':4,'Selasa':3,'Rabu':7,'Kamis':8,'Jumat':6,'Sabtu':9,'Minggu':5}.get(hari_name, 0)
        neptu_pas = {'Legi':5,'Pahing':9,'Pon':7,'Wage':4,'Kliwon':8}.get(pasaran_name, 0)
        
        # Get wuku number
        wuku_names = ['Sinta','Landep','Ukir','Kulantir','Tolu','Gumbreg','Wariga','Warigadian','Julungwangi','Sungsang','Dungulan','Kuningan','Langkir','Medangsia','Pujut','Pahang','Kurulu','Merakih','Tambir','Medangkungan','Matal','Uye','Menail','Prangbakat','Bala','Ugu','Wayang','Kulawu','Dukut','Watugunung']
        try:
            wuku_num = wuku_names.index(wuku_name.capitalize()) + 1 if wuku_name else 1
        except ValueError:
            wuku_num = 1
        
        # Day index
        day_order = ['Minggu','Senin','Selasa','Rabu','Kamis','Jumat','Sabtu']
        try:
            day_idx = day_order.index(hari_name.capitalize())
        except ValueError:
            day_idx = 0
        
        print(f"Weton: {hari_name} {pasaran_name} (Neptu: {neptu_hari + neptu_pas})")
        print(f"Wuku: {wuku_name} (#{wuku_num}), Day index: {day_idx}")
        
        # Calculate all Wewaran
        wewaran_results = []
        
        try:
            ekawara = calculate_ekawara(neptu_hari, neptu_pas)
            wewaran_results.append(('Ekawara', ekawara))
        except Exception as e:
            wewaran_results.append(('Ekawara', f'ERROR: {e}'))
        
        try:
            dwiwara = calculate_dwiwara(neptu_hari, neptu_pas)
            wewaran_results.append(('Dwiwara', dwiwara))
        except Exception as e:
            wewaran_results.append(('Dwiwara', f'ERROR: {e}'))
        
        try:
            triwara = calculate_triwara(wuku_num, day_idx)
            wewaran_results.append(('Triwara', triwara))
        except Exception as e:
            wewaran_results.append(('Triwara', f'ERROR: {e}'))
        
        try:
            caturwara = calculate_caturwara(wuku_num, day_idx, hari_name)
            wewaran_results.append(('Caturwara', caturwara))
        except Exception as e:
            wewaran_results.append(('Caturwara', f'ERROR: {e}'))
        
        try:
            sadwara = calculate_sadwara(wuku_num, day_idx)
            wewaran_results.append(('Sadwara', sadwara))
        except Exception as e:
            wewaran_results.append(('Sadwara', f'ERROR: {e}'))
        
        try:
            astawara = calculate_astawara(wuku_num, day_idx, hari_name)
            wewaran_results.append(('Astawara', astawara))
        except Exception as e:
            wewaran_results.append(('Astawara', f'ERROR: {e}'))
        
        try:
            sangawara = calculate_sangawara(wuku_num, day_idx)
            wewaran_results.append(('Sangawara', sangawara))
        except Exception as e:
            wewaran_results.append(('Sangawara', f'ERROR: {e}'))
        
        try:
            dasawara = calculate_dasawara(neptu_hari, neptu_pas)
            wewaran_results.append(('Dasawara', dasawara))
        except Exception as e:
            wewaran_results.append(('Dasawara', f'ERROR: {e}'))
        
        # Display results
        print("Wewaran Results:")
        for wewaran_type, result in wewaran_results:
            print(f"  {wewaran_type}: {result}")
        
        # Check if we can find descriptions from Excel
        excel_path = '/Users/baktanarta/Documents/numerulogi/desk_wewaran.xlsx'
        if os.path.exists(excel_path):
            df = pd.read_excel(excel_path, engine='openpyxl')
            print("\nWith descriptions from Excel:")
            for wewaran_type, result in wewaran_results:
                if not result.startswith('ERROR'):
                    # Find matching description
                    match = df[(df['kategori'] == wewaran_type) & (df['nama'].str.lower() == result.lower())]
                    if not match.empty:
                        desc = match.iloc[0]['deskripsi']
                        print(f"  {wewaran_type}: {result} → {desc}")
                    else:
                        print(f"  {wewaran_type}: {result} → No description found")

if __name__ == "__main__":
    final_test()
