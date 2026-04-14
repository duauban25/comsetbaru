#!/usr/bin/env python3

import pandas as pd
import os

def check_excel_structure():
    try:
        file_path = '/Users/baktanarta/Documents/numerulogi/desk_wewaran.xlsx'
        
        if not os.path.exists(file_path):
            print(f"File tidak ditemukan: {file_path}")
            return
        
        # Baca file Excel
        df = pd.read_excel(file_path, engine='openpyxl')
        
        print("=== STRUKTUR FILE EXCEL desk_wewaran.xlsx ===")
        print(f"Jumlah baris: {len(df)}")
        print(f"Kolom yang tersedia: {list(df.columns)}")
        print()
        
        print("=== CONTOH DATA (5 baris pertama) ===")
        print(df.head().to_string())
        print()
        
        print("=== INFO KOLOM ===")
        for col in df.columns:
            print(f"- {col}: {df[col].dtype}")
            if df[col].dtype == 'object':
                unique_vals = df[col].unique()[:10]  # Ambil 10 nilai unik pertama
                print(f"  Contoh nilai: {unique_vals}")
        print()
        
        print("=== KATEGORI YANG TERSEDIA ===")
        if 'kategori' in df.columns or 'Kategori' in df.columns:
            kategori_col = 'kategori' if 'kategori' in df.columns else 'Kategori'
            categories = df[kategori_col].unique()
            print(f"Kategori: {categories}")
            
            for cat in categories:
                count = len(df[df[kategori_col] == cat])
                print(f"  - {cat}: {count} entries")
        
    except Exception as e:
        print(f"Error membaca file: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_excel_structure()
