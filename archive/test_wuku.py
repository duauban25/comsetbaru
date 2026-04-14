from numerology_utils import get_wuku
from datetime import datetime

def test_wuku_calculation():
    """Test Wuku calculation with known dates"""
    test_cases = [
        # Reference date: July 8, 1633 (Sunday, Wuku Sinta)
        ('1633-07-08', 'Sinta'),
        # 7 days later should be next Wuku (Landep)
        ('1633-07-15', 'Landep'),
        # 30 weeks later should cycle back to Sinta
        ('1634-02-06', 'Sinta'),
        # September 11, 2025 (Wuku Sinta)
        ('2025-09-11', 'Sinta')
    ]
    
    print("=== Testing Wuku Calculation ===")
    for date_str, expected_wuku in test_cases:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        result = get_wuku(date_obj)
        wuku_name = result['nama_wuku'] if result else 'Error'
        status = "✓" if wuku_name == expected_wuku else f"✗ (expected: {expected_wuku})"
        print(f"Date: {date_str} | Wuku: {wuku_name} {status}")
        if result:
            print(f"   Details: {result.get('detail', 'No details')}")

if __name__ == "__main__":
    test_wuku_calculation()
