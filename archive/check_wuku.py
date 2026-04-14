import pandas as pd

try:
    # Baca file Wuku_Urip.xlsx
    print("Membaca file Wuku_Urip.xlsx...")
    wuku_df = pd.read_excel('Wuku_Urip.xlsx')
    
    # Tampilkan informasi dasar
    print("\nInformasi file:")
    print(wuku_df.info())
    
    # Tampilkan beberapa baris pertama
    print("\nBeberapa baris pertama:")
    print(wuku_df.head())
    
    # Tampilkan nama kolom
    print("\nNama kolom:")
    print(wuku_df.columns.tolist())
    
except Exception as e:
    print(f"Error: {str(e)}")
