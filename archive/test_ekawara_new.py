#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(__file__))

from numerology_utils import calculate_ekawara

def test_ekawara_new_logic():
    print("=== TEST EKAWARA NEW LOGIC ===")
    print("Aturan: Ekawara = (Neptu_hari + neptu_pasaran)")
    print("- Jika hasil GENAP = '' (kosong)")
    print("- Jika hasil GANJIL = 'Luang'")
    print()
    
    # Test cases
    test_cases = [
        # (neptu_hari, neptu_pas, hari, pasaran, expected)
        (3, 9, "Selasa", "Pahing", ""),      # 3+9=12 (genap) → ""
        (4, 8, "Senin", "Kliwon", ""),       # 4+8=12 (genap) → ""
        (5, 7, "Minggu", "Pon", ""),         # 5+7=12 (genap) → ""
        (6, 9, "Jumat", "Pahing", "Luang"),  # 6+9=15 (ganjil) → "Luang"
        (4, 5, "Senin", "Legi", "Luang"),    # 4+5=9 (ganjil) → "Luang"
        (7, 4, "Rabu", "Wage", "Luang"),     # 7+4=11 (ganjil) → "Luang"
        (9, 5, "Sabtu", "Legi", ""),         # 9+5=14 (genap) → ""
    ]
    
    print(f"{'Hari':<8} {'Pasaran':<8} {'Neptu':<6} {'Total':<6} {'Expected':<8} {'Result':<8} {'Status'}")
    print("-" * 65)
    
    all_correct = True
    for neptu_hari, neptu_pas, hari, pasaran, expected in test_cases:
        total = neptu_hari + neptu_pas
        result = calculate_ekawara(neptu_hari, neptu_pas)
        
        # Handle empty string display
        expected_display = expected if expected else "''"
        result_display = result if result else "''"
        
        status = "✓" if result == expected else "✗"
        if status == "✗":
            all_correct = False
        
        print(f"{hari:<8} {pasaran:<8} {neptu_hari}+{neptu_pas}  {total:<6} {expected_display:<8} {result_display:<8} {status}")
    
    print(f"\n{'='*65}")
    
    # Test dengan tanggal 16/01/1962
    print(f"\nTEST KHUSUS: 16/01/1962")
    print(f"Selasa Pahing: neptu_hari=3, neptu_pas=9")
    print(f"Total: 3 + 9 = 12 (genap)")
    
    result_1962 = calculate_ekawara(3, 9)
    expected_1962 = ""  # Genap = kosong
    result_display = result_1962 if result_1962 else "''"
    expected_display = expected_1962 if expected_1962 else "''"
    
    print(f"Expected: {expected_display}")
    print(f"Result: {result_display}")
    print(f"Status: {'✓' if result_1962 == expected_1962 else '✗'}")
    
    if result_1962 == expected_1962:
        print("✅ Sesuai dengan aturan manual: 16/01/1962 → Ekawara kosong")
    else:
        print("❌ Tidak sesuai dengan aturan manual")
        all_correct = False
    
    print(f"\n{'='*65}")
    if all_correct:
        print("🎉 SEMUA TEST EKAWARA BERHASIL!")
        print("✅ Fungsi Ekawara sudah sesuai dengan aturan manual")
    else:
        print("❌ Ada test yang gagal, perlu perbaikan")

if __name__ == "__main__":
    test_ekawara_new_logic()
