#!/usr/bin/env python3
"""
Numerulogi - Excel Data Processing Application
Main application file for reading and processing Excel data
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys
import os

class ExcelProcessor:
    """Class to handle Excel file operations and data processing"""
    
    def __init__(self):
        self.data = None
        self.file_path = None
    
    def load_excel(self, file_path, sheet_name=None):
        """
        Load Excel file into pandas DataFrame
        
        Args:
            file_path (str): Path to Excel file
            sheet_name (str, optional): Specific sheet name to load
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.file_path = Path(file_path)
            
            if not self.file_path.exists():
                print(f"Error: File {file_path} tidak ditemukan!")
                return False
            
            # Read Excel file
            if sheet_name:
                self.data = pd.read_excel(file_path, sheet_name=sheet_name)
                print(f"Data berhasil dimuat dari sheet '{sheet_name}'")
            else:
                self.data = pd.read_excel(file_path)
                print("Data berhasil dimuat dari Excel file")
            
            # Display basic info
            print(f"Jumlah baris: {len(self.data)}")
            print(f"Jumlah kolom: {len(self.data.columns)}")
            print(f"Kolom yang tersedia: {list(self.data.columns)}")
            
            return True
            
        except Exception as e:
            print(f"Error saat membaca file Excel: {str(e)}")
            return False
    
    def show_data_info(self):
        """Display comprehensive information about the loaded data"""
        if self.data is None:
            print("Tidak ada data yang dimuat. Silakan muat file Excel terlebih dahulu.")
            return
        
        print("\n=== INFORMASI DATA ===")
        print(f"Shape data: {self.data.shape}")
        print(f"Tipe data kolom:")
        print(self.data.dtypes)
        
        print(f"\n=== PREVIEW DATA (5 baris pertama) ===")
        print(self.data.head())
        
        print(f"\n=== STATISTIK DESKRIPTIF ===")
        print(self.data.describe())
        
        # Check for missing values
        missing_values = self.data.isnull().sum()
        if missing_values.any():
            print(f"\n=== DATA YANG HILANG ===")
            print(missing_values[missing_values > 0])
    
    def filter_data(self, column, value):
        """
        Filter data berdasarkan kolom dan nilai tertentu
        
        Args:
            column (str): Nama kolom
            value: Nilai untuk filter
        
        Returns:
            DataFrame: Data yang sudah difilter
        """
        if self.data is None:
            print("Tidak ada data yang dimuat.")
            return None
        
        if column not in self.data.columns:
            print(f"Kolom '{column}' tidak ditemukan!")
            return None
        
        filtered_data = self.data[self.data[column] == value]
        print(f"Data difilter: {len(filtered_data)} baris ditemukan untuk {column} = {value}")
        return filtered_data
    
    def save_to_excel(self, output_path, data=None):
        """
        Save data to Excel file
        
        Args:
            output_path (str): Path untuk file output
            data (DataFrame, optional): Data to save, uses self.data if None
        """
        try:
            data_to_save = data if data is not None else self.data
            
            if data_to_save is None:
                print("Tidak ada data untuk disimpan.")
                return False
            
            data_to_save.to_excel(output_path, index=False)
            print(f"Data berhasil disimpan ke: {output_path}")
            return True
            
        except Exception as e:
            print(f"Error saat menyimpan file: {str(e)}")
            return False

def main():
    """Main function to demonstrate usage"""
    print("=== NUMERULOGI - EXCEL DATA PROCESSOR ===")
    print("Aplikasi untuk memproses data Excel\n")
    
    # Create processor instance
    processor = ExcelProcessor()
    
    # Example usage
    print("Contoh penggunaan:")
    print("1. processor.load_excel('path/to/your/file.xlsx')")
    print("2. processor.show_data_info()")
    print("3. filtered = processor.filter_data('column_name', 'value')")
    print("4. processor.save_to_excel('output.xlsx', filtered)")
    
    # Interactive mode
    while True:
        print("\n=== MENU ===")
        print("1. Muat file Excel")
        print("2. Tampilkan info data")
        print("3. Filter data")
        print("4. Simpan data")
        print("5. Keluar")
        
        choice = input("\nPilih menu (1-5): ").strip()
        
        if choice == '1':
            file_path = input("Masukkan path file Excel: ").strip()
            sheet_name = input("Masukkan nama sheet (kosong untuk default): ").strip()
            sheet_name = sheet_name if sheet_name else None
            processor.load_excel(file_path, sheet_name)
            
        elif choice == '2':
            processor.show_data_info()
            
        elif choice == '3':
            if processor.data is None:
                print("Silakan muat data terlebih dahulu!")
                continue
            column = input("Masukkan nama kolom: ").strip()
            value = input("Masukkan nilai untuk filter: ").strip()
            filtered = processor.filter_data(column, value)
            if filtered is not None:
                print(filtered.head())
                
        elif choice == '4':
            if processor.data is None:
                print("Silakan muat data terlebih dahulu!")
                continue
            output_path = input("Masukkan path file output: ").strip()
            processor.save_to_excel(output_path)
            
        elif choice == '5':
            print("Terima kasih telah menggunakan Numerulogi!")
            break
            
        else:
            print("Pilihan tidak valid!")

if __name__ == "__main__":
    main()
