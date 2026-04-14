#!/usr/bin/env python3

# Test script untuk memverifikasi Wewaran calculations dengan Excel
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
    weton_calculation,
    get_wewaran
)
import pandas as pd

def test_excel_integration():
    print("=== Testing Excel Integration ===")
    
    # Load Excel file
    excel_path = '/Users/baktanarta/Documents/numerulogi/desk_wewaran.xlsx'
    if os.path.exists(excel_path):
        df = pd.read_excel(excel_path, engine='openpyxl')
        print(f"Excel loaded: {len(df)} rows")
        
        # Test get_wewaran function with Excel data
        print("\n=== Testing get_wewaran with Excel ===")
        for _, row in df.head(10).iterrows():
            kategori = row['kategori']
            nilai = row['nilai']
            expected_nama = row['nama']
            
            result = get_wewaran(kategori, nilai)
            match = "✓" if result.lower() == expected_nama.lower() else "✗"
            print(f"{match} {kategori}[{nilai}]: Expected='{expected_nama}', Got='{result}'")
    
    print("\n=== Testing Full Calculation ===")
    # Test dengan data sample
    test_date = "1990-01-01"
    weton_info = weton_calculation(test_date)
    
    if weton_info:
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
        
        print(f"Date: {test_date}")
        print(f"Weton: {hari_name} {pasaran_name} (Neptu: {neptu_hari + neptu_pas})")
        print(f"Wuku: {wuku_name} (#{wuku_num})")
        print(f"Day index: {day_idx}")
        
        # Test using the actual calculation functions
        print(f"\n=== Wewaran Results (using calculation functions) ===")
        try:
            ekawara = calculate_ekawara(neptu_hari, neptu_pas)
            print(f"Ekawara: {ekawara}")
        except Exception as e:
            print(f"Ekawara: ERROR - {e}")
        
        try:
            dwiwara = calculate_dwiwara(neptu_hari, neptu_pas)
            print(f"Dwiwara: {dwiwara}")
        except Exception as e:
            print(f"Dwiwara: ERROR - {e}")
        
        try:
            triwara = calculate_triwara(wuku_num, day_idx)
            print(f"Triwara: {triwara}")
        except Exception as e:
            print(f"Triwara: ERROR - {e}")
        
        try:
            caturwara = calculate_caturwara(wuku_num, day_idx, hari_name)
            print(f"Caturwara: {caturwara}")
        except Exception as e:
            print(f"Caturwara: ERROR - {e}")
        
        try:
            sadwara = calculate_sadwara(wuku_num, day_idx)
            print(f"Sadwara: {sadwara}")
        except Exception as e:
            print(f"Sadwara: ERROR - {e}")
        
        try:
            astawara = calculate_astawara(wuku_num, day_idx, hari_name)
            print(f"Astawara: {astawara}")
        except Exception as e:
            print(f"Astawara: ERROR - {e}")
        
        try:
            sangawara = calculate_sangawara(wuku_num, day_idx)
            print(f"Sangawara: {sangawara}")
        except Exception as e:
            print(f"Sangawara: ERROR - {e}")
        
        try:
            dasawara = calculate_dasawara(neptu_hari, neptu_pas)
            print(f"Dasawara: {dasawara}")
        except Exception as e:
            print(f"Dasawara: ERROR - {e}")
        
        # Calculate all Wewaran with nilai for Excel lookup
        calculations = [
            ('Ekawara', 1),  # Always 1 based on Excel
            ('Dwiwara', (neptu_hari + neptu_pas) % 2),
            ('Triwara', (max(0, wuku_num - 1) + day_idx) % 3),
            ('Caturwara', ((max(0, wuku_num - 1) * 7) + day_idx) % 4),
            ('Sadawara', (max(0, wuku_num - 1) + day_idx) % 6),
            ('Astawara', (((max(0, wuku_num - 1) * 7) + day_idx) % 8) + 1),
            ('Sangawara', ((max(0, wuku_num - 1) * 7) + day_idx) % 9),
            ('Dasawara', (neptu_hari + neptu_pas) % 10),
        ]
        
        print(f"\n=== Wewaran Results ===")
        for wewaran_type, calc_nilai in calculations:
            nama = get_wewaran(wewaran_type, calc_nilai)
            
            # Try to find description from Excel
            desc = "No description"
            if os.path.exists(excel_path):
                match = df[(df['kategori'] == wewaran_type) & (df['nilai'] == calc_nilai)]
                if not match.empty:
                    desc = match.iloc[0]['deskripsi']
            
            print(f"{wewaran_type}[{calc_nilai}]: {nama}")
            print(f"  → {desc}")

if __name__ == "__main__":
    test_excel_integration()
