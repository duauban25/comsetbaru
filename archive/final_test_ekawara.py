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

def final_test_with_corrected_ekawara():
    print("=== FINAL TEST: WEWARAN DENGAN EKAWARA YANG DIPERBAIKI ===")
    
    # Test case: 16/01/1962
    test_date = "1962-01-16"
    expected_results = {
        'Ekawara': '',         # Genap (12) → kosong
        'Dwiwara': 'Menga',
        'Triwara': 'Kajeng',
        'Caturwara': 'Laba',
        'Sadawara': 'Maulu',
        'Astawara': 'Indra',
        'Sangawara': 'Dadi',
        'Dasawara': 'Suka'
    }
    
    print(f"Test Date: {test_date} (16/01/1962)")
    
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
    
    print(f"Weton: {hari_name} {pasaran_name} (Neptu: {neptu_hari + neptu_pas})")
    print(f"Wuku: {wuku_name} (#{wuku_num})")
    
    # Calculate all Wewaran
    calculations = [
        ('Ekawara', lambda: calculate_ekawara(neptu_hari, neptu_pas)),
        ('Dwiwara', lambda: calculate_dwiwara(neptu_hari, neptu_pas)),
        ('Triwara', lambda: calculate_triwara(wuku_num, day_idx)),
        ('Caturwara', lambda: calculate_caturwara(wuku_num, day_idx, hari_name)),
        ('Sadawara', lambda: calculate_sadwara(wuku_num, day_idx)),
        ('Astawara', lambda: calculate_astawara(wuku_num, day_idx, hari_name)),
        ('Sangawara', lambda: calculate_sangawara(wuku_num, day_idx)),
        ('Dasawara', lambda: calculate_dasawara(neptu_hari, neptu_pas)),
    ]
    
    print(f"\n{'Wewaran':<12} {'Expected':<12} {'Calculated':<12} {'Status'}")
    print("-" * 50)
    
    all_correct = True
    for wewaran_type, calc_func in calculations:
        try:
            calculated = calc_func()
            expected = expected_results[wewaran_type]
            
            # Handle empty string display
            expected_display = expected if expected else "''"
            calculated_display = calculated if calculated else "''"
            
            status = "✓" if calculated == expected else "✗"
            if status == "✗":
                all_correct = False
            
            print(f"{wewaran_type:<12} {expected_display:<12} {calculated_display:<12} {status}")
            
        except Exception as e:
            print(f"{wewaran_type:<12} {expected_results[wewaran_type]:<12} {'ERROR':<12} ✗")
            print(f"  Error: {e}")
            all_correct = False
    
    print(f"\n{'='*50}")
    
    # Test additional cases for Ekawara
    print(f"\nTEST TAMBAHAN EKAWARA:")
    ekawara_test_cases = [
        ("Jumat Pahing", 6, 9, "Luang"),     # 6+9=15 (ganjil) → "Luang"
        ("Senin Legi", 4, 5, "Luang"),       # 4+5=9 (ganjil) → "Luang"
        ("Rabu Wage", 7, 4, "Luang"),        # 7+4=11 (ganjil) → "Luang"
        ("Sabtu Legi", 9, 5, ""),            # 9+5=14 (genap) → ""
    ]
    
    for case_name, nh, np, expected_eka in ekawara_test_cases:
        result_eka = calculate_ekawara(nh, np)
        total = nh + np
        
        expected_display = expected_eka if expected_eka else "''"
        result_display = result_eka if result_eka else "''"
        status = "✓" if result_eka == expected_eka else "✗"
        
        print(f"  {case_name}: {nh}+{np}={total} → {expected_display} (got {result_display}) {status}")
    
    if all_correct:
        print(f"\n🎉 SEMUA PERHITUNGAN WEWARAN SUDAH BENAR!")
        print(f"✅ Ekawara: Genap = kosong, Ganjil = 'Luang'")
        print(f"✅ Sistem siap digunakan untuk aplikasi web")
    else:
        print(f"\n❌ Masih ada perhitungan yang perlu diperbaiki")
    
    print(f"\nCatatan Ekawara:")
    print(f"- Neptu Total 12 (genap) → Ekawara kosong ('')")
    print(f"- Sesuai dengan aturan manual: '-' = kosong")
    print(f"- Formula: (neptu_hari + neptu_pasaran) % 2")
    print(f"  - Genap (0) → '' (kosong)")
    print(f"  - Ganjil (1) → 'Luang'")

if __name__ == "__main__":
    final_test_with_corrected_ekawara()
