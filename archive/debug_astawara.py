#!/usr/bin/env python3

def debug_astawara():
    print("=== DEBUG ASTAWARA UNTUK 16/01/1962 ===")
    
    # Data untuk 16/01/1962
    wuku_num = 10   # Sungsang
    day_idx = 2     # Selasa
    w0 = max(0, wuku_num - 1)  # 9
    
    print(f"wuku_num: {wuku_num}")
    print(f"day_idx: {day_idx}")
    print(f"w0: {w0}")
    
    astawara_names = ['Sri', 'Indra', 'Guru', 'Yama', 'Ludra', 'Brahma', 'Kala', 'Uma']
    expected = 'Indra'  # index 1
    expected_idx = astawara_names.index(expected)
    
    print(f"Expected: {expected} (index {expected_idx})")
    
    # Test berbagai rumus
    formulas = [
        ("((w0 * 7) + day_idx) % 8 + 1", ((w0 * 7) + day_idx) % 8 + 1),
        ("((w0 * 7) + day_idx + 1) % 8 + 1", ((w0 * 7) + day_idx + 1) % 8 + 1),
        ("((w0 * 7) + day_idx - 1) % 8 + 1", ((w0 * 7) + day_idx - 1) % 8 + 1),
        ("(wuku_num + day_idx) % 8 + 1", (wuku_num + day_idx) % 8 + 1),
        ("(w0 + day_idx) % 8 + 1", (w0 + day_idx) % 8 + 1),
        ("((w0 * 7) + day_idx + 6) % 8 + 1", ((w0 * 7) + day_idx + 6) % 8 + 1),
    ]
    
    print(f"\nTesting formulas:")
    for formula, result in formulas:
        result_idx = result - 1  # Convert to 0-based index
        if 0 <= result_idx < len(astawara_names):
            name = astawara_names[result_idx]
            match = "✓" if name == expected else "✗"
            print(f"{match} {formula} = {result} (idx {result_idx}) → {name}")
        else:
            print(f"✗ {formula} = {result} (idx {result_idx}) → OUT_OF_RANGE")
    
    # Manual calculation step by step
    print(f"\nManual calculation:")
    print(f"w0 * 7 = {w0} * 7 = {w0 * 7}")
    print(f"(w0 * 7) + day_idx = {w0 * 7} + {day_idx} = {w0 * 7 + day_idx}")
    print(f"((w0 * 7) + day_idx) % 8 = {w0 * 7 + day_idx} % 8 = {(w0 * 7 + day_idx) % 8}")
    print(f"Result + 1 = {(w0 * 7 + day_idx) % 8} + 1 = {(w0 * 7 + day_idx) % 8 + 1}")
    
    # Reverse calculation - what value should give us Indra?
    print(f"\nReverse calculation:")
    print(f"To get {expected} (index {expected_idx}), we need result = {expected_idx + 1}")
    print(f"So ((w0 * 7) + day_idx + offset) % 8 + 1 = {expected_idx + 1}")
    print(f"((w0 * 7) + day_idx + offset) % 8 = {expected_idx}")
    print(f"({w0 * 7} + {day_idx} + offset) % 8 = {expected_idx}")
    print(f"({w0 * 7 + day_idx} + offset) % 8 = {expected_idx}")
    
    # Find the offset
    current_mod = (w0 * 7 + day_idx) % 8
    needed_offset = (expected_idx - current_mod) % 8
    print(f"Current mod: {current_mod}")
    print(f"Needed offset: {needed_offset}")
    
    # Verify
    test_result = ((w0 * 7) + day_idx + needed_offset) % 8 + 1
    test_idx = test_result - 1
    test_name = astawara_names[test_idx] if 0 <= test_idx < len(astawara_names) else "OUT_OF_RANGE"
    print(f"Verification: ((w0 * 7) + day_idx + {needed_offset}) % 8 + 1 = {test_result} → {test_name}")

if __name__ == "__main__":
    debug_astawara()
