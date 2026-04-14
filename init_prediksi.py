#!/usr/bin/env python3
"""
Initialize Prediksi table with all the matrix conditions and their meanings.
Run this when Flask app is NOT running to avoid database locks.
"""

import sqlite3
import os

def init_prediksi_table():
    """Create and seed the prediksi table with all matrix conditions and meanings."""
    
    print("Initializing Prediksi table and data...")
    
    # Get the correct database path (same as SQLAlchemy uses)
    db_path = os.path.join(os.path.dirname(__file__), 'app.db')
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS prediksi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kondisi TEXT NOT NULL,
            makna TEXT NOT NULL
        );
        ''')
        
        # Check if data already exists
        cursor.execute('SELECT COUNT(*) FROM prediksi;')
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"✅ Prediksi table already has {count} records. Skipping seeding.")
            conn.close()
            return
        
        # All prediction conditions and their meanings
        prediksi_data = [
            # Single digit conditions
            ("I=1", "Pusat perhatian, ambisius, sulit mengakui kekalahan, banyak masalah, keras kepala, mandiri, perfeksionis."),
            ("N=1", "Sangat egois, menentang aturan, mandiri, menciptakan drama dan pengalihan perhatian."),
            ("J=1", "Memiliki ayah yang diktator."),
            ("I=2", "Sensitif, lembut, menerima, mudah terpengaruh, malas dan apatis, dapat berganti peran dengan cepat."),
            ("N=2", "Sangat lembut dan pendiam, atau bisa juga sangat cerewet."),
            ("I=3", "Emosional, harga diri, ambisius, konservatif, tertutup, mudah frustasi."),
            ("N=3", "Sangat egois, tidak sabaran dan emosional."),
            ("I=4", "Revolusioner, inovator, cerdas, menghibur, terkadang misterius, kontrol berlebih (tirani) yang melahirkan sifat otoriter."),
            ("N=4", "Sangat pesimis dan curigaan."),
            ("I=5", "Semangat, suka mencoba hal baru, sosialis, cepat berpindah."),
            ("N=5", "Sangat keras kepala dan banyak rintangan."),
            ("I=6", "Bersenang-senang, genit, cinta, peduli dan perhatian, pengorbanan, pengabdian, diplomatis, sangat bergantung pada pendapat orang lain tentang dirinya."),
            ("N=6", "Sangat pelit dan perhitungan."),
            ("I=7", "Inspirator, kreatif namun rapuh, kurang mandiri, sosok seniman, potensi bermasalah terkait hubungan percintaan."),
            ("N=7", "Sangat mudah bosan."),
            ("I=8", "Terisolasi, canggung, emosional, penanggungjawab, setia."),
            ("N=8", "Sangat sibuk."),
            ("I=9", "Tempramen, sensitif, pemberani, cerdas, pikiran sistematis dan terstruktur, mandiri dan menyendiri, kurang percaya dengan orang lain, terlalu berhati-hati, agak sombong."),
            ("N=9", "Sangat serakah."),
            
            # Two digit combinations
            ("KL=1", "Ada perpisahan, dikhianati orang."),
            ("JK=11", "Potensi mengalami perselisihan rumah tangga, perpisahan, perceraian."),
            ("NO=22", "Perselingkuhan (cinta, bisnis atau keyakinan), punya istri muda."),
            ("IJ=12", "Potensi kaya raya di umur diatas 40 tahun."),
            ("KL=12", "Indigo, potensi kaya raya diumur > 40 tahun, dekat dengan sosok ibu dan selalu dinasehati ibunya."),
            ("KN=12", "Pandai, terkenal, sosok pengacara yang handal."),
            ("IJ=13", "Menentang Ayahnya, bandel."),
            ("KL=13", "Potensi menikah dengan lain suku, atau bangsa atau agama lain."),
            ("KL=14", "Pendiam, jarang mau bercerita, setiap masalah diselesaikan sendirian atau dipedam dalam hati."),
            ("KL=15", "Perpisahan, dikhianati, sulit rejeki ditempat kelahirannya."),
            ("JK=16", "Potensi tertembak di area kepala."),
            ("KL=16", "Menikah dengan orang yang 4 tahunan lebih muda/tua, makin tua makin genit."),
            ("KL=17", "Menikah dengan orang yang 4 tahunan lebih muda atau lebih tua, hidup merantau."),
            ("KL=19", "Janda atau duda akibat pasangannya meninggal lebih dahulu."),
            ("KN=21", "Ucapannya menyakitkan, marah tak kenal waktu dan tempat, disituasi kondisi apapun akan meluapkan amarahnya."),
            ("KL=21", "Ucapannya menyakitkan, marah tak kenal waktu dan tempat, disituasi kondisi apapun akan meluapkan amarahnya."),
            ("IJ=21", "Ucapannya menyakitkan, marah tak kenal waktu dan tempat, disituasi kondisi apapun akan meluapkan amarahnya."),
            ("KL=24", "Pendiam, jarang mau bercerita, menyelesaikan masalah sendirian atau dipedam dalam hati."),
            ("KL=26", "Suka minta uang pada ayahnya."),
            ("IJ=33", "Menikah lebih dari sekali, atau potensi tidak menikah."),
            ("JN=44", "Berkarisma, wajah cantik dan menarik, pelacur."),
            ("JM=44", "Berkarisma, wajah cantik dan menarik, pelacur."),
            ("MO=44", "Berkarisma, wajah cantik dan menarik, pelacur."),
            ("IJ=4", "Berkarisma, wajah cantik dan menarik, pelacur."),
            ("IJ=57", "Memiliki Ayah terpandang, berpangkat atau kaya raya, dimanfaatkan, tertipu, ditipu."),
            ("JM=66", "Pelupa, pikun, otak bermasalah."),
            ("NO=66", "Potensi kaya, keuangan bagus."),
            ("NO=77", "Perselingkuhan (cinta, bisnis, atau keyakinan), kawin lebih dari sekali, istri muda, sangat cantik, sering berselisih, banyak pacar atau selingkuhan."),
            ("MO=77", "Kehidupan sedih, tidak mampu hidup dengan pasangannya, umur cintanya pendek."),
            ("IM=78", "Potensi minggat atau pergi tanpa pamit."),
            ("MO=78", "Potensi minggat atau pergi tanpa pamit."),
            
            # Three digit combinations
            ("IJK=111", "Potensi cerai, lelaki: beberapa kali gagal dalam percintaan; perempuan: pembawa sial atau keburukan bagi pasangannya."),
            ("JKL=111", "Perselisihan, perpisahan, perceraian."),
            ("LNO=123", "Pandai bicara."),
            ("JKL=115", "Potensi melakukan bunuh diri."),
            ("JNO=222", "Ketergantungan obat, Potensi Narkoba; Pria yang tergantung dengan istri, sosok Germo, Wanita pemeras pria."),
            ("IMO=444", "Potensi kecelakaan akibat unsur kayu, kecelakaan tersusuk kayu, menabrak atau tertimpa pohon."),
            ("JNO=555", "Boleh dan mau berbisnis haram."),
            ("ILO=666", "Yang dialami akibat kemauannya sendiri, saat merasa buntu akan bunuh diri atau membunuh orang lain."),
            ("IMO=888", "Tempramen, pemarah, potensi kecelakaan oleh unsur api, petir, listrik, serangan jantung."),
            ("KMO=888", "Semua kejadian atau masalah di kehidupannya atas permintaan atau keinginannya sendiri."),
            ("JNO=888", "Semua kejadian atau masalah di kehidupannya atas permintaan atau keinginannya sendiri."),
            ("MNL=426", "Membunuh dan menyakiti demi uang."),
            ("IMN=642", "Potensi melakukan Korupsi."),
            ("JMN=642", "Potensi melakukan Korupsi."),
            
            # Four digit combinations
            ("IJKL=1111", "Perselisihan, perceraian, prahara rumah tangga."),
            ("IKMN=1111", "Potensi masuk penjara, diculik, dikurung atau terkurung, dicekal, tidak bisa pulang kerumah."),
            ("IJKM=1911", "Dikekang, potensi depresi, stress, gangguan jiwa."),
            ("JMNO=1911", "Kerugian, bangkrut, tidak cocok membangun usaha, hanya cocok menjadi staf."),
            ("JNOT=5555", "Sosok mafia, anggota gengster."),
            
            # Five digit combinations
            ("IMOPU=11111", "Potensi bunuh diri atau dibunuh."),
            ("IMOTP=33333", "Selalu mencoba bunuh diri tetapi gagal, tersiksa, sulit mati."),
            ("JNOTQ=44444", "Sang perancang pembunuhan."),
            ("IJMNO=44444", "Perancang sesuatu yang sangat dirahasiakan (kecuali Sektor ibu)."),
            ("JONTQ=55555", "Sosok pemimpin mafia."),
            ("JNOTQ=77777", "Mampu memperalat orang dengan maksimal."),
            
            # Special conditions
            ("ST-VW=69-96", "Raja judi, sangat beruntung dalam berspekulasi."),
            
            # Six digit conditions (more than 5 occurrences)
            (">5=111111", "Potensi kecelakaan, tertabrak, tertusuk, tertimpa atau meninggal yang disebabkan oleh unsur logam."),
            (">5=222222", "Potensi kecelakaan, hanyut, tenggelam, pendarahan atau meninggal akibat unsur air (cairan)."),
            (">6=333333", "Potensi kecelakaan, tersetrum, terbakar, tersambar petir, atau meninggal akibat unsur api."),
            (">5=444444", "Potensi kecelakaan, tertimpa atau tersusuk kayu, tersesat didalam hutan atau meninggal akibat unsur kayu."),
            (">5=555555", "Potensi kecelakaan, tertimpa batu, tertimbun longsoran tanah bebatuan, atau meninggal akibat unsur tanah."),
            (">5=666666", "Potensi kecelakaan, tertabrak, tertusuk, tertimpa atau meninggal yang disebabkan oleh unsur logam."),
            (">5=777777", "Potensi kecelakaan, hanyut, tenggelam, pendarahan atau meninggal akibat unsur air (cairan)."),
            (">5=888888", "Potensi kecelakaan, tersetrum, terbakar, tersambar petir, atau meninggal akibat unsur api."),
            (">5=999999", "Serakah, banyak peluang bisnis, ingin cepat kaya, penyendiri, suka tempat sepi, suka hutan dan binatang, saat bangkrut akan menghilang melarikan diri; Potensi kecelakaan, tertimpa atau tersusuk kayu, tersesat didalam hutan atau meninggal akibat unsur kayu."),
        ]
        
        # Insert the data
        cursor.executemany('INSERT INTO prediksi (kondisi, makna) VALUES (?, ?)', prediksi_data)
        
        conn.commit()
        print('✅ Prediksi data seeded successfully!')
        
        # Verify the data
        cursor.execute('SELECT COUNT(*) FROM prediksi;')
        count = cursor.fetchone()[0]
        print(f'✅ Total Prediksi records: {count}')
        
        # Test a sample record
        cursor.execute('SELECT * FROM prediksi WHERE kondisi = "I=1";')
        sample = cursor.fetchone()
        if sample:
            print(f'✅ Sample record (I=1): {sample[2][:100]}...')
        
        conn.close()
        
    except Exception as e:
        print(f'❌ Error: {e}')
        print("\nMake sure the Flask application is not running, then try again.")

if __name__ == '__main__':
    init_prediksi_table()
