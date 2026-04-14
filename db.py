from __future__ import annotations
import os
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Boolean,
    create_engine,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, sessionmaker
from flask_login import UserMixin
from werkzeug.security import generate_password_hash
from sqlalchemy import text

# SQLite database file in project directory
DB_PATH = os.path.join(os.path.dirname(__file__), 'app.db')
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # Required for SQLite with threads
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Authentication and user management
class User(Base, UserMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(32), default='bronze', index=True)  # bronze, silver, gold, admin
    is_active = Column(Boolean, default=True)
    reset_token = Column(String(255), nullable=True, index=True)
    reset_expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    # Profile fields
    full_name = Column(String(255), nullable=True)
    birth_date = Column(String(10), nullable=True)  # YYYY-MM-DD

# Reference tables migrated from Excel files
class LifePath(Base):
    __tablename__ = 'life_path'
    no = Column(Integer, primary_key=True, index=True)
    deskripsi = Column(Text, default='')
    detail = Column(Text, default='')
    kekuatan = Column(Text, default='')     # serialized text (e.g., sentences joined by \n)
    tantangan = Column(Text, default='')    # serialized text
    penjelasan_html = Column(Text, default='')


class Tantangan(Base):
    __tablename__ = 'tantangan'
    kode = Column(Integer, primary_key=True, index=True)
    penjelasan = Column(Text, default='')


class HaraniNama(Base):
    __tablename__ = 'harani_nama'
    no = Column(Integer, primary_key=True, index=True)
    deskripsi = Column(Text, default='')
    kekuatan = Column(Text, default='')
    kelemahan = Column(Text, default='')
    makna_energi = Column(Text, default='')


class Karma(Base):
    __tablename__ = 'karma'
    no = Column(Integer, primary_key=True, index=True)
    judul = Column(Text, default='')
    makna = Column(Text, default='')
    pelajaran = Column(Text, default='')
    saran = Column(Text, default='')


# Arrow Individual meanings (per specific arrow key)
class ArrowIndividual(Base):
    __tablename__ = 'arrow_individual'
    id = Column(String(50), primary_key=True, index=True)  # e.g., 'arrow_determination'
    title = Column(String(100), default='')
    deskripsi = Column(Text, default='')


class Rejeki(Base):
    __tablename__ = 'rejeki'
    no = Column(Integer, primary_key=True, index=True)
    deskripsi = Column(Text, default='')
    kekuatan = Column(Text, default='')
    kelemahan = Column(Text, default='')
    saran = Column(Text, default='')
    pq = Column(String(10), nullable=True)           # optional key for combinations
    deskripsi_pq = Column(Text, default='')


class ArahSukses(Base):
    __tablename__ = 'arah_sukses'
    id = Column(Integer, primary_key=True)
    arah = Column(String(64), index=True, unique=True)
    deskripsi = Column(Text, default='')


class LintangBali(Base):
    __tablename__ = 'lintang_bali'
    id = Column(Integer, primary_key=True)
    hari = Column(String(32), index=True)
    pasaran = Column(String(32), index=True)
    lintang = Column(String(64), index=True)
    deskripsi = Column(Text, default='')
    watak1 = Column(String(128), default='')
    arti1 = Column(Text, default='')
    watak2 = Column(String(128), default='')
    arti2 = Column(Text, default='')
    __table_args__ = (
        UniqueConstraint('hari', 'pasaran', name='uq_lintang_hari_pasaran'),
    )


class DeskWewaran(Base):
    __tablename__ = 'desk_wewaran'
    id = Column(Integer, primary_key=True)
    kategori = Column(String(32), index=True)   # Ekawara, Dwiwara, ...
    nilai = Column(Integer, index=True)         # 0-based value used in code
    nama = Column(String(64), default='')
    deskripsi = Column(Text, default='')
    __table_args__ = (
        UniqueConstraint('kategori', 'nilai', name='uq_wewaran_kategori_nilai'),
    )


class HariLahir(Base):
    __tablename__ = 'hari_lahir'
    hari = Column(Integer, primary_key=True, index=True)  # 1..31
    keterangan = Column(Text, default='')


class WukuAwal(Base):
    __tablename__ = 'wuku_awal'
    tahun = Column(Integer, primary_key=True, index=True)
    no_wuku = Column(Integer, nullable=True)
    wuku_awal = Column(String(64), default='')


class Upload(Base):
    __tablename__ = 'uploads'
    id = Column(Integer, primary_key=True)
    filename = Column(String(255), index=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow, index=True)


class UploadRow(Base):
    __tablename__ = 'upload_rows'
    id = Column(Integer, primary_key=True)
    upload_id = Column(Integer, index=True)
    row_index = Column(Integer, index=True)    # 0-based index in original Excel
    row_json = Column(Text)                    # JSON string per row


# Master list of Wuku names (ordered 1..30)
class WukuName(Base):
    __tablename__ = 'wuku_name'
    no = Column(Integer, primary_key=True, index=True)   # 1..30
    nama = Column(String(64), unique=True, index=True)
    deskripsi = Column(Text, default='')


# Generic weton arti mapping by category/name (e.g., Hari/"Senin", Pasaran/"Legi", Wuku/"Sinta")
class WetonArti(Base):
    __tablename__ = 'weton_arti'
    id = Column(Integer, primary_key=True)
    kategori = Column(String(32), index=True)  # 'Hari', 'Pasaran', 'Wuku'
    nama = Column(String(64), index=True)
    deskripsi = Column(Text, default='')
    __table_args__ = (
        UniqueConstraint('kategori', 'nama', name='uq_weton_arti_kategori_nama'),
    )


# Combined mapping for specific Hari+Pasaran pairs
class WetonArtiPair(Base):
    __tablename__ = 'weton_arti_pair'
    id = Column(Integer, primary_key=True)
    hari = Column(String(32), index=True)
    pasaran = Column(String(32), index=True)
    ket_hari = Column(Text, default='')
    ket_pasaran = Column(Text, default='')
    __table_args__ = (
        UniqueConstraint('hari', 'pasaran', name='uq_weton_arti_pair'),
    )


class Panggilan(Base):
    __tablename__ = 'panggilan'
    no = Column(Integer, primary_key=True, index=True)
    deskripsi = Column(Text, default='')

class TenungNama(Base):
    __tablename__ = 'tenung_nama'
    no = Column(Integer, primary_key=True, index=True)
    deskripsi = Column(Text, default='')

# Karmic Debt table (stores descriptions for 13, 14, 16, 19)
class KarmicDebt(Base):
    __tablename__ = 'karmic_debt'
    no = Column(Integer, primary_key=True, index=True)  # 13, 14, 16, 19
    deskripsi = Column(Text)


class HeartDesire(Base):
    __tablename__ = 'heart_desire'
    no = Column(Integer, primary_key=True, index=True)  # 1-9
    deskripsi = Column(Text)
    kekuatan = Column(Text, default='')
    kelemahan = Column(Text, default='')
    saran = Column(Text, default='')


class Personality(Base):
    __tablename__ = 'personality'
    no = Column(Integer, primary_key=True, index=True)  # 1-9, 11, 22
    deskripsi = Column(Text)


class SoulUrge(Base):
    __tablename__ = 'soul_urge'
    no = Column(Integer, primary_key=True, index=True)  # 1-9
    deskripsi = Column(Text)


class OuterExpression(Base):
    __tablename__ = 'outer_expression'
    no = Column(Integer, primary_key=True, index=True)  # 1-9
    deskripsi = Column(Text)


class TenungLahir(Base):
    __tablename__ = 'tenung_lahir'
    id = Column(String(10), primary_key=True, index=True)  # O value or M&N combination
    deskripsi = Column(Text)


class Prediksi(Base):
    __tablename__ = 'prediksi'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    kondisi = Column(String(50), index=True)  # e.g., "I=1", "JK=11", "IJK=111"
    makna = Column(Text)  # The prediction meaning


class TenungKarma(Base):
    __tablename__ = 'tenung_karma'
    id = Column(String(20), primary_key=True, index=True)  # N-DL-D combination like "7-12-3"
    arti = Column(String(100))  # Short meaning
    deskripsi = Column(Text)  # Detailed description


class PapanPythagoras(Base):
    __tablename__ = 'papan_pythagoras'
    id = Column(String(20), primary_key=True, index=True)  # Format: "position_count" e.g., "mind_self_3", "soul_community_0"
    deskripsi = Column(Text)


# Birth Chart table (based on birth date digits distribution)
class BirthChart(Base):
    __tablename__ = 'birth_chart'
    id = Column(String(20), primary_key=True, index=True)  # Format: "mind_self_2", "soul_world_0", etc.
    deskripsi = Column(Text)


class BirthChartEmptyCombo(Base):
    __tablename__ = 'birth_chart_empty_combo'
    id = Column(String(100), primary_key=True, index=True)  # e.g., "mind_self", "mind_self+soul_world"
    deskripsi = Column(Text)


class AngkaTerisolasi(Base):
    __tablename__ = 'angka_terisolasi'
    angka = Column(Integer, primary_key=True, index=True)  # 1, 3, 7, 9
    deskripsi = Column(Text)


class AngkaBerderet(Base):
    __tablename__ = 'angka_berderet'
    id = Column(String(50), primary_key=True, index=True)  # e.g., "diagonal_159", "baris_body", etc.
    status = Column(String(10))  # "deret" or "tanpa"
    deskripsi = Column(Text)

class Chaldean(Base):
    __tablename__ = 'chaldean'
    id = Column(Integer, primary_key=True, index=True)  # 1-9
    deskripsi = Column(Text)


# Bridge mapping table (key -> description)
class BridgeName(Base):
    __tablename__ = 'bridge_name'
    bgride = Column(String(32), primary_key=True, index=True)
    deskripsi = Column(Text, default='')


# Bridge full details table
class BridgeNumber(Base):
    __tablename__ = 'bridge_number'
    # Key can be numeric string like "4" or combo like "3-5"
    key = Column(String(32), primary_key=True, index=True)
    deskripsi = Column(Text, default='')
    makna = Column(Text, default='')
    tantangan = Column(Text, default='')
    saran = Column(Text, default='')


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    # Simple SQLite migrations for new columns in users table
    try:
        with engine.connect() as conn:
            res = conn.execute(text("PRAGMA table_info(users)"))
            cols = [row[1] for row in res.fetchall()]
            if 'full_name' not in cols:
                conn.execute(text("ALTER TABLE users ADD COLUMN full_name VARCHAR(255)"))
            if 'birth_date' not in cols:
                conn.execute(text("ALTER TABLE users ADD COLUMN birth_date VARCHAR(10)"))
    except Exception as e:
        print(f"[DB] migration check/add columns failed: {e}")
    
    # Seed Heart's Desire data if table is empty
    db = SessionLocal()
    try:
        # Check if HeartDesire data exists
        existing_hd = db.query(HeartDesire).first()
        if not existing_hd:
            # Seed basic Heart's Desire data
            heart_desire_data = [
                {
                    'no': 1,
                    'deskripsi': 'Anda memiliki keinginan mendalam untuk menjadi pemimpin dan pelopor. Jiwa Anda mendambakan kemandirian, inovasi, dan kemampuan untuk memulai hal-hal baru.',
                    'kekuatan': 'Ambisi yang kuat, keberanian mengambil risiko, kemampuan memimpin.',
                    'kelemahan': 'Kecenderungan egois, terlalu dominan, sulit bekerja sama.',
                    'saran': 'Belajarlah untuk mendengarkan orang lain dan bekerja sama dalam tim.'
                },
                {
                    'no': 2,
                    'deskripsi': 'Keinginan hati Anda adalah menciptakan harmoni dan kedamaian. Anda mendambakan hubungan yang mendalam dan kerjasama yang baik.',
                    'kekuatan': 'Kemampuan diplomasi yang baik, sensitif terhadap perasaan orang lain.',
                    'kelemahan': 'Terlalu sensitif, mudah terpengaruh orang lain, ragu-ragu.',
                    'saran': 'Percayai intuisi Anda dan jangan takut untuk mengambil keputusan.'
                },
                {
                    'no': 3,
                    'deskripsi': 'Anda memiliki keinginan kuat untuk mengekspresikan diri secara kreatif. Jiwa Anda mendambakan kebebasan berekspresi dan kegembiraan.',
                    'kekuatan': 'Kreativitas tinggi, kemampuan komunikasi yang baik, optimisme.',
                    'kelemahan': 'Mudah terdistraksi, kurang fokus, terlalu emosional.',
                    'saran': 'Fokuskan energi kreatif Anda pada proyek-proyek yang bermakna.'
                },
                {
                    'no': 4,
                    'deskripsi': 'Keinginan mendalam Anda adalah menciptakan stabilitas dan keamanan. Jiwa Anda mendambakan keteraturan dan sistem yang solid.',
                    'kekuatan': 'Disiplin tinggi, dapat diandalkan, pekerja keras.',
                    'kelemahan': 'Terlalu kaku, sulit menerima perubahan, workaholic.',
                    'saran': 'Belajarlah untuk lebih fleksibel dan terbuka terhadap cara-cara baru.'
                },
                {
                    'no': 5,
                    'deskripsi': 'Anda memiliki keinginan kuat akan kebebasan dan petualangan. Jiwa Anda mendambakan pengalaman baru dan eksplorasi.',
                    'kekuatan': 'Adaptabilitas tinggi, rasa ingin tahu yang besar, berani.',
                    'kelemahan': 'Sulit berkomitmen, mudah bosan, impulsif.',
                    'saran': 'Belajarlah untuk menyeimbangkan kebebasan dengan tanggung jawab.'
                },
                {
                    'no': 6,
                    'deskripsi': 'Keinginan hati Anda adalah untuk mengasuh dan melayani orang lain. Jiwa Anda mendambakan harmoni keluarga dan kemampuan menyembuhkan.',
                    'kekuatan': 'Penuh kasih sayang, bertanggung jawab, naluri mengasuh yang kuat.',
                    'kelemahan': 'Terlalu protektif, sulit mengatakan tidak, mengabaikan kebutuhan sendiri.',
                    'saran': 'Belajarlah untuk menyeimbangkan memberi dengan menerima.'
                },
                {
                    'no': 7,
                    'deskripsi': 'Anda memiliki keinginan mendalam untuk memahami misteri kehidupan. Jiwa Anda mendambakan kebijaksanaan dan pengetahuan spiritual.',
                    'kekuatan': 'Kemampuan analisis yang tajam, intuisi spiritual yang kuat.',
                    'kelemahan': 'Terlalu kritis, sulit percaya pada orang lain, cenderung menyendiri.',
                    'saran': 'Bagikan kebijaksanaan Anda dengan orang lain.'
                },
                {
                    'no': 8,
                    'deskripsi': 'Keinginan hati Anda adalah mencapai kesuksesan material dan pengaruh yang besar. Jiwa Anda mendambakan kekuasaan dan prestasi.',
                    'kekuatan': 'Ambisi yang kuat, kemampuan bisnis yang baik, kepemimpinan efektif.',
                    'kelemahan': 'Terlalu fokus pada materi, workaholic, kurang peka terhadap perasaan.',
                    'saran': 'Ingatlah bahwa kesuksesan sejati meliputi kebahagiaan dan hubungan bermakna.'
                },
                {
                    'no': 9,
                    'deskripsi': 'Anda memiliki keinginan mulia untuk melayani kemanusiaan. Jiwa Anda mendambakan kemampuan memberikan kontribusi besar bagi dunia.',
                    'kekuatan': 'Jiwa yang mulia, empati yang tinggi, visi global.',
                    'kelemahan': 'Terlalu idealis, mudah kecewa dengan realitas, sulit fokus.',
                    'saran': 'Mulailah dari hal-hal kecil di sekitar Anda.'
                }
            ]
            
            for data in heart_desire_data:
                heart_desire = HeartDesire(**data)
                db.add(heart_desire)
            
            db.commit()
            print('Heart\'s Desire data seeded successfully!')
    except Exception as e:
        print(f'Error seeding Heart\'s Desire data: {e}')
        db.rollback()
    finally:
        db.close()

    # Seed ArrowIndividual data if table is empty
    db = SessionLocal()
    try:
        existing_arrow = db.execute(text("SELECT COUNT(1) FROM arrow_individual")).scalar()
        if not existing_arrow:
            arrow_data = [
                {"id": "arrow_determination", "title": "Arrow of Determination", "deskripsi": "Kehadiran angka 1, 5, dan 9 menunjukkan tekad kuat, fokus, dan keberanian untuk menyelesaikan apa yang dimulai."},
                {"id": "arrow_procrastination", "title": "Arrow of Procrastination", "deskripsi": "Ketidakhadiran angka 1, 5, dan 9 mengindikasikan kecenderungan menunda dan kurangnya momentum untuk bertindak."},
                {"id": "arrow_spirituality", "title": "Arrow of Spirituality", "deskripsi": "Kehadiran angka 3, 5, dan 7 menandakan kepekaan spiritual, intuisi, dan pencarian makna yang mendalam."},
                {"id": "arrow_enquirer", "title": "Arrow of The Enquirer", "deskripsi": "Ketiadaan angka 3, 5, dan 7 membuat seseorang cenderung banyak bertanya namun sulit menemukan keyakinan batin."},
                {"id": "arrow_intellect", "title": "Arrow of The Intellect", "deskripsi": "Kehadiran angka 3, 6, dan 9 menunjukkan daya pikir logis, memori kuat, dan kemampuan analitis."},
                {"id": "arrow_poor_memory", "title": "Arrow of Poor Memory", "deskripsi": "Ketiadaan angka 3, 6, dan 9 berkaitan dengan tantangan daya ingat dan fokus mental."},
                {"id": "arrow_emotional_balance", "title": "Arrow of Emotional Balance", "deskripsi": "Kehadiran angka 2, 5, dan 8 menandakan kestabilan emosi, empati, dan kedewasaan perasaan."},
                {"id": "arrow_hypersensitivity", "title": "Arrow of Hypersensitivity", "deskripsi": "Ketiadaan angka 2, 5, dan 8 dapat memunculkan sensitivitas berlebih atau reaksi emosional yang tidak stabil."},
                {"id": "arrow_practicality", "title": "Arrow of Practicality", "deskripsi": "Kehadiran angka 1, 4, dan 7 menggambarkan sifat praktis, mandiri, dan kemampuan eksekusi yang baik."},
                {"id": "arrow_disorder", "title": "Arrow of Disorder", "deskripsi": "Ketiadaan angka 1, 4, dan 7 mengarah pada pola yang kurang terstruktur dan kesulitan menjaga keteraturan."},
                {"id": "arrow_planner", "title": "Arrow of The Planner", "deskripsi": "Kehadiran angka 3, 2, dan 1 menunjukkan kekuatan dalam perencanaan, urutan langkah, dan strategi tindakan."},
                {"id": "arrow_will", "title": "Arrow of The Will", "deskripsi": "Kehadiran angka 6, 5, dan 3 merefleksikan kemauan kuat, konsistensi, dan daya dorong internal."},
                {"id": "arrow_frustration", "title": "Arrow of Frustration", "deskripsi": "Ketiadaan angka 3, 5, dan 6 dapat memunculkan rasa frustasi serta kesulitan mengekspresikan ide secara efektif."},
                {"id": "arrow_activity", "title": "Arrow of Activity", "deskripsi": "Kehadiran angka 7, 8, dan 9 menandakan dinamika tinggi, inisiatif, dan orientasi aksi."},
                {"id": "arrow_passivity", "title": "Arrow of Passivity", "deskripsi": "Ketiadaan angka 7, 8, dan 9 menunjukkan kecenderungan pasif dan menunggu keadaan berubah terlebih dahulu."},
                {"id": "arrow_no_arrows", "title": "Birth Charts With No Arrows", "deskripsi": "Tidak terbentuk panah utuh; baris/kolom hanya berisi satu atau dua titik. Ini menandakan pola energi yang tersebar dan perlu fokus untuk membentuk keunggulan tertentu."},
            ]
            for a in arrow_data:
                db.execute(text("INSERT INTO arrow_individual(id, title, deskripsi) VALUES (:id, :title, :deskripsi)"), a)
            db.commit()
            print('ArrowIndividual data seeded successfully!')
    except Exception as e:
        print(f'Error seeding ArrowIndividual data: {e}')
        db.rollback()
    finally:
        db.close()

    # Seed BirthChart data if table is empty
    db = SessionLocal()
    try:
        existing_birth_chart = db.query(BirthChart).first()
        if not existing_birth_chart:
            birth_chart_data = [
                # Mind row (3,6,9)
                {'id': 'mind_self_0', 'deskripsi': 'Belum tampak pola pikir kreatif dari tanggal lahir. Perlu merangsang ide melalui pengalaman.'},
                {'id': 'mind_self_1', 'deskripsi': 'Ada potensi kreativitas mental yang muncul dari tanggal lahir.'},
                {'id': 'mind_self_2', 'deskripsi': 'Kreativitas berpikir cukup kuat dan konsisten.'},
                {'id': 'mind_community_0', 'deskripsi': 'Dorongan komunikasi mental ke lingkungan masih minim.'},
                {'id': 'mind_community_1', 'deskripsi': 'Mampu mengekspresikan pemikiran kepada sekitar.'},
                {'id': 'mind_community_2', 'deskripsi': 'Sangat komunikatif dalam menyampaikan ide.'},
                {'id': 'mind_world_0', 'deskripsi': 'Visi mental skala luas belum terbentuk.'},
                {'id': 'mind_world_1', 'deskripsi': 'Ada kesadaran mental terhadap konteks yang lebih luas.'},
                {'id': 'mind_world_2', 'deskripsi': 'Visi mental global yang kuat.'},

                # Soul row (2,5,8)
                {'id': 'soul_self_0', 'deskripsi': 'Kepekaan batiniah dari tanggal lahir belum dominan.'},
                {'id': 'soul_self_1', 'deskripsi': 'Intuisi dan perasaan pribadi hadir secara seimbang.'},
                {'id': 'soul_self_2', 'deskripsi': 'Sangat peka secara batiniah.'},
                {'id': 'soul_self_3', 'deskripsi': 'Empati batin mendalam dan kuat.'},
                {'id': 'soul_community_0', 'deskripsi': 'Empati terhadap lingkungan belum menonjol.'},
                {'id': 'soul_community_1', 'deskripsi': 'Peduli dan mampu memahami orang lain.'},
                {'id': 'soul_community_2', 'deskripsi': 'Kepedulian sosial yang tinggi.'},
                {'id': 'soul_community_3', 'deskripsi': 'Pengabdian emosional yang besar untuk komunitas.'},
                {'id': 'soul_world_0', 'deskripsi': 'Dorongan ambisi/keinginan jiwa pada dunia belum terlihat.'},
                {'id': 'soul_world_1', 'deskripsi': 'Ada dorongan untuk berperan lebih luas.'},
                {'id': 'soul_world_2', 'deskripsi': 'Dorongan batin untuk berkontribusi besar di dunia.'},

                # Body row (1,4,7)
                {'id': 'body_self_0', 'deskripsi': 'Kepercayaan diri dan kemandirian praktis belum menonjol.'},
                {'id': 'body_self_1', 'deskripsi': 'Mandiri dan praktis dalam bertindak.'},
                {'id': 'body_self_2', 'deskripsi': 'Sangat mandiri dan proaktif.'},
                {'id': 'body_self_3', 'deskripsi': 'Dominan dalam kemandirian dan inisiatif.'},
                {'id': 'body_community_0', 'deskripsi': 'Stabilitas dan keterandalan praktis belum kuat.'},
                {'id': 'body_community_1', 'deskripsi': 'Cukup stabil dan dapat diandalkan.'},
                {'id': 'body_community_2', 'deskripsi': 'Sangat stabil dan konsisten.'},
                {'id': 'body_community_3', 'deskripsi': 'Menjadi pilar stabilitas di lingkungan.'},
                {'id': 'body_world_0', 'deskripsi': 'Kebijaksanaan praktis terhadap dunia belum berkembang.'},
                {'id': 'body_world_1', 'deskripsi': 'Ada kecenderungan bijak dalam bertindak.'},
                {'id': 'body_world_2', 'deskripsi': 'Memiliki kebijaksanaan praktis yang kuat.'},
            ]

            for data in birth_chart_data:
                bc = BirthChart(**data)
                db.add(bc)

            db.commit()
            print('BirthChart data seeded successfully!')
    except Exception as e:
        print(f'Error seeding BirthChart data: {e}')
        db.rollback()
    finally:
        db.close()
    
    # Seed Personality data if table is empty
    db = SessionLocal()
    try:
        # Check if Personality data exists
        existing_personality = db.query(Personality).first()
        if not existing_personality:
            # Seed basic Personality data
            personality_data = [
                {
                    'no': 1,
                    'deskripsi': 'Anda terlihat sebagai sosok yang percaya diri, mandiri, dan berjiwa pemimpin. Orang lain melihat Anda sebagai individu yang berani mengambil inisiatif, inovatif, dan tidak takut menghadapi tantangan.'
                },
                {
                    'no': 2,
                    'deskripsi': 'Anda memberikan kesan sebagai orang yang ramah, kooperatif, dan mudah bergaul. Orang lain melihat Anda sebagai sosok yang diplomatik, pengertian, dan selalu siap membantu.'
                },
                {
                    'no': 3,
                    'deskripsi': 'Anda terlihat sebagai pribadi yang kreatif, ekspresif, dan penuh semangat. Orang lain melihat Anda sebagai sosok yang komunikatif, optimis, dan memiliki selera humor yang baik.'
                },
                {
                    'no': 4,
                    'deskripsi': 'Anda memberikan kesan sebagai orang yang dapat diandalkan, praktis, dan pekerja keras. Orang lain melihat Anda sebagai sosok yang terorganisir, disiplin, dan memiliki dedikasi tinggi.'
                },
                {
                    'no': 5,
                    'deskripsi': 'Anda terlihat sebagai pribadi yang dinamis, petualang, dan penuh energi. Orang lain melihat Anda sebagai sosok yang fleksibel, mudah beradaptasi, dan selalu siap mencoba hal-hal baru.'
                },
                {
                    'no': 6,
                    'deskripsi': 'Anda memberikan kesan sebagai orang yang peduli, bertanggung jawab, dan penuh kasih sayang. Orang lain melihat Anda sebagai sosok yang dapat dipercaya, protektif, dan selalu siap membantu keluarga dan teman.'
                },
                {
                    'no': 7,
                    'deskripsi': 'Anda terlihat sebagai pribadi yang bijaksana, misterius, dan mendalam. Orang lain melihat Anda sebagai sosok yang intelektual, spiritual, dan memiliki pemahaman yang mendalam tentang kehidupan.'
                },
                {
                    'no': 8,
                    'deskripsi': 'Anda memberikan kesan sebagai orang yang ambisius, sukses, dan berpengaruh. Orang lain melihat Anda sebagai sosok yang profesional, efisien, dan memiliki kemampuan bisnis yang baik.'
                },
                {
                    'no': 9,
                    'deskripsi': 'Anda terlihat sebagai pribadi yang mulia, altruistik, dan memiliki visi kemanusiaan. Orang lain melihat Anda sebagai sosok yang bijaksana, toleran, dan selalu siap membantu sesama.'
                },
                {
                    'no': 11,
                    'deskripsi': 'Anda memberikan kesan sebagai orang yang karismatik, inspiratif, dan memiliki intuisi yang kuat. Orang lain melihat Anda sebagai sosok yang visioner, spiritual, dan mampu memahami hal-hal yang tidak terlihat.'
                },
                {
                    'no': 22,
                    'deskripsi': 'Anda terlihat sebagai pribadi yang memiliki visi besar, kemampuan membangun yang luar biasa, dan potensi untuk menciptakan perubahan besar. Orang lain melihat Anda sebagai sosok yang praktis namun visioner.'
                }
            ]
            
            for data in personality_data:
                personality = Personality(**data)
                db.add(personality)
            
            db.commit()
            print('Personality data seeded successfully!')
    except Exception as e:
        print(f'Error seeding Personality data: {e}')
        db.rollback()
    finally:
        db.close()
    
    # Seed TenungLahir data if table is empty
    db = SessionLocal()
    try:
        # Check if TenungLahir data exists
        existing_tenung_lahir = db.query(TenungLahir).first()
        if not existing_tenung_lahir:
            # Seed basic TenungLahir data
            tenung_lahir_data = [
                # Root Numbers (O values 1-9)
                {'id': '1', 'deskripsi': 'Karakter kepemimpinan yang kuat, mandiri, dan inovatif. Anda memiliki kemampuan untuk memulai sesuatu yang baru dan memimpin orang lain dengan percaya diri.'},
                {'id': '2', 'deskripsi': 'Karakter yang kooperatif, diplomatik, dan sensitif terhadap kebutuhan orang lain. Anda unggul dalam kerjasama tim dan membangun hubungan harmonis.'},
                {'id': '3', 'deskripsi': 'Karakter yang kreatif, ekspresif, dan komunikatif. Anda memiliki bakat artistik dan kemampuan untuk menginspirasi orang lain melalui kata-kata dan kreativitas.'},
                {'id': '4', 'deskripsi': 'Karakter yang praktis, terorganisir, dan pekerja keras. Anda memiliki dedikasi tinggi untuk membangun fondasi yang kuat dalam segala aspek kehidupan.'},
                {'id': '5', 'deskripsi': 'Karakter yang dinamis, petualang, dan bebas. Anda menyukai perubahan, petualangan, dan memiliki kemampuan adaptasi yang tinggi.'},
                {'id': '6', 'deskripsi': 'Karakter yang peduli, bertanggung jawab, dan penuh kasih sayang. Anda memiliki naluri mengasuh yang kuat dan selalu siap membantu keluarga dan komunitas.'},
                {'id': '7', 'deskripsi': 'Karakter yang bijaksana, spiritual, dan analitis. Anda memiliki kemampuan untuk memahami hal-hal yang mendalam dan sering menjadi pencari kebenaran.'},
                {'id': '8', 'deskripsi': 'Karakter yang ambisius, berorientasi pada kesuksesan material, dan memiliki kemampuan bisnis yang baik. Anda unggul dalam mengelola sumber daya dan mencapai tujuan besar.'},
                {'id': '9', 'deskripsi': 'Karakter yang humanis, bijaksana, dan memiliki visi universal. Anda memiliki kemampuan untuk melayani kemanusiaan dan memberikan kontribusi positif bagi dunia.'},
                # Sample M&N combinations
                {'id': '11', 'deskripsi': 'Kombinasi yang menunjukkan intuisi tinggi dan kemampuan spiritual. Anda memiliki potensi untuk menjadi inspirasi bagi orang lain.'},
                {'id': '22', 'deskripsi': 'Kombinasi master yang menunjukkan kemampuan membangun visi besar. Anda memiliki potensi untuk mewujudkan impian menjadi kenyataan.'},
                {'id': '33', 'deskripsi': 'Kombinasi master yang menunjukkan kemampuan mengajar dan menginspirasi. Anda memiliki potensi untuk menjadi guru spiritual.'}
            ]
            
            for data in tenung_lahir_data:
                tenung_lahir = TenungLahir(**data)
                db.add(tenung_lahir)
            
            db.commit()
            print('TenungLahir data seeded successfully!')
    except Exception as e:
        print(f'Error seeding TenungLahir data: {e}')
        db.rollback()
    finally:
        db.close()
    
    # Seed Prediksi data if table is empty
    db = SessionLocal()
    try:
        # Check if Prediksi data exists
        existing_prediksi = db.query(Prediksi).first()
        if not existing_prediksi:
            # Seed basic Prediksi data (sample - full data in init_prediksi.py)
            prediksi_data = [
                {'kondisi': 'I=1', 'makna': 'Pusat perhatian, ambisius, sulit mengakui kekalahan, banyak masalah, keras kepala, mandiri, perfeksionis.'},
                {'kondisi': 'N=1', 'makna': 'Sangat egois, menentang aturan, mandiri, menciptakan drama dan pengalihan perhatian.'},
                {'kondisi': 'I=2', 'makna': 'Sensitif, lembut, menerima, mudah terpengaruh, malas dan apatis, dapat berganti peran dengan cepat.'},
                {'kondisi': 'IJK=111', 'makna': 'Potensi cerai, lelaki: beberapa kali gagal dalam percintaan; perempuan: pembawa sial atau keburukan bagi pasangannya.'},
                {'kondisi': 'IJKL=1111', 'makna': 'Perselisihan, perceraian, prahara rumah tangga.'}
            ]
            
            for data in prediksi_data:
                prediksi = Prediksi(**data)
                db.add(prediksi)
            
            db.commit()
            print('Prediksi data seeded successfully!')
    except Exception as e:
        print(f'Error seeding Prediksi data: {e}')
        db.rollback()
    finally:
        db.close()
    
    # Seed PapanPythagoras data if table is empty
    db = SessionLocal()
    try:
        # Check if PapanPythagoras data exists
        existing_pythagoras = db.query(PapanPythagoras).first()
        if not existing_pythagoras:
            # Seed basic PapanPythagoras data
            pythagoras_data = [
                # Mind-Self (position 3)
                {'id': 'mind_self_0', 'deskripsi': 'Kurangnya kemampuan berpikir kreatif dan inovatif. Perlu mengembangkan ide-ide baru.'},
                {'id': 'mind_self_1', 'deskripsi': 'Memiliki kemampuan berpikir kreatif yang baik, mampu menghasilkan ide-ide segar.'},
                {'id': 'mind_self_2', 'deskripsi': 'Sangat kreatif dalam berpikir, memiliki banyak ide inovatif dan solusi unik.'},
                {'id': 'mind_self_3', 'deskripsi': 'Kreativitas mental yang luar biasa, mampu berpikir out-of-the-box dengan mudah.'},
                
                # Mind-Community (position 6)
                {'id': 'mind_community_0', 'deskripsi': 'Kurang dalam kemampuan berkomunikasi dan berinteraksi dengan komunitas.'},
                {'id': 'mind_community_1', 'deskripsi': 'Memiliki kemampuan komunikasi yang baik dengan komunitas sekitar.'},
                {'id': 'mind_community_2', 'deskripsi': 'Sangat baik dalam berkomunikasi dan membangun hubungan dengan komunitas.'},
                
                # Mind-World (position 9)
                {'id': 'mind_world_0', 'deskripsi': 'Kurang memiliki visi global dan pemahaman tentang dunia luas.'},
                {'id': 'mind_world_1', 'deskripsi': 'Memiliki pemahaman yang baik tentang dunia dan visi global.'},
                {'id': 'mind_world_2', 'deskripsi': 'Sangat visioner dengan pemahaman mendalam tentang dunia dan kemanusiaan.'},
                
                # Soul-Self (position 2)
                {'id': 'soul_self_0', 'deskripsi': 'Kurang sensitif terhadap perasaan diri sendiri, perlu mengembangkan intuisi.'},
                {'id': 'soul_self_1', 'deskripsi': 'Memiliki kepekaan emosional yang baik terhadap diri sendiri.'},
                {'id': 'soul_self_2', 'deskripsi': 'Sangat sensitif dan intuitif, memahami perasaan diri dengan mendalam.'},
                {'id': 'soul_self_3', 'deskripsi': 'Kepekaan emosional yang luar biasa, sangat intuitif dan empatis.'},
                {'id': 'soul_self_4', 'deskripsi': 'Sensitivitas yang sangat tinggi, kadang terlalu emosional.'},
                {'id': 'soul_self_5', 'deskripsi': 'Kepekaan emosional yang berlebihan, perlu keseimbangan.'},
                
                # Soul-Community (position 5)
                {'id': 'soul_community_0', 'deskripsi': 'Kurang dalam kemampuan berempati dan memahami perasaan orang lain.'},
                {'id': 'soul_community_1', 'deskripsi': 'Memiliki empati yang baik terhadap komunitas sekitar.'},
                {'id': 'soul_community_2', 'deskripsi': 'Sangat empatik dan peduli terhadap perasaan komunitas.'},
                {'id': 'soul_community_3', 'deskripsi': 'Empati yang luar biasa, mampu merasakan dan memahami orang lain dengan mendalam.'},
                {'id': 'soul_community_4', 'deskripsi': 'Kepedulian yang sangat tinggi terhadap komunitas, kadang berlebihan.'},
                
                # Soul-World (position 8)
                {'id': 'soul_world_0', 'deskripsi': 'Kurang memiliki ambisi dan dorongan untuk mencapai kesuksesan material.'},
                {'id': 'soul_world_1', 'deskripsi': 'Memiliki ambisi yang sehat untuk mencapai kesuksesan di dunia.'},
                {'id': 'soul_world_2', 'deskripsi': 'Sangat ambisius dan berorientasi pada kesuksesan material.'},
                
                # Body-Self (position 1)
                {'id': 'body_self_0', 'deskripsi': 'Kurang memiliki kepercayaan diri dan kemandirian dalam bertindak.'},
                {'id': 'body_self_1', 'deskripsi': 'Memiliki kepercayaan diri yang baik dan mampu mandiri.'},
                {'id': 'body_self_2', 'deskripsi': 'Sangat percaya diri dan mandiri, mampu memimpin diri sendiri.'},
                {'id': 'body_self_3', 'deskripsi': 'Kepercayaan diri yang luar biasa, sangat mandiri dan berani.'},
                {'id': 'body_self_4', 'deskripsi': 'Kemandirian yang sangat tinggi, kadang terlalu individualistis.'},
                {'id': 'body_self_5', 'deskripsi': 'Kepercayaan diri berlebihan, perlu keseimbangan dengan kerendahan hati.'},
                {'id': 'body_self_6', 'deskripsi': 'Kemandirian ekstrem, cenderung egois dan sulit bekerja sama.'},
                {'id': 'body_self_7', 'deskripsi': 'Individualisme yang berlebihan, perlu belajar kolaborasi.'},
                {'id': 'body_self_8', 'deskripsi': 'Sangat individualistis, sulit menerima bantuan atau saran orang lain.'},
                
                # Body-Community (position 4)
                {'id': 'body_community_0', 'deskripsi': 'Kurang stabil dan kurang dapat diandalkan dalam komunitas.'},
                {'id': 'body_community_1', 'deskripsi': 'Memiliki stabilitas yang baik dan dapat diandalkan oleh komunitas.'},
                {'id': 'body_community_2', 'deskripsi': 'Sangat stabil dan dapat diandalkan, menjadi pilar komunitas.'},
                {'id': 'body_community_3', 'deskripsi': 'Stabilitas yang luar biasa, sangat dapat diandalkan dan konsisten.'},
                
                # Body-World (position 7)
                {'id': 'body_world_0', 'deskripsi': 'Kurang memiliki kebijaksanaan dan pemahaman spiritual tentang dunia.'},
                {'id': 'body_world_1', 'deskripsi': 'Memiliki kebijaksanaan yang baik dalam memahami dunia.'},
                {'id': 'body_world_2', 'deskripsi': 'Sangat bijaksana dan memiliki pemahaman spiritual yang mendalam.'},
            ]
            
            for data in pythagoras_data:
                pythagoras = PapanPythagoras(**data)
                db.add(pythagoras)
            
            db.commit()
            print('PapanPythagoras data seeded successfully!')
    except Exception as e:
        print(f'Error seeding PapanPythagoras data: {e}')
        db.rollback()
    finally:
        db.close()
    
    # Seed AngkaTerisolasi data if table is empty
    db = SessionLocal()
    try:
        # Check if AngkaTerisolasi data exists
        existing_terisolasi = db.query(AngkaTerisolasi).first()
        if not existing_terisolasi:
            # Seed AngkaTerisolasi data
            terisolasi_data = [
                {
                    'angka': 1,
                    'deskripsi': 'Angka 1 terisolasi menunjukkan kepemimpinan yang sangat mandiri namun cenderung individualistis. Anda memiliki kemampuan memimpin yang kuat tetapi mungkin kesulitan dalam bekerja sama dengan orang lain. Perlu belajar untuk lebih terbuka terhadap masukan dan kolaborasi.'
                },
                {
                    'angka': 3,
                    'deskripsi': 'Angka 3 terisolasi menandakan kreativitas dan komunikasi yang unik namun terkadang sulit dipahami orang lain. Anda memiliki ide-ide brilian dan cara berkomunikasi yang khas, tetapi mungkin perlu usaha ekstra untuk menyampaikan pemikiran Anda dengan jelas kepada orang lain.'
                },
                {
                    'angka': 7,
                    'deskripsi': 'Angka 7 terisolasi menunjukkan kebijaksanaan spiritual yang mendalam namun cenderung menyendiri. Anda memiliki pemahaman spiritual dan intuisi yang kuat, tetapi mungkin merasa sulit untuk berbagi pengalaman spiritual Anda dengan orang lain. Perlu keseimbangan antara kontemplasi dan interaksi sosial.'
                },
                {
                    'angka': 9,
                    'deskripsi': 'Angka 9 terisolasi menandakan visi humanis yang luas namun terkadang idealistis berlebihan. Anda memiliki kepedulian besar terhadap kemanusiaan dan visi global yang kuat, tetapi mungkin frustrasi ketika realitas tidak sesuai dengan idealisme Anda. Perlu belajar untuk menerima keterbatasan dan bekerja secara bertahap.'
                }
            ]
            
            for data in terisolasi_data:
                terisolasi = AngkaTerisolasi(**data)
                db.add(terisolasi)
            
            db.commit()
            print('AngkaTerisolasi data seeded successfully!')
    except Exception as e:
        print(f'Error seeding AngkaTerisolasi data: {e}')
        db.rollback()
    finally:
        db.close()
    
    # Seed Chaldean data if table is empty
    db = SessionLocal()
    try:
        # Check if Chaldean data exists
        existing_chaldean = db.query(Chaldean).first()
        if not existing_chaldean:
            # Seed Chaldean data
            chaldean_data = [
                {
                    'id': 1,
                    'deskripsi': 'Angka 1 dalam sistem Chaldean melambangkan kepemimpinan, kemandirian, dan inovasi. Anda memiliki jiwa pionir yang kuat dan kemampuan untuk memulai hal-hal baru. Kepribadian Anda memancarkan otoritas alami dan kemampuan untuk menginspirasi orang lain.'
                },
                {
                    'id': 2,
                    'deskripsi': 'Angka 2 dalam sistem Chaldean menunjukkan sifat kooperatif, diplomatis, dan sensitif. Anda adalah peacemaker alami yang pandai dalam kerjasama dan membangun hubungan harmonis. Intuisi dan empati Anda sangat kuat.'
                },
                {
                    'id': 3,
                    'deskripsi': 'Angka 3 dalam sistem Chaldean melambangkan kreativitas, ekspresi diri, dan komunikasi. Anda memiliki bakat artistik dan kemampuan komunikasi yang luar biasa. Kepribadian Anda ceria, optimis, dan mampu menginspirasi orang lain.'
                },
                {
                    'id': 4,
                    'deskripsi': 'Angka 4 dalam sistem Chaldean menunjukkan stabilitas, kerja keras, dan praktikalitas. Anda adalah orang yang dapat diandalkan, metodis, dan memiliki dedikasi tinggi. Kemampuan organisasi dan perencanaan Anda sangat baik.'
                },
                {
                    'id': 5,
                    'deskripsi': 'Angka 5 dalam sistem Chaldean melambangkan kebebasan, petualangan, dan perubahan. Anda memiliki jiwa yang dinamis, suka tantangan, dan selalu mencari pengalaman baru. Adaptabilitas dan fleksibilitas adalah kekuatan utama Anda.'
                },
                {
                    'id': 6,
                    'deskripsi': 'Angka 6 dalam sistem Chaldean menunjukkan tanggung jawab, kasih sayang, dan orientasi keluarga. Anda adalah pengasuh alami yang peduli dengan kesejahteraan orang lain. Kemampuan untuk menciptakan harmoni dan keseimbangan sangat menonjol.'
                },
                {
                    'id': 7,
                    'deskripsi': 'Angka 7 dalam sistem Chaldean melambangkan spiritualitas, introspeksi, dan pencarian kebenaran. Anda memiliki kecenderungan filosofis yang kuat dan kemampuan analitis yang mendalam. Intuisi spiritual Anda sangat berkembang.'
                },
                {
                    'id': 8,
                    'deskripsi': 'Angka 8 dalam sistem Chaldean menunjukkan ambisi, kekuatan material, dan kemampuan bisnis. Anda memiliki potensi besar untuk mencapai kesuksesan finansial dan posisi otoritas. Kemampuan manajemen dan organisasi sangat kuat.'
                },
                {
                    'id': 9,
                    'deskripsi': 'Angka 9 dalam sistem Chaldean melambangkan kebijaksanaan, humanitarianisme, dan pelayanan universal. Anda memiliki visi luas dan keinginan kuat untuk berkontribusi pada kebaikan umat manusia. Kepemimpinan spiritual dan empati universal adalah kekuatan Anda.'
                }
            ]
            
            for data in chaldean_data:
                chaldean = Chaldean(**data)
                db.add(chaldean)
            
            db.commit()
            print('Chaldean data seeded successfully!')
    except Exception as e:
        print(f'Error seeding Chaldean data: {e}')
        db.rollback()
    finally:
        db.close()

    # Seed Admin user from environment variables if provided
    admin_email = os.environ.get('ADMIN_EMAIL')
    admin_password = os.environ.get('ADMIN_PASSWORD')
    if admin_email and admin_password:
        db = SessionLocal()
        try:
            existing_admin = db.query(User).filter(User.email == admin_email).first()
            if not existing_admin:
                admin_user = User(
                    email=admin_email.strip().lower(),
                    password_hash=generate_password_hash(admin_password.strip()),
                    role='admin',
                    is_active=True,
                )
                db.add(admin_user)
                db.commit()
                print(f"Admin user seeded: {admin_email}")
        except Exception as e:
            print(f"Error seeding admin user: {e}")
            db.rollback()
        finally:
            db.close()

    # Seed AngkaBerderet data if table is empty
    db = SessionLocal()
    try:
        # Check if AngkaBerderet data exists
        existing_berderet = db.query(AngkaBerderet).first()
        if not existing_berderet:
            # Seed AngkaBerderet data
            berderet_data = [
                # Diagonal patterns
                {
                    'id': 'diagonal_159_deret',
                    'status': 'deret',
                    'deskripsi': 'Diagonal 1-5-9 lengkap menunjukkan keseimbangan sempurna antara kepemimpinan (1), adaptabilitas (5), dan visi universal (9). Anda memiliki kemampuan untuk memimpin dengan bijaksana dan visi yang luas.'
                },
                {
                    'id': 'diagonal_159_tanpa',
                    'status': 'tanpa',
                    'deskripsi': 'Diagonal 1-5-9 kosong menandakan kurangnya keseimbangan antara kepemimpinan, adaptabilitas, dan visi. Perlu mengembangkan kemampuan memimpin dan memperluas perspektif hidup.'
                },
                {
                    'id': 'diagonal_357_deret',
                    'status': 'deret',
                    'deskripsi': 'Diagonal 3-5-7 lengkap menunjukkan keseimbangan antara kreativitas (3), perubahan (5), dan spiritualitas (7). Anda memiliki kemampuan untuk mengekspresikan diri secara kreatif dengan landasan spiritual yang kuat.'
                },
                {
                    'id': 'diagonal_357_tanpa',
                    'status': 'tanpa',
                    'deskripsi': 'Diagonal 3-5-7 kosong menandakan kurangnya keseimbangan antara kreativitas, perubahan, dan spiritualitas. Perlu mengembangkan ekspresi kreatif dan pemahaman spiritual.'
                },
                
                # Row patterns
                {
                    'id': 'baris_body_deret',
                    'status': 'deret',
                    'deskripsi': 'Baris Body (1-4-7) lengkap menunjukkan kekuatan fisik dan praktis yang seimbang. Anda memiliki kemampuan kepemimpinan, stabilitas, dan kebijaksanaan dalam tindakan nyata.'
                },
                {
                    'id': 'baris_body_tanpa',
                    'status': 'tanpa',
                    'deskripsi': 'Baris Body (1-4-7) kosong menandakan kurangnya energi fisik dan praktis. Perlu mengembangkan kemampuan untuk bertindak nyata dan membangun stabilitas hidup.'
                },
                {
                    'id': 'baris_soul_deret',
                    'status': 'deret',
                    'deskripsi': 'Baris Soul (2-5-8) lengkap menunjukkan keseimbangan emosional dan spiritual yang kuat. Anda memiliki kepekaan, adaptabilitas, dan kemampuan mencapai kesuksesan material dengan landasan spiritual.'
                },
                {
                    'id': 'baris_soul_tanpa',
                    'status': 'tanpa',
                    'deskripsi': 'Baris Soul (2-5-8) kosong menandakan kurangnya keseimbangan emosional dan spiritual. Perlu mengembangkan kepekaan perasaan dan koneksi spiritual.'
                },
                {
                    'id': 'baris_mind_deret',
                    'status': 'deret',
                    'deskripsi': 'Baris Mind (3-6-9) lengkap menunjukkan kekuatan mental dan intelektual yang seimbang. Anda memiliki kreativitas, tanggung jawab, dan visi yang komprehensif.'
                },
                {
                    'id': 'baris_mind_tanpa',
                    'status': 'tanpa',
                    'deskripsi': 'Baris Mind (3-6-9) kosong menandakan kurangnya aktivitas mental dan intelektual. Perlu mengembangkan kemampuan berpikir kreatif dan analitis.'
                },
                
                # Column patterns
                {
                    'id': 'kolom_self_deret',
                    'status': 'deret',
                    'deskripsi': 'Kolom Self (1-2-3) lengkap menunjukkan pengembangan diri yang seimbang. Anda memiliki kepemimpinan, kepekaan, dan kreativitas yang terfokus pada pertumbuhan personal.'
                },
                {
                    'id': 'kolom_self_tanpa',
                    'status': 'tanpa',
                    'deskripsi': 'Kolom Self (1-2-3) kosong menandakan kurangnya fokus pada pengembangan diri. Perlu lebih memperhatikan pertumbuhan personal dan pemahaman diri.'
                },
                {
                    'id': 'kolom_community_deret',
                    'status': 'deret',
                    'deskripsi': 'Kolom Community (4-5-6) lengkap menunjukkan kemampuan berinteraksi dengan komunitas yang baik. Anda memiliki stabilitas, adaptabilitas, dan tanggung jawab dalam hubungan sosial.'
                },
                {
                    'id': 'kolom_community_tanpa',
                    'status': 'tanpa',
                    'deskripsi': 'Kolom Community (4-5-6) kosong menandakan kurangnya keterlibatan dengan komunitas. Perlu mengembangkan kemampuan bersosialisasi dan berkontribusi pada masyarakat.'
                },
                {
                    'id': 'kolom_world_deret',
                    'status': 'deret',
                    'deskripsi': 'Kolom World (7-8-9) lengkap menunjukkan orientasi global yang kuat. Anda memiliki kebijaksanaan, kemampuan material, dan visi universal untuk berkontribusi pada dunia.'
                },
                {
                    'id': 'kolom_world_tanpa',
                    'status': 'tanpa',
                    'deskripsi': 'Kolom World (7-8-9) kosong menandakan kurangnya orientasi global. Perlu memperluas perspektif dan meningkatkan kontribusi pada skala yang lebih luas.'
                }
            ]
            
            for data in berderet_data:
                berderet = AngkaBerderet(**data)
                db.add(berderet)
            
            db.commit()
            print('AngkaBerderet data seeded successfully!')
    except Exception as e:
        print(f'Error seeding AngkaBerderet data: {e}')
        db.rollback()
    finally:
        db.close()
    
    # Seed TenungKarma data if table is empty
    db = SessionLocal()
    try:
        # Check if TenungKarma data exists
        existing_karma = db.query(TenungKarma).first()
        if not existing_karma:
            # Seed sample TenungKarma data (N-D-L combinations)
            tenung_karma_data = [
                {'id': '1-0-1', 'arti': 'Karma Keseimbangan', 'deskripsi': 'Kombinasi yang menunjukkan kebutuhan untuk mencari keseimbangan antara ego dan kerendahan hati. Anda memiliki potensi kepemimpinan yang kuat namun perlu belajar untuk tidak terlalu dominan.'},
                {'id': '2-0-2', 'arti': 'Karma Kerjasama', 'deskripsi': 'Pelajaran hidup tentang pentingnya kerjasama dan diplomasi. Anda cenderung terlalu sensitif dan perlu belajar untuk lebih tegas dalam mengambil keputusan.'},
                {'id': '3-0-3', 'arti': 'Karma Kreativitas', 'deskripsi': 'Kombinasi yang mengharuskan Anda mengembangkan bakat kreatif dan komunikasi. Hindari kecenderungan untuk terlalu kritis terhadap diri sendiri dan orang lain.'},
                {'id': '4-0-4', 'arti': 'Karma Kerja Keras', 'deskripsi': 'Pelajaran tentang disiplin, ketekunan, dan membangun fondasi yang kuat. Anda perlu belajar untuk tidak terlalu kaku dan membuka diri terhadap perubahan.'},
                {'id': '5-0-5', 'arti': 'Karma Kebebasan', 'deskripsi': 'Kombinasi yang menuntut Anda untuk belajar menggunakan kebebasan dengan bijak. Hindari kecenderungan untuk terlalu impulsif dan tidak bertanggung jawab.'},
                {'id': '6-0-6', 'arti': 'Karma Pelayanan', 'deskripsi': 'Pelajaran hidup tentang cinta, pengasuhan, dan tanggung jawab terhadap keluarga. Anda perlu belajar untuk tidak terlalu mengontrol dan membiarkan orang lain tumbuh.'},
                {'id': '7-0-7', 'arti': 'Karma Spiritual', 'deskripsi': 'Kombinasi yang mengharuskan Anda mengembangkan kebijaksanaan dan spiritualitas. Hindari kecenderungan untuk terlalu menyendiri dan menutup diri dari dunia.'},
                {'id': '8-0-8', 'arti': 'Karma Material', 'deskripsi': 'Pelajaran tentang kekuasaan, otoritas, dan kesuksesan material. Anda perlu belajar untuk tidak terlalu serakah dan menggunakan kekuasaan dengan bijak.'},
                {'id': '9-0-9', 'arti': 'Karma Universal', 'deskripsi': 'Kombinasi yang menuntut Anda untuk melayani kemanusiaan dengan cinta universal. Hindari kecenderungan untuk terlalu idealis dan tidak praktis.'},
                # Sample combinations with different D values
                {'id': '7-2-3', 'arti': 'Karma Transformasi', 'deskripsi': 'Kombinasi yang menunjukkan perjalanan spiritual melalui tantangan emosional. Anda memiliki kemampuan untuk mentransformasi penderitaan menjadi kebijaksanaan.'},
                {'id': '3-1-5', 'arti': 'Karma Ekspresi', 'deskripsi': 'Pelajaran tentang mengekspresikan kreativitas dengan cara yang konstruktif. Anda perlu belajar untuk fokus dan tidak menyebarkan energi terlalu tipis.'},
                {'id': '5-2-1', 'arti': 'Karma Pionir', 'deskripsi': 'Kombinasi yang mengharuskan Anda menjadi pelopor perubahan dengan cara yang bertanggung jawab. Keseimbangan antara kebebasan dan kepemimpinan adalah kunci.'},
                {'id': '1-1-9', 'arti': 'Karma Pelayanan Kepemimpinan', 'deskripsi': 'Pelajaran tentang memimpin dengan melayani. Anda memiliki potensi untuk menjadi pemimpin yang menginspirasi melalui contoh dan dedikasi.'},
                {'id': '9-1-1', 'arti': 'Karma Kebijaksanaan Aksi', 'deskripsi': 'Kombinasi yang menuntut Anda untuk mengaplikasikan kebijaksanaan universal dalam tindakan nyata. Hindari kecenderungan untuk hanya berteori tanpa praktek.'},
                {'id': '4-2-8', 'arti': 'Karma Struktur Kekuasaan', 'deskripsi': 'Pelajaran tentang membangun sistem yang adil dan berkelanjutan. Anda perlu belajar untuk menyeimbangkan ambisi material dengan nilai-nilai moral.'},
                {'id': '6-3-2', 'arti': 'Karma Harmoni Keluarga', 'deskripsi': 'Kombinasi yang mengharuskan Anda menciptakan harmoni dalam hubungan keluarga melalui komunikasi yang baik dan empati yang mendalam.'}
            ]
            
            for data in tenung_karma_data:
                karma = TenungKarma(**data)
                db.add(karma)
            
            db.commit()
            print('TenungKarma data seeded successfully!')
    except Exception as e:
        print(f'Error seeding TenungKarma data: {e}')
        db.rollback()
    finally:
        db.close()
