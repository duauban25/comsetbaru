#!/usr/bin/env python3

def test_formulas_16011962():
    print("=== MENCARI RUMUS YANG BENAR UNTUK 16/01/1962 ===")
    
    # Data untuk 16/01/1962
    neptu_hari = 3  # Selasa
    neptu_pas = 9   # Pahing
    wuku_num = 10   # Sungsang
    day_idx = 2     # Selasa (0=Minggu, 1=Senin, 2=Selasa)
    hari_name = 'Selasa'
    
    print(f"Data: Selasa Pahing, Wuku Sungsang (#10), Day Index: {day_idx}")
    print(f"Neptu: {neptu_hari} + {neptu_pas} = {neptu_hari + neptu_pas}")
    
    # Expected results
    expected = {
        'Caturwara': 'Laba',    # Expected: Laba (index 1)
        'Astawara': 'Indra',    # Expected: Indra (index 2) 
        'Sangawara': 'Dadi'     # Expected: Dadi (index 8)
    }
    
    # Mapping arrays
    caturwara_names = ['Sri', 'Laba', 'Jaya', 'Mandala']
    astawara_names = ['Sri', 'Indra', 'Guru', 'Yama', 'Ludra', 'Brahma', 'Kala', 'Uma']
    sangawara_names = ['Dangu', 'Jangur', 'Gigis', 'Nohan', 'Ogan', 'Erangan', 'Urungan', 'Tulus', 'Dadi']
    
    print(f"\n=== TESTING CATURWARA FORMULAS ===")
    print(f"Expected: {expected['Caturwara']} (index {caturwara_names.index(expected['Caturwara'])})")
    
    # Test different Caturwara formulas
    w0 = max(0, wuku_num - 1)
    
    formulas_catur = [
        ("((w0 * 7) + 1 + day_idx) % 4", ((w0 * 7) + 1 + day_idx) % 4),
        ("((w0 * 7) + day_idx) % 4", ((w0 * 7) + day_idx) % 4),
        ("(wuku_num + day_idx) % 4", (wuku_num + day_idx) % 4),
        ("(neptu_total) % 4", (neptu_hari + neptu_pas) % 4),
        ("(w0 + day_idx) % 4", (w0 + day_idx) % 4),
        ("((w0 * 7) + day_idx + 1) % 4", ((w0 * 7) + day_idx + 1) % 4),
    ]
    
    for formula, result in formulas_catur:
        name = caturwara_names[result] if result < len(caturwara_names) else f"Index_{result}"
        match = "✓" if name == expected['Caturwara'] else "✗"
        print(f"{match} {formula} = {result} → {name}")
    
    print(f"\n=== TESTING ASTAWARA FORMULAS ===")
    print(f"Expected: {expected['Astawara']} (index {astawara_names.index(expected['Astawara'])})")
    
    # Test different Astawara formulas
    formulas_asta = [
        ("((w0 * 7) + 1 + day_idx) % 8 + 1", (((w0 * 7) + 1 + day_idx) % 8) + 1),
        ("((w0 * 7) + day_idx) % 8 + 1", (((w0 * 7) + day_idx) % 8) + 1),
        ("(wuku_num + day_idx) % 8 + 1", ((wuku_num + day_idx) % 8) + 1),
        ("(neptu_total) % 8 + 1", ((neptu_hari + neptu_pas) % 8) + 1),
        ("(w0 + day_idx) % 8 + 1", ((w0 + day_idx) % 8) + 1),
        ("((w0 * 7) + day_idx + 1) % 8 + 1", (((w0 * 7) + day_idx + 1) % 8) + 1),
    ]
    
    for formula, result in formulas_asta:
        result_idx = result - 1  # Convert to 0-based index
        name = astawara_names[result_idx] if 0 <= result_idx < len(astawara_names) else f"Index_{result_idx}"
        match = "✓" if name == expected['Astawara'] else "✗"
        print(f"{match} {formula} = {result} (idx {result_idx}) → {name}")
    
    print(f"\n=== TESTING SANGAWARA FORMULAS ===")
    print(f"Expected: {expected['Sangawara']} (index {sangawara_names.index(expected['Sangawara'])})")
    
    # Test different Sangawara formulas
    formulas_sang = [
        ("((w0 * 7) + day_idx) % 9", ((w0 * 7) + day_idx) % 9),
        ("((w0 * 7) + 1 + day_idx) % 9", ((w0 * 7) + 1 + day_idx) % 9),
        ("(wuku_num + day_idx) % 9", (wuku_num + day_idx) % 9),
        ("(neptu_total) % 9", (neptu_hari + neptu_pas) % 9),
        ("(w0 + day_idx) % 9", (w0 + day_idx) % 9),
        ("((w0 * 7) + day_idx + 1) % 9", ((w0 * 7) + day_idx + 1) % 9),
        ("((w0 * 7) + day_idx + 6) % 9", ((w0 * 7) + day_idx + 6) % 9),
    ]
    
    for formula, result in formulas_sang:
        name = sangawara_names[result] if result < len(sangawara_names) else f"Index_{result}"
        match = "✓" if name == expected['Sangawara'] else "✗"
        print(f"{match} {formula} = {result} → {name}")

if __name__ == "__main__":
    test_formulas_16011962()
