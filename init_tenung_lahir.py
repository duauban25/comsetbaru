#!/usr/bin/env python3
"""
Initialize TenungLahir table with sample data.
Run this when Flask app is NOT running to avoid database locks.
"""

import sqlite3
import os

def init_tenung_lahir_table():
    """Create and seed the tenung_lahir table with descriptions for O values (1-9) and M&N combinations."""
    
    print("Initializing TenungLahir table and data...")
    
    # Get the correct database path (same as SQLAlchemy uses)
    db_path = os.path.join(os.path.dirname(__file__), 'app.db')
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tenung_lahir (
            id TEXT PRIMARY KEY,
            deskripsi TEXT
        );
        ''')
        
        # Check if data already exists
        cursor.execute('SELECT COUNT(*) FROM tenung_lahir;')
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"✅ TenungLahir table already has {count} records. Skipping seeding.")
            conn.close()
            return
        
        # Sample data for Root Numbers (O values 1-9)
        root_number_data = [
            ("1", "Karakter kepemimpinan yang kuat, mandiri, dan inovatif. Anda memiliki kemampuan untuk memulai sesuatu yang baru dan memimpin orang lain dengan percaya diri."),
            ("2", "Karakter yang kooperatif, diplomatik, dan sensitif terhadap kebutuhan orang lain. Anda unggul dalam kerjasama tim dan membangun hubungan harmonis."),
            ("3", "Karakter yang kreatif, ekspresif, dan komunikatif. Anda memiliki bakat artistik dan kemampuan untuk menginspirasi orang lain melalui kata-kata dan kreativitas."),
            ("4", "Karakter yang praktis, terorganisir, dan pekerja keras. Anda memiliki dedikasi tinggi untuk membangun fondasi yang kuat dalam segala aspek kehidupan."),
            ("5", "Karakter yang dinamis, petualang, dan bebas. Anda menyukai perubahan, petualangan, dan memiliki kemampuan adaptasi yang tinggi."),
            ("6", "Karakter yang peduli, bertanggung jawab, dan penuh kasih sayang. Anda memiliki naluri mengasuh yang kuat dan selalu siap membantu keluarga dan komunitas."),
            ("7", "Karakter yang bijaksana, spiritual, dan analitis. Anda memiliki kemampuan untuk memahami hal-hal yang mendalam dan sering menjadi pencari kebenaran."),
            ("8", "Karakter yang ambisius, berorientasi pada kesuksesan material, dan memiliki kemampuan bisnis yang baik. Anda unggul dalam mengelola sumber daya dan mencapai tujuan besar."),
            ("9", "Karakter yang humanis, bijaksana, dan memiliki visi universal. Anda memiliki kemampuan untuk melayani kemanusiaan dan memberikan kontribusi positif bagi dunia.")
        ]
        
        # Sample data for some M&N combinations (you can expand this)
        mn_combination_data = [
            ("11", "Kombinasi yang menunjukkan intuisi tinggi dan kemampuan spiritual. Anda memiliki potensi untuk menjadi inspirasi bagi orang lain."),
            ("12", "Kombinasi yang menunjukkan keseimbangan antara kepemimpinan dan kerjasama. Anda mampu memimpin dengan cara yang diplomatik."),
            ("13", "Kombinasi yang menunjukkan kreativitas dalam kepemimpinan. Anda mampu memimpin dengan cara yang inovatif dan inspiratif."),
            ("21", "Kombinasi yang menunjukkan kerjasama dalam kepemimpinan. Anda mampu bekerja sama untuk mencapai tujuan bersama."),
            ("22", "Kombinasi master yang menunjukkan kemampuan membangun visi besar. Anda memiliki potensi untuk mewujudkan impian menjadi kenyataan."),
            ("23", "Kombinasi yang menunjukkan komunikasi yang harmonis. Anda mampu menyampaikan ide dengan cara yang menyenangkan."),
            ("31", "Kombinasi yang menunjukkan kreativitas dalam kepemimpinan. Anda mampu memimpin dengan cara yang unik dan menarik."),
            ("32", "Kombinasi yang menunjukkan kreativitas dalam kerjasama. Anda mampu bekerja sama dengan cara yang kreatif."),
            ("33", "Kombinasi master yang menunjukkan kemampuan mengajar dan menginspirasi. Anda memiliki potensi untuk menjadi guru spiritual."),
            ("44", "Kombinasi yang menunjukkan kemampuan membangun yang luar biasa. Anda mampu menciptakan struktur yang kuat dan tahan lama."),
            ("55", "Kombinasi yang menunjukkan kebebasan dan petualangan yang tinggi. Anda memiliki jiwa yang sangat bebas dan dinamis."),
            ("66", "Kombinasi yang menunjukkan tanggung jawab dan kasih sayang yang besar. Anda memiliki dedikasi tinggi untuk melayani orang lain."),
            ("77", "Kombinasi yang menunjukkan kebijaksanaan dan spiritualitas yang mendalam. Anda memiliki pemahaman yang dalam tentang kehidupan."),
            ("88", "Kombinasi yang menunjukkan kemampuan bisnis dan material yang luar biasa. Anda memiliki potensi untuk mencapai kesuksesan besar."),
            ("99", "Kombinasi yang menunjukkan jiwa pelayanan dan humanisme yang tinggi. Anda memiliki misi untuk melayani kemanusiaan.")
        ]
        
        # Combine all data
        all_data = root_number_data + mn_combination_data
        
        # Insert the data
        cursor.executemany('INSERT INTO tenung_lahir (id, deskripsi) VALUES (?, ?)', all_data)
        
        conn.commit()
        print('✅ TenungLahir data seeded successfully!')
        
        # Verify the data
        cursor.execute('SELECT COUNT(*) FROM tenung_lahir;')
        count = cursor.fetchone()[0]
        print(f'✅ Total TenungLahir records: {count}')
        
        # Test a sample record
        cursor.execute('SELECT * FROM tenung_lahir WHERE id = "1";')
        sample = cursor.fetchone()
        if sample:
            print(f'✅ Sample record (Root Number 1): {sample[1][:100]}...')
        
        conn.close()
        
    except Exception as e:
        print(f'❌ Error: {e}')
        print("\nMake sure the Flask application is not running, then try again.")

if __name__ == '__main__':
    init_tenung_lahir_table()
