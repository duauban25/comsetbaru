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

def verify_date_16011962():
    print("=== VERIFIKASI PERHITUNGAN WEWARAN: 16/01/1962 ===")
    
    test_date = "1962-01-16"
    print(f"Tanggal test: {test_date} (16/01/1962)")
    
    # Hitung Weton
    weton_info = weton_calculation(test_date)
    if not weton_info:
        print("ERROR: Gagal menghitung weton")
        return
    
    hari_name = weton_info.get('hari', '')
    pasaran_name = weton_info.get('pasaran', '')
    wuku_name = weton_info.get('wuku', '')
    neptu_total = weton_info.get('neptu', 0)
    
    print(f"\nHasil Weton:")
    print(f"  Hari: {hari_name}")
    print(f"  Pasaran: {pasaran_name}")
    print(f"  Neptu Total: {neptu_total}")
    print(f"  Wuku: {wuku_name}")
    
    # Hitung neptu individual
    neptu_hari = {'Senin':4,'Selasa':3,'Rabu':7,'Kamis':8,'Jumat':6,'Sabtu':9,'Minggu':5}.get(hari_name, 0)
    neptu_pas = {'Legi':5,'Pahing':9,'Pon':7,'Wage':4,'Kliwon':8}.get(pasaran_name, 0)
    
    print(f"  Neptu Hari: {neptu_hari}")
    print(f"  Neptu Pasaran: {neptu_pas}")
    print(f"  Total: {neptu_hari + neptu_pas}")
    
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
    
    print(f"  Wuku Number: {wuku_num}")
    print(f"  Day Index: {day_idx}")
    
    print(f"\n=== PERHITUNGAN WEWARAN ===")
    
    # Expected results from manual calculation
    expected = {
        'Ekawara': '-',
        'Dwiwara': 'Menga',
        'Triwara': 'Kajeng',
        'Caturwara': 'Laba',
        'Sadawara': 'Maulu',
        'Astawara': 'Indra',
        'Sangawara': 'Dadi',
        'Dasawara': 'Suka'
    }
    
    # Calculate using our functions
    calculated = {}
    
    # Ekawara
    try:
        calculated['Ekawara'] = calculate_ekawara(neptu_hari, neptu_pas)
    except Exception as e:
        calculated['Ekawara'] = f"ERROR: {e}"
    
    # Dwiwara
    try:
        calculated['Dwiwara'] = calculate_dwiwara(neptu_hari, neptu_pas)
    except Exception as e:
        calculated['Dwiwara'] = f"ERROR: {e}"
    
    # Triwara
    try:
        calculated['Triwara'] = calculate_triwara(wuku_num, day_idx)
    except Exception as e:
        calculated['Triwara'] = f"ERROR: {e}"
    
    # Caturwara
    try:
        calculated['Caturwara'] = calculate_caturwara(wuku_num, day_idx, hari_name)
    except Exception as e:
        calculated['Caturwara'] = f"ERROR: {e}"
    
    # Sadawara
    try:
        calculated['Sadawara'] = calculate_sadwara(wuku_num, day_idx)
    except Exception as e:
        calculated['Sadawara'] = f"ERROR: {e}"
    
    # Astawara
    try:
        calculated['Astawara'] = calculate_astawara(wuku_num, day_idx, hari_name)
    except Exception as e:
        calculated['Astawara'] = f"ERROR: {e}"
    
    # Sangawara
    try:
        calculated['Sangawara'] = calculate_sangawara(wuku_num, day_idx)
    except Exception as e:
        calculated['Sangawara'] = f"ERROR: {e}"
    
    # Dasawara
    try:
        calculated['Dasawara'] = calculate_dasawara(neptu_hari, neptu_pas)
    except Exception as e:
        calculated['Dasawara'] = f"ERROR: {e}"
    
    # Compare results
    print(f"{'Wewaran':<12} {'Expected':<12} {'Calculated':<12} {'Match'}")
    print("-" * 50)
    
    all_match = True
    for wewaran_type in ['Ekawara', 'Dwiwara', 'Triwara', 'Caturwara', 'Sadawara', 'Astawara', 'Sangawara', 'Dasawara']:
        exp = expected[wewaran_type]
        calc = calculated[wewaran_type]
        
        # Special handling for Ekawara
        if wewaran_type == 'Ekawara' and exp == '-':
            match = "?" if calc != '-' else "✓"
        else:
            match = "✓" if exp.lower() == calc.lower() else "✗"
            if match == "✗":
                all_match = False
        
        print(f"{wewaran_type:<12} {exp:<12} {calc:<12} {match}")
    
    print("\n=== DETAIL PERHITUNGAN MANUAL ===")
    
    # Manual calculation details
    print(f"Neptu Total: {neptu_hari} + {neptu_pas} = {neptu_hari + neptu_pas}")
    
    # Ekawara calculation
    ekawara_calc = (neptu_hari + neptu_pas) % 2
    print(f"Ekawara: ({neptu_hari} + {neptu_pas}) % 2 = {ekawara_calc}")
    print(f"  → Nilai {ekawara_calc} = {'Void' if ekawara_calc == 0 else 'Luang'}")
    print(f"  → Expected: '-' (mungkin tidak ada Ekawara untuk kombinasi ini?)")
    
    # Dwiwara calculation  
    dwiwara_calc = (neptu_hari + neptu_pas) % 2
    print(f"Dwiwara: ({neptu_hari} + {neptu_pas}) % 2 = {dwiwara_calc}")
    print(f"  → Nilai {dwiwara_calc} = {'Menga' if dwiwara_calc == 0 else 'Pepet'}")
    
    # Triwara calculation
    triwara_calc = (max(0, wuku_num - 1) + day_idx) % 3
    print(f"Triwara: ({wuku_num - 1} + {day_idx}) % 3 = {triwara_calc}")
    print(f"  → Nilai {triwara_calc} = {['Pasah', 'Beteng', 'Kajeng'][triwara_calc]}")
    
    # Caturwara calculation
    w0 = max(0, wuku_num - 1)
    if wuku_num <= 11 and hari_name.lower() != 'senin':
        caturwara_calc = ((w0 * 7) + 1 + day_idx) % 4
        print(f"Caturwara: (({w0} * 7) + 1 + {day_idx}) % 4 = {caturwara_calc} (wuku <= 11, bukan Senin)")
    else:
        caturwara_calc = ((w0 * 7) + day_idx) % 4
        print(f"Caturwara: (({w0} * 7) + {day_idx}) % 4 = {caturwara_calc}")
    print(f"  → Nilai {caturwara_calc} = {['Sri', 'Laba', 'Jaya', 'Mandala'][caturwara_calc]}")
    
    # Sadawara calculation
    sadawara_calc = (max(0, wuku_num - 1) + day_idx) % 6
    print(f"Sadawara: ({wuku_num - 1} + {day_idx}) % 6 = {sadawara_calc}")
    print(f"  → Nilai {sadawara_calc} = {['Tungleh', 'Aryang', 'Urukung', 'Paniron', 'Was', 'Maulu'][sadawara_calc]}")
    
    # Astawara calculation
    if wuku_num <= 11 and hari_name.lower() != 'senin':
        astawara_calc = ((w0 * 7) + 1 + day_idx) % 8
        print(f"Astawara: (({w0} * 7) + 1 + {day_idx}) % 8 = {astawara_calc} (wuku <= 11, bukan Senin)")
    else:
        astawara_calc = ((w0 * 7) + day_idx) % 8
        print(f"Astawara: (({w0} * 7) + {day_idx}) % 8 = {astawara_calc}")
    astawara_calc += 1  # Astawara uses 1..8
    print(f"  → Nilai {astawara_calc} = {['', 'Sri', 'Indra', 'Guru', 'Yama', 'Ludra', 'Brahma', 'Kala', 'Uma'][astawara_calc]}")
    
    # Sangawara calculation
    sangawara_calc = ((max(0, wuku_num - 1) * 7) + day_idx) % 9
    print(f"Sangawara: (({wuku_num - 1} * 7) + {day_idx}) % 9 = {sangawara_calc}")
    print(f"  → Nilai {sangawara_calc} = {['Dangu', 'Jangur', 'Gigis', 'Nohan', 'Ogan', 'Erangan', 'Urungan', 'Tulus', 'Dadi'][sangawara_calc]}")
    
    # Dasawara calculation
    dasawara_calc = (neptu_hari + neptu_pas) % 10
    print(f"Dasawara: ({neptu_hari} + {neptu_pas}) % 10 = {dasawara_calc}")
    print(f"  → Nilai {dasawara_calc} = {['Pandita', 'Pati', 'Suka', 'Duka', 'Sri', 'Manuh', 'Manusa', 'Raja', 'Dewa', 'Raksasa'][dasawara_calc]}")
    
    if all_match:
        print(f"\n✅ SEMUA PERHITUNGAN COCOK!")
    else:
        print(f"\n❌ ADA PERBEDAAN PERHITUNGAN - perlu disesuaikan")

if __name__ == "__main__":
    verify_date_16011962()
