#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(__file__))

from numerology_utils import weton_calculation
import pandas as pd

def test_excel_descriptions():
    print("=== TEST EXCEL DESCRIPTIONS FOR 16/01/1962 ===")
    
    # Test date: 16/01/1962 (Selasa Pahing, Neptu 12)
    test_date = "1962-01-16"
    
    # Get Weton info
    weton_info = weton_calculation(test_date)
    if not weton_info:
        print("ERROR: Failed to calculate weton")
        return
    
    hari_name = weton_info.get('hari', '')
    pasaran_name = weton_info.get('pasaran', '')
    wuku_name = weton_info.get('wuku', '')
    
    # Calculate neptu values
    neptu_hari = {'Senin':4,'Selasa':3,'Rabu':7,'Kamis':8,'Jumat':6,'Sabtu':9,'Minggu':5}.get(hari_name, 0)
    neptu_pas = {'Legi':5,'Pahing':9,'Pon':7,'Wage':4,'Kliwon':8}.get(pasaran_name, 0)
    
    # Get wuku number and day index
    wuku_names = ['Sinta','Landep','Ukir','Kulantir','Tolu','Gumbreg','Wariga','Warigadian','Julungwangi','Sungsang','Dungulan','Kuningan','Langkir','Medangsia','Pujut','Pahang','Kurulu','Merakih','Tambir','Medangkungan','Matal','Uye','Menail','Prangbakat','Bala','Ugu','Wayang','Kulawu','Dukut','Watugunung']
    try:
        wuku_num = wuku_names.index(wuku_name.capitalize()) + 1 if wuku_name else 1
    except ValueError:
        wuku_num = 1
    
    day_order = ['Minggu','Senin','Selasa','Rabu','Kamis','Jumat','Sabtu']
    try:
        day_idx = day_order.index(hari_name.capitalize())
    except ValueError:
        day_idx = 0
    
    print(f"Date: {test_date}")
    print(f"Weton: {hari_name} {pasaran_name} (Neptu: {neptu_hari + neptu_pas})")
    print(f"Wuku: {wuku_name} (#{wuku_num}), Day index: {day_idx}")
    
    # Load Excel data
    excel_path = '/Users/baktanarta/Documents/numerulogi/desk_wewaran.xlsx'
    if not os.path.exists(excel_path):
        print(f"ERROR: Excel file not found: {excel_path}")
        return
    
    df = pd.read_excel(excel_path, engine='openpyxl')
    print(f"Excel loaded: {len(df)} rows")
    
    # Calculate nilai for each Wewaran type
    wewaran_calculations = [
        ('Ekawara', lambda: 1 if (neptu_hari + neptu_pas) % 2 == 1 else None),  # Odd = 1, Even = None
        ('Dwiwara', lambda: (neptu_hari + neptu_pas) % 2),
        ('Triwara', lambda: (max(0, wuku_num - 1) + day_idx) % 3),
        ('Caturwara', lambda: ((max(0, wuku_num - 1) * 7) + day_idx) % 4),
        ('Sadwara', lambda: (max(0, wuku_num - 1) + day_idx) % 6),
        ('Astawara', lambda: ((max(0, wuku_num - 1) * 7) + day_idx) % 8),
        ('Sangawara', lambda: ((max(0, wuku_num - 1) * 7) + day_idx + 6) % 9),
        ('Dasawara', lambda: (neptu_hari + neptu_pas) % 10),
    ]
    
    print(f"\n{'Wewaran':<12} {'Nilai':<6} {'Nama':<12} {'Deskripsi'}")
    print("-" * 80)
    
    for wewaran_type, calc_func in wewaran_calculations:
        try:
            calc_nilai = calc_func()
            
            if calc_nilai is None:  # Ekawara even case
                print(f"{wewaran_type:<12} {'None':<6} {'-':<12} Tidak ada Ekawara untuk neptu genap")
                continue
            
            # Look up in Excel
            match = df[(df['kategori'] == wewaran_type) & (df['nilai'] == calc_nilai)]
            
            if not match.empty:
                nama = str(match.iloc[0]['nama']).strip()
                deskripsi = str(match.iloc[0]['deskripsi']).strip()
                
                # Handle spelling variations
                if nama.lower() == 'menge':
                    nama = 'Menga'
                
                print(f"{wewaran_type:<12} {calc_nilai:<6} {nama:<12} {deskripsi[:60]}...")
            else:
                print(f"{wewaran_type:<12} {calc_nilai:<6} {'NOT_FOUND':<12} No Excel data for this nilai")
                
        except Exception as e:
            print(f"{wewaran_type:<12} {'ERROR':<6} {'ERROR':<12} {str(e)}")
    
    print(f"\n{'='*80}")
    print("✅ Semua deskripsi harus diambil dari Excel sesuai nilai yang dihitung")
    print("✅ Ekawara untuk neptu genap (12) = kosong/tidak ada")
    print("✅ Semua Wewaran lainnya harus memiliki deskripsi dari Excel")

if __name__ == "__main__":
    test_excel_descriptions()
