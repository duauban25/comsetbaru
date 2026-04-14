#!/usr/bin/env python3

# Test script to verify Wewaran calculations
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

def test_wewaran_calculations():
    print("Testing Wewaran calculations...")
    
    # Test with sample data
    test_date = "1990-01-01"
    weton_info = weton_calculation(test_date)
    
    print(f"Test date: {test_date}")
    print(f"Weton info: {weton_info}")
    
    if weton_info:
        hari_name = weton_info.get('hari', '')
        pasaran_name = weton_info.get('pasaran', '')
        wuku_name = weton_info.get('wuku', '')
        
        # Calculate neptu values
        neptu_hari = {'Senin':4,'Selasa':3,'Rabu':7,'Kamis':8,'Jumat':6,'Sabtu':9,'Minggu':5}.get(hari_name, 0)
        neptu_pas = {'Legi':5,'Pahing':9,'Pon':7,'Wage':4,'Kliwon':8}.get(pasaran_name, 0)
        
        # Get wuku number (simplified)
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
        
        print(f"\nCalculation inputs:")
        print(f"  neptu_hari: {neptu_hari}")
        print(f"  neptu_pas: {neptu_pas}")
        print(f"  wuku_num: {wuku_num}")
        print(f"  day_idx: {day_idx}")
        print(f"  hari_name: {hari_name}")
        
        # Test all Wewaran calculations
        print(f"\nWewaran calculations:")
        try:
            ekawara = calculate_ekawara(neptu_hari, neptu_pas)
            print(f"  Ekawara: {ekawara}")
        except Exception as e:
            print(f"  Ekawara: ERROR - {e}")
        
        try:
            dwiwara = calculate_dwiwara(neptu_hari, neptu_pas)
            print(f"  Dwiwara: {dwiwara}")
        except Exception as e:
            print(f"  Dwiwara: ERROR - {e}")
        
        try:
            triwara = calculate_triwara(wuku_num, day_idx)
            print(f"  Triwara: {triwara}")
        except Exception as e:
            print(f"  Triwara: ERROR - {e}")
        
        try:
            caturwara = calculate_caturwara(wuku_num, day_idx, hari_name)
            print(f"  Caturwara: {caturwara}")
        except Exception as e:
            print(f"  Caturwara: ERROR - {e}")
        
        try:
            sadwara = calculate_sadwara(wuku_num, day_idx)
            print(f"  Sadwara: {sadwara}")
        except Exception as e:
            print(f"  Sadwara: ERROR - {e}")
        
        try:
            astawara = calculate_astawara(wuku_num, day_idx, hari_name)
            print(f"  Astawara: {astawara}")
        except Exception as e:
            print(f"  Astawara: ERROR - {e}")
        
        try:
            sangawara = calculate_sangawara(wuku_num, day_idx)
            print(f"  Sangawara: {sangawara}")
        except Exception as e:
            print(f"  Sangawara: ERROR - {e}")
        
        try:
            dasawara = calculate_dasawara(neptu_hari, neptu_pas)
            print(f"  Dasawara: {dasawara}")
        except Exception as e:
            print(f"  Dasawara: ERROR - {e}")

if __name__ == "__main__":
    test_wewaran_calculations()
