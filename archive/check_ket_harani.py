import pandas as pd
import os

def print_section(title, char='=', length=80):
    """Print a formatted section header"""
    print(f"\n{char * length}")
    print(f"{title.upper():^{length}}")
    print(f"{char * length}")

def print_table(headers, rows):
    """Print a simple table without external dependencies"""
    # Calculate column widths
    col_widths = [max(len(str(x)) for x in col) for col in zip(headers, *rows)]
    
    # Print header
    header_row = " | ".join(f"{h:<{w}}" for h, w in zip(headers, col_widths))
    print(header_row)
    print("-" * len(header_row))
    
    # Print rows
    for row in rows:
        print(" | ".join(f"{str(x):<{w}}" for x, w in zip(row, col_widths)))

def check_ket_harani():
    """
    Check and display the structure of Ket_harani.xlsx
    This will help verify if the Excel file has the correct structure for the application.
    """
    try:
        # Get the absolute path to the Excel file
        base_dir = os.path.dirname(os.path.abspath(__file__))
        excel_path = os.path.join(base_dir, 'Ket_harani.xlsx')
        
        if not os.path.exists(excel_path):
            print(f"Error: File not found: {excel_path}")
            print("Please make sure Ket_harani.xlsx exists in the same directory as this script.")
            return
            
        print_section(f"Analyzing: {excel_path}")
        
        # Get all sheet names
        xl = pd.ExcelFile(excel_path)
        sheet_names = xl.sheet_names
        
        # Expected sheets and their required columns
        expected_sheets = {
            'Hari': ['Neptu_Hari', 'Nama_Hari', 'Keterangan_Hari'],
            'Pasaran': ['Neptu_Pasaran', 'Nama_Pasaran', 'Keterangan_Pasaran'],
            'Wuku': ['Neptu_Wuku', 'Nama_Wuku', 'Keterangan_Wuku'],
            'LifePath': ['Angka', 'Kategori', 'Keterangan'],
            'Nama': ['Angka', 'Kategori', 'Keterangan']
        }
        
        # Print summary of found sheets
        print_section("Sheet Summary")
        print(f"Found {len(sheet_names)} sheet(s):")
        for i, sheet in enumerate(sheet_names, 1):
            status = "✓" if sheet in expected_sheets else "⚠"
            print(f"{i}. {status} {sheet}")
        
        # Check for missing sheets
        missing_sheets = set(expected_sheets.keys()) - set(sheet_names)
        if missing_sheets:
            print("\n⚠ Missing required sheets:")
            for sheet in sorted(missing_sheets):
                print(f"- {sheet}")
        
        # Analyze each sheet
        for sheet_name in sheet_names:
            print_section(f"Sheet: {sheet_name}")
            
            try:
                # Read the sheet
                df = pd.read_excel(excel_path, sheet_name=sheet_name)
                
                # Basic info
                print(f"Rows: {len(df)}, Columns: {len(df.columns)}")
                
                # Column information
                print("\nColumns:")
                for i, col in enumerate(df.columns, 1):
                    non_null = df[col].count()
                    null_count = len(df) - non_null
                    dtype = str(df[col].dtype)
                    sample = ""
                    
                    # Get a sample non-null value if available
                    non_null_vals = df[col].dropna()
                    if len(non_null_vals) > 0:
                        sample = str(non_null_vals.iloc[0])
                        if len(sample) > 30:
                            sample = sample[:27] + "..."
                    
                    print(f"{i}. {col} ({dtype})")
                    print(f"   Non-null: {non_null}, Null: {null_count}")
                    if sample:
                        print(f"   Sample: {sample}")
                
                # Check for required columns if this is an expected sheet
                if sheet_name in expected_sheets:
                    missing_cols = [col for col in expected_sheets[sheet_name] 
                                 if col not in df.columns]
                    if missing_cols:
                        print("\n⚠ Missing required columns:")
                        for col in missing_cols:
                            print(f"- {col}")
                
                # Show first 3 rows of data
                print("\nSample data (first 3 rows):")
                if len(df) > 0:
                    # Use pandas' built-in to_string for basic table display
                    print(df.head(3).to_string(index=False, max_colwidth=30))
                else:
                    print("No data found in this sheet.")
                
            except Exception as e:
                print(f"Error analyzing sheet '{sheet_name}': {str(e)}")
                import traceback
                traceback.print_exc()
        
        # Print summary of potential issues
        print_section("Analysis Complete")
        print("Key things to check:")
        print("1. All required sheets are present")
        print("2. Required columns exist in each sheet")
        print("3. Data types are correct (especially numeric fields)")
        print("4. No unexpected null values in key columns")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()

def check_life_path_file():
    """Check the structure of life_path.xlsx"""
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, 'life_path.xlsx')
        
        if not os.path.exists(file_path):
            print(f"Error: File not found: {file_path}")
            return
            
        print_section(f"Analyzing: {file_path}")
        
        # Check if file is an Excel file
        if not file_path.endswith(('.xls', '.xlsx')):
            print("Error: Not an Excel file")
            return
            
        # Get all sheet names
        xl = pd.ExcelFile(file_path)
        sheet_names = xl.sheet_names
        
        print(f"Found {len(sheet_names)} sheet(s):")
        for i, sheet in enumerate(sheet_names, 1):
            print(f"{i}. {sheet}")
        
        # Analyze each sheet
        for sheet_name in sheet_names:
            print_section(f"Sheet: {sheet_name}")
            
            try:
                # Read the sheet
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                
                # Basic info
                print(f"Rows: {len(df)}, Columns: {len(df.columns)}")
                
                # Column information
                print("\nColumns:")
                for i, col in enumerate(df.columns, 1):
                    non_null = df[col].count()
                    null_count = len(df) - non_null
                    dtype = str(df[col].dtype)
                    sample = ""
                    
                    # Get a sample non-null value if available
                    non_null_vals = df[col].dropna()
                    if len(non_null_vals) > 0:
                        sample = str(non_null_vals.iloc[0])
                        if len(sample) > 30:
                            sample = sample[:27] + "..."
                    
                    print(f"{i}. {col} ({dtype})")
                    print(f"   Non-null: {non_null}, Null: {null_count}")
                    if sample:
                        print(f"   Sample: {sample}")
                
                # Show first 3 rows of data
                print("\nSample data (first 3 rows):")
                if len(df) > 0:
                    print(df.head(3).to_string(index=False, max_colwidth=50))
                else:
                    print("No data found in this sheet.")
                
            except Exception as e:
                print(f"Error analyzing sheet '{sheet_name}': {str(e)}")
                import traceback
                traceback.print_exc()
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_ket_harani()
    check_life_path_file()
