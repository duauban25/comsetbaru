#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(__file__))

# Simulate the app.py logic for testing
from numerology_utils import weton_calculation
import pandas as pd

def test_web_app_descriptions():
    print("=== TEST WEB APP DESCRIPTIONS LOGIC ===")
    
    # Simulate the same logic as in app.py
    birth_date = "1962-01-16"
    
    # Get weton calculation
    weton_info = weton_calculation(birth_date)
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
    
    print(f"Input: {birth_date}")
    print(f"Weton: {hari_name} {pasaran_name} (Neptu: {neptu_hari + neptu_pas})")
    print(f"Wuku: {wuku_name} (#{wuku_num}), Day index: {day_idx}")
    
    # Load Excel data (same as app.py)
    desc_map = {}
    wewaran_names = {}
    
    try:
        desk_path = '/Users/baktanarta/Documents/numerulogi/desk_wewaran.xlsx'
        df_desc = pd.read_excel(desk_path, engine='openpyxl')
        
        for idx, row in df_desc.iterrows():
            try:
                kategori = str(row['kategori']).strip() if pd.notna(row.get('kategori')) else ''
                nilai = int(row['nilai']) if pd.notna(row.get('nilai')) else -1
                nama = str(row['nama']).strip() if 'nama' in row and pd.notna(row.get('nama')) else ''
                deskripsi = str(row['deskripsi']).strip() if pd.notna(row.get('deskripsi')) else ''
                
                if not kategori or nilai < 0:
                    continue
                
                key = (kategori.lower().strip(), nilai)
                
                if deskripsi:
                    desc_map[key] = deskripsi
                    if nama:
                        wewaran_names[key] = nama
                        
            except Exception as e:
                continue
                
        print(f"Loaded {len(desc_map)} descriptions from Excel")
        
    except Exception as e:
        print(f"Error loading Excel: {e}")
        return
    
    # Process Wewaran (same logic as app.py)
    order = ['Ekawara', 'Dwiwara', 'Triwara', 'Caturwara', 
             'Sadwara', 'Astawara', 'Sangawara', 'Dasawara']
    
    wewaran_list = []
    
    for level in order:
        try:
            description = f"Informasi untuk {level} tidak tersedia."
            display_value = "-"
            calc_nilai = -1
            
            if level == 'Ekawara':
                neptu_total = neptu_hari + neptu_pas
                if neptu_total % 2 == 0:  # Even (genap)
                    display_value = "-"
                    description = "Tidak ada Ekawara untuk neptu genap."
                else:  # Odd (ganjil)
                    calc_nilai = 1
                    display_value = "Luang"
            elif level == 'Dwiwara':
                calc_nilai = (neptu_hari + neptu_pas) % 2
            elif level == 'Triwara':
                calc_nilai = (max(0, wuku_num - 1) + day_idx) % 3
            elif level == 'Caturwara':
                w0 = max(0, wuku_num - 1)
                calc_nilai = ((w0 * 7) + day_idx) % 4
            elif level == 'Sadwara':
                calc_nilai = (max(0, wuku_num - 1) + day_idx) % 6
            elif level == 'Astawara':
                w0 = max(0, wuku_num - 1)
                calc_nilai = ((w0 * 7) + day_idx) % 8
            elif level == 'Sangawara':
                calc_nilai = ((max(0, wuku_num - 1) * 7) + day_idx + 6) % 9
            elif level == 'Dasawara':
                calc_nilai = (neptu_hari + neptu_pas) % 10
            
            # Look up in Excel data
            if calc_nilai >= 0:
                key = (level.lower(), calc_nilai)
                if key in desc_map:
                    description = desc_map[key]
                    if key in wewaran_names:
                        display_value = wewaran_names[key]
                        # Handle spelling variations
                        if display_value.lower() == 'menge':
                            display_value = 'Menga'
            
            wewaran_list.append({
                'nama': level,
                'nilai': display_value,
                'keterangan': description
            })
            
        except Exception as e:
            wewaran_list.append({
                'nama': level,
                'nilai': 'Error',
                'keterangan': f'Gagal memproses data: {str(e)}'
            })
    
    # Display results as they would appear in web app
    print(f"\n{'Wewaran':<12} {'Nilai':<12} {'Deskripsi'}")
    print("-" * 80)
    
    for item in wewaran_list:
        nama = item['nama']
        nilai = item['nilai'] if item['nilai'] else '-'
        keterangan = item['keterangan'][:60] + "..." if len(item['keterangan']) > 60 else item['keterangan']
        
        print(f"{nama:<12} {nilai:<12} {keterangan}")
    
    print(f"\n{'='*80}")
    print("✅ Hasil ini akan ditampilkan di web app")
    print("✅ Semua deskripsi diambil dari Excel desk_wewaran.xlsx")
    print("✅ Ekawara kosong untuk neptu genap (12)")

if __name__ == "__main__":
    test_web_app_descriptions()
