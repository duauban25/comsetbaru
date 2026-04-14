import pandas as pd

try:
    # Baca file Pasaran.xlsx
    print("Membaca file Pasaran.xlsx...")
    pasaran_df = pd.read_excel('Pasaran.xlsx')
    
    # Tampilkan informasi dasar
    print("\nInformasi file:")
    print(pasaran_df.info())
    
    # Tampilkan beberapa baris pertama
    print("\nBeberapa baris pertama:")
    print(pasaran_df.head())
    
    # Tampilkan nama kolom
    print("\nNama kolom:")
    print(pasaran_df.columns.tolist())
    
except Exception as e:
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()
