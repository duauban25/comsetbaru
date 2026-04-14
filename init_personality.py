#!/usr/bin/env python3
"""
Initialize Personality table with sample data.
Run this when Flask app is NOT running to avoid database locks.
"""

import sqlite3
import os

def init_personality_table():
    """Create and seed the personality table with descriptions for numbers 1-9, 11, 22."""
    
    print("Initializing Personality table and data...")
    
    # Get the correct database path (same as SQLAlchemy uses)
    db_path = os.path.join(os.path.dirname(__file__), 'app.db')
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS personality (
            no INTEGER PRIMARY KEY,
            deskripsi TEXT
        );
        ''')
        
        # Check if data already exists
        cursor.execute('SELECT COUNT(*) FROM personality;')
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"✅ Personality table already has {count} records. Skipping seeding.")
            conn.close()
            return
        
        # Personality data for numbers 1-9, 11, 22
        personality_data = [
            (1, "Anda terlihat sebagai sosok yang percaya diri, mandiri, dan berjiwa pemimpin. Orang lain melihat Anda sebagai individu yang berani mengambil inisiatif, inovatif, dan tidak takut menghadapi tantangan. Kesan pertama yang Anda berikan adalah seseorang yang kuat, tegas, dan mampu memimpin dalam situasi apapun."),
            (2, "Anda memberikan kesan sebagai orang yang ramah, kooperatif, dan mudah bergaul. Orang lain melihat Anda sebagai sosok yang diplomatik, pengertian, dan selalu siap membantu. Kepribadian luar Anda memancarkan kehangatan, ketenangan, dan kemampuan untuk menciptakan harmoni dalam hubungan interpersonal."),
            (3, "Anda terlihat sebagai pribadi yang kreatif, ekspresif, dan penuh semangat. Orang lain melihat Anda sebagai sosok yang komunikatif, optimis, dan memiliki selera humor yang baik. Kesan pertama yang Anda berikan adalah seseorang yang menyenangkan, artistik, dan mampu menginspirasi orang lain dengan kreativitas Anda."),
            (4, "Anda memberikan kesan sebagai orang yang dapat diandalkan, praktis, dan pekerja keras. Orang lain melihat Anda sebagai sosok yang terorganisir, disiplin, dan memiliki dedikasi tinggi. Kepribadian luar Anda memancarkan stabilitas, konsistensi, dan kemampuan untuk menyelesaikan tugas dengan baik."),
            (5, "Anda terlihat sebagai pribadi yang dinamis, petualang, dan penuh energi. Orang lain melihat Anda sebagai sosok yang fleksibel, mudah beradaptasi, dan selalu siap mencoba hal-hal baru. Kesan pertama yang Anda berikan adalah seseorang yang bebas, progresif, dan memiliki wawasan yang luas."),
            (6, "Anda memberikan kesan sebagai orang yang peduli, bertanggung jawab, dan penuh kasih sayang. Orang lain melihat Anda sebagai sosok yang dapat dipercaya, protektif, dan selalu siap membantu keluarga dan teman. Kepribadian luar Anda memancarkan kehangatan keluarga, empati, dan naluri mengasuh yang kuat."),
            (7, "Anda terlihat sebagai pribadi yang bijaksana, misterius, dan mendalam. Orang lain melihat Anda sebagai sosok yang intelektual, spiritual, dan memiliki pemahaman yang mendalam tentang kehidupan. Kesan pertama yang Anda berikan adalah seseorang yang tenang, reflektif, dan memiliki aura kebijaksanaan."),
            (8, "Anda memberikan kesan sebagai orang yang ambisius, sukses, dan berpengaruh. Orang lain melihat Anda sebagai sosok yang profesional, efisien, dan memiliki kemampuan bisnis yang baik. Kepribadian luar Anda memancarkan otoritas, kemakmuran, dan kemampuan untuk mencapai tujuan besar."),
            (9, "Anda terlihat sebagai pribadi yang mulia, altruistik, dan memiliki visi kemanusiaan. Orang lain melihat Anda sebagai sosok yang bijaksana, toleran, dan selalu siap membantu sesama. Kesan pertama yang Anda berikan adalah seseorang yang inspiratif, universal, dan memiliki jiwa pelayanan yang besar."),
            (11, "Anda memberikan kesan sebagai orang yang karismatik, inspiratif, dan memiliki intuisi yang kuat. Orang lain melihat Anda sebagai sosok yang visioner, spiritual, dan mampu memahami hal-hal yang tidak terlihat. Kepribadian luar Anda memancarkan energi tinggi, sensitivitas psikis, dan kemampuan untuk menginspirasi orang lain pada level yang lebih tinggi."),
            (22, "Anda terlihat sebagai pribadi yang memiliki visi besar, kemampuan membangun yang luar biasa, dan potensi untuk menciptakan perubahan besar. Orang lain melihat Anda sebagai sosok yang praktis namun visioner, mampu mewujudkan impian menjadi kenyataan. Kesan pertama yang Anda berikan adalah seseorang yang memiliki misi besar dan kemampuan untuk mempengaruhi dunia secara positif.")
        ]
        
        # Insert the data
        cursor.executemany('INSERT INTO personality (no, deskripsi) VALUES (?, ?)', personality_data)
        
        conn.commit()
        print('✅ Personality data seeded successfully!')
        
        # Verify the data
        cursor.execute('SELECT COUNT(*) FROM personality;')
        count = cursor.fetchone()[0]
        print(f'✅ Total Personality records: {count}')
        
        # Test a sample record
        cursor.execute('SELECT * FROM personality WHERE no = 1;')
        sample = cursor.fetchone()
        if sample:
            print(f'✅ Sample record (Personality 1): {sample[1][:100]}...')
        
        conn.close()
        
    except Exception as e:
        print(f'❌ Error: {e}')
        print("\nMake sure the Flask application is not running, then try again.")

if __name__ == '__main__':
    init_personality_table()
