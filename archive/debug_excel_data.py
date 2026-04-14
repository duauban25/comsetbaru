#!/usr/bin/env python3

import pandas as pd
import os

def debug_excel_data():
    excel_path = '/Users/baktanarta/Documents/numerulogi/desk_wewaran.xlsx'
    if os.path.exists(excel_path):
        df = pd.read_excel(excel_path, engine='openpyxl')
        
        print("=== EKAWARA DATA ===")
        ekawara_data = df[df['kategori'] == 'Ekawara']
        print(ekawara_data.to_string())
        
        print("\n=== SADAWARA DATA ===")
        sadawara_data = df[df['kategori'] == 'Sadawara']
        print(sadawara_data.to_string())
        
        print("\n=== ALL CATEGORIES AND THEIR NILAI RANGES ===")
        for cat in df['kategori'].unique():
            cat_data = df[df['kategori'] == cat]
            nilai_list = sorted(cat_data['nilai'].tolist())
            print(f"{cat}: {nilai_list}")

if __name__ == "__main__":
    debug_excel_data()
