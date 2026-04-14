"""
Excel Utilities Module
Additional utility functions for Excel data processing
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

class ExcelAnalyzer:
    """Advanced Excel data analysis utilities"""
    
    @staticmethod
    def get_sheet_names(file_path):
        """
        Get all sheet names from Excel file
        
        Args:
            file_path (str): Path to Excel file
            
        Returns:
            list: List of sheet names
        """
        try:
            excel_file = pd.ExcelFile(file_path)
            return excel_file.sheet_names
        except Exception as e:
            print(f"Error reading sheet names: {str(e)}")
            return []
    
    @staticmethod
    def compare_sheets(file_path, sheet1, sheet2):
        """
        Compare two sheets in the same Excel file
        
        Args:
            file_path (str): Path to Excel file
            sheet1 (str): First sheet name
            sheet2 (str): Second sheet name
        """
        try:
            df1 = pd.read_excel(file_path, sheet_name=sheet1)
            df2 = pd.read_excel(file_path, sheet_name=sheet2)
            
            print(f"=== PERBANDINGAN SHEET '{sheet1}' vs '{sheet2}' ===")
            print(f"{sheet1}: {df1.shape[0]} baris, {df1.shape[1]} kolom")
            print(f"{sheet2}: {df2.shape[0]} baris, {df2.shape[1]} kolom")
            
            # Compare columns
            cols1 = set(df1.columns)
            cols2 = set(df2.columns)
            
            common_cols = cols1.intersection(cols2)
            unique_cols1 = cols1 - cols2
            unique_cols2 = cols2 - cols1
            
            print(f"\nKolom yang sama: {len(common_cols)}")
            print(f"Kolom unik di {sheet1}: {len(unique_cols1)}")
            print(f"Kolom unik di {sheet2}: {len(unique_cols2)}")
            
            if unique_cols1:
                print(f"Kolom unik di {sheet1}: {list(unique_cols1)}")
            if unique_cols2:
                print(f"Kolom unik di {sheet2}: {list(unique_cols2)}")
                
        except Exception as e:
            print(f"Error comparing sheets: {str(e)}")
    
    @staticmethod
    def create_summary_report(data, output_path=None):
        """
        Create comprehensive summary report of the data
        
        Args:
            data (DataFrame): Data to analyze
            output_path (str, optional): Path to save report
        """
        if data is None or data.empty:
            print("Data kosong atau tidak valid")
            return
        
        report = []
        report.append("=== LAPORAN RINGKASAN DATA ===\n")
        
        # Basic info
        report.append(f"Jumlah baris: {len(data)}")
        report.append(f"Jumlah kolom: {len(data.columns)}")
        report.append(f"Ukuran data: {data.shape}")
        report.append("")
        
        # Column info
        report.append("=== INFORMASI KOLOM ===")
        for col in data.columns:
            dtype = data[col].dtype
            null_count = data[col].isnull().sum()
            unique_count = data[col].nunique()
            
            report.append(f"{col}:")
            report.append(f"  - Tipe data: {dtype}")
            report.append(f"  - Nilai kosong: {null_count}")
            report.append(f"  - Nilai unik: {unique_count}")
            
            if dtype in ['int64', 'float64']:
                report.append(f"  - Min: {data[col].min()}")
                report.append(f"  - Max: {data[col].max()}")
                report.append(f"  - Rata-rata: {data[col].mean():.2f}")
            report.append("")
        
        # Missing values summary
        missing_data = data.isnull().sum()
        if missing_data.any():
            report.append("=== DATA YANG HILANG ===")
            for col, count in missing_data.items():
                if count > 0:
                    percentage = (count / len(data)) * 100
                    report.append(f"{col}: {count} ({percentage:.1f}%)")
            report.append("")
        
        # Duplicate rows
        duplicates = data.duplicated().sum()
        if duplicates > 0:
            report.append(f"=== BARIS DUPLIKAT ===")
            report.append(f"Jumlah baris duplikat: {duplicates}")
            report.append("")
        
        report_text = "\n".join(report)
        print(report_text)
        
        # Save to file if requested
        if output_path:
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(report_text)
                print(f"\nLaporan disimpan ke: {output_path}")
            except Exception as e:
                print(f"Error saving report: {str(e)}")

def create_sample_excel():
    """Create a sample Excel file for testing"""
    # Sample data
    data = {
        'Nama': ['Ahmad', 'Budi', 'Citra', 'Dewi', 'Eko'],
        'Umur': [25, 30, 28, 35, 22],
        'Kota': ['Jakarta', 'Bandung', 'Surabaya', 'Jakarta', 'Yogyakarta'],
        'Gaji': [5000000, 7500000, 6000000, 8000000, 4500000],
        'Status': ['Menikah', 'Lajang', 'Menikah', 'Menikah', 'Lajang']
    }
    
    df = pd.DataFrame(data)
    
    # Create sample Excel with multiple sheets
    sample_path = '/Users/baktanarta/Documents/numerulogi/sample_data.xlsx'
    
    with pd.ExcelWriter(sample_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Data_Karyawan', index=False)
        
        # Create second sheet with different data
        sales_data = {
            'Bulan': ['Jan', 'Feb', 'Mar', 'Apr', 'Mei'],
            'Penjualan': [1000000, 1200000, 950000, 1300000, 1150000],
            'Target': [1000000, 1100000, 1000000, 1200000, 1100000],
            'Pencapaian': ['100%', '109%', '95%', '108%', '105%']
        }
        df_sales = pd.DataFrame(sales_data)
        df_sales.to_excel(writer, sheet_name='Data_Penjualan', index=False)
    
    print(f"File contoh dibuat: {sample_path}")
    return sample_path

if __name__ == "__main__":
    # Create sample file for testing
    sample_file = create_sample_excel()
    
    # Demonstrate utilities
    analyzer = ExcelAnalyzer()
    
    print("\n=== NAMA SHEET YANG TERSEDIA ===")
    sheets = analyzer.get_sheet_names(sample_file)
    for sheet in sheets:
        print(f"- {sheet}")
    
    print("\n=== PERBANDINGAN SHEET ===")
    if len(sheets) >= 2:
        analyzer.compare_sheets(sample_file, sheets[0], sheets[1])
