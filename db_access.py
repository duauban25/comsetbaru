from __future__ import annotations
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session

from db import (
    SessionLocal,
    LifePath,
    Tantangan,
    HaraniNama,
    Karma,
    Rejeki,
    ArahSukses,
    LintangBali,
    DeskWewaran,
    HariLahir,
    WukuName,
    WetonArti,
    WetonArtiPair,
    WukuAwal,
    TenungNama,
    Panggilan,
    BridgeName,
    BridgeNumber,
    KarmicDebt,
    HeartDesire,
    Personality,
    SoulUrge,
    OuterExpression,
    TenungLahir,
    Prediksi,
    TenungKarma,
    PapanPythagoras,
    AngkaTerisolasi,
    AngkaBerderet,
    Chaldean,
    BirthChart,
    BirthChartEmptyCombo,
    ArrowIndividual,
)
from sqlalchemy import text


def get_session() -> Session:
    return SessionLocal()


# Life Path
def get_life_path(no: int, db: Optional[Session] = None) -> Optional[dict]:
    close = False
    if db is None:
        db = get_session()
        close = True
    try:
        row = db.get(LifePath, no)
        if not row:
            return None
        return {
            'no': row.no,
            'deskripsi': row.deskripsi or '',
            'detail': row.detail or '',
            'kekuatan': row.kekuatan or '',
            'tantangan': row.tantangan or '',
            'penjelasan': row.penjelasan_html or '',
        }
    finally:
        if close:
            db.close()


# Birth Chart Empty Combo
def get_birth_chart_empty_combo_desc(keys: list[str], db: Optional[Session] = None) -> dict:
    """Fetch descriptions for empty box combinations.
    - keys: list of position keys like 'mind_self', 'soul_world', ...
    Returns dict with optional 'combined' and 'items' list of {key, deskripsi}.
    """
    result = {'combined': None, 'entries': []}
    if not keys:
        return result
    close = False
    if db is None:
        db = get_session()
        close = True
    try:
        # Individual keys
        rows = (
            db.query(BirthChartEmptyCombo)
            .filter(BirthChartEmptyCombo.id.in_(keys))
            .all()
        )
        for r in rows:
            result['entries'].append({'key': r.id, 'deskripsi': r.deskripsi or ''})

        # Combined key attempt in stable order
        combined_key = "+".join(sorted(keys))
        r = db.get(BirthChartEmptyCombo, combined_key)
        if r and (r.deskripsi or '').strip():
            result['combined'] = r.deskripsi
        return result
    finally:
        if close:
            db.close()


def get_arrow_individual(key: str, db: Optional[Session] = None) -> Optional[dict]:
    """Fetch ArrowIndividual by id. Returns {'title':..., 'deskripsi':...} or None."""
    close = False
    if db is None:
        db = get_session()
        close = True
    try:
        r = db.query(ArrowIndividual).filter(ArrowIndividual.id == key).first()
        if r:
            return {'title': r.title or '', 'deskripsi': r.deskripsi or ''}
        return None
    except Exception as e:
        print(f"Error getting arrow individual: {e}")
        return None
    finally:
        if close:
            db.close()


# Birth Chart
def get_birth_chart_desc(desc_key: str, db: Optional[Session] = None) -> str:
    """Get description for Birth Chart position and count.
    Keys look like 'mind_self_2', 'soul_world_0', etc.
    """
    close = False
    if db is None:
        db = get_session()
        close = True
    try:
        # 1) Try exact match via ORM
        r = db.query(BirthChart).filter(BirthChart.id == desc_key).first()
        if r and (r.deskripsi or '').strip():
            return r.deskripsi or ''

        # 2) Try trimmed/cast raw SQL to handle numeric/text typing differences
        try:
            sql = text("""
                SELECT deskripsi FROM birth_chart
                WHERE id = :k
                   OR CAST(id AS TEXT) = :k
                   OR id = CAST(:k AS INTEGER)
                   OR TRIM(CAST(id AS TEXT)) = TRIM(:k)
                LIMIT 1
            """)
            row = db.execute(sql, {"k": str(desc_key)}).fetchone()
            if row and row[0]:
                return row[0]
        except Exception:
            pass

        return f'Deskripsi untuk {desc_key} belum tersedia'
    except Exception as e:
        print(f"Error getting birth chart description: {e}")
        return f'Deskripsi untuk {desc_key} belum tersedia'
    finally:
        if close:
            db.close()


# Karmic Debt (double-digit 13/14/16/19)
def get_karmic_debt(no: int, db: Optional[Session] = None) -> Optional[str]:
    """Fetch Karmic Debt description for 13, 14, 16, 19."""
    if not no:
        return None
    close = False
    if db is None:
        db = get_session()
        close = True
    try:
        r = db.get(KarmicDebt, int(no))
        return (r.deskripsi or '') if r else None
    finally:
        if close:
            db.close()


# Arah Sukses
def get_arah_deskripsi(direction: str, db: Optional[Session] = None) -> Optional[str]:
    """Get arah sukses description by direction."""
    if not direction:
        return None
    close = False
    if db is None:
        db = get_session()
        close = True
    try:
        r = db.query(ArahSukses).filter(ArahSukses.arah == direction).first()
        return (r.deskripsi or '') if r else None
    finally:
        if close:
            db.close()


# Heart's Desire (1-9)
def get_heart_desire(no: int, db: Optional[Session] = None) -> Optional[dict]:
    """Fetch Heart's Desire description and details for numbers 1-9.

    IMPORTANT: Connect to the SAME SQLite file used by SQLAlchemy (engine.url.database)
    to avoid path mismatches that would trigger fallback rendering.
    """
    if not no or no < 1 or no > 9:
        return None
    
    # Use direct SQL but ensure we open the exact DB file SQLAlchemy uses
    import sqlite3
    from db import engine
    try:
        db_path = engine.url.database  # absolute path to app.db
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT no, deskripsi, kekuatan, kelemahan, saran FROM heart_desire WHERE no = ?', (no,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'deskripsi': result[1] or '',
                'kekuatan': result[2] or '',
                'kelemahan': result[3] or '',
                'saran': result[4] or ''
            }
        return None
    except Exception as e:
        print(f'Heart Desire DB error: {e}')
        return None


# Personality Number (1-9, 11, 22)
def get_personality(no: int, db: Optional[Session] = None) -> Optional[str]:
    """Fetch Personality description for numbers 1-9, 11, 22.

    IMPORTANT: Connect to the SAME SQLite file used by SQLAlchemy (engine.url.database)
    to avoid path mismatches that would trigger fallback rendering.
    """
    if not no or (no < 1 or no > 22) or (no > 9 and no not in (11, 22)):
        return None
    
    # Use direct SQL but ensure we open the exact DB file SQLAlchemy uses
    import sqlite3
    from db import engine
    try:
        db_path = engine.url.database  # absolute path to app.db
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT deskripsi FROM personality WHERE no = ?', (no,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return result[0] or ''
        return None
    except Exception as e:
        print(f'Personality DB error: {e}')
        return None


# Soul Urge (1-9)
def get_soul_urge(no: int, db: Optional[Session] = None) -> Optional[str]:
    """Fetch Soul Urge description for numbers 1-9."""
    if not no or no < 1 or no > 9:
        return None
    import sqlite3
    from db import engine
    try:
        db_path = engine.url.database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT deskripsi FROM soul_urge WHERE no = ?', (no,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return row[0] or ''
        return None
    except Exception as e:
        print(f'Soul Urge DB error: {e}')
        return None


# Outer Expression (1-9)
def get_outer_expression(no: int, db: Optional[Session] = None) -> Optional[str]:
    """Fetch Outer Expression description for numbers 1-9."""
    if not no or no < 1 or no > 9:
        return None
    import sqlite3
    from db import engine
    try:
        db_path = engine.url.database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT deskripsi FROM outer_expression WHERE no = ?', (no,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return row[0] or ''
        return None
    except Exception as e:
        print(f'Outer Expression DB error: {e}')
        return None


# Tenung Lahir (Character from birth date)
def get_tenung_lahir(id_key: str, db: Optional[Session] = None) -> Optional[str]:
    """Fetch Tenung Lahir description by ID key (O value or M&N combination).

    IMPORTANT: Connect to the SAME SQLite file used by SQLAlchemy (engine.url.database)
    to avoid path mismatches that would trigger fallback rendering.
    """
    if not id_key:
        return None
    
    # Use direct SQL but ensure we open the exact DB file SQLAlchemy uses
    import sqlite3
    from db import engine
    try:
        db_path = engine.url.database  # absolute path to app.db
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT deskripsi FROM tenung_lahir WHERE id = ?', (str(id_key),))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return result[0] or ''
        return None
    except Exception as e:
        print(f'Tenung Lahir DB error: {e}')
        return None


# Prediksi (Predictions from birth date matrix)
def get_prediksi_by_kondisi(kondisi: str, db: Optional[Session] = None) -> Optional[str]:
    """Fetch Prediksi meaning by condition string.
    
    Args:
        kondisi: Condition string like "I=1", "JK=11", "IJK=111", etc.
    
    Returns:
        Prediction meaning or None if not found
    """
    if not kondisi:
        return None
    
    # Use direct SQL but ensure we open the exact DB file SQLAlchemy uses
    import sqlite3
    from db import engine
    try:
        db_path = engine.url.database  # absolute path to app.db
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT makna FROM prediksi WHERE kondisi = ?', (kondisi,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return result[0] or ''
        return None
    except Exception as e:
        print(f'Prediksi DB error: {e}')
        return None

def get_bridge_details(key: str, db: Optional[Session] = None) -> Optional[dict]:
    """Fetch full bridge details by key from bridge_number table.
    Key examples: "1", "2", "3-5".
    Returns dict with: deskripsi, makna, tantangan, saran.
    """
    if not key:
        return None
    close = False
    if db is None:
        db = get_session()
        close = True
    try:
        r = db.get(BridgeNumber, str(key))
        if not r:
            return None
        return {
            'deskripsi': r.deskripsi or '',
            'makna': r.makna or '',
            'tantangan': r.tantangan or '',
            'saran': r.saran or '',
        }
    finally:
        if close:
            db.close()


# Bridge Name
def get_bridge_name(bgride: str, db: Optional[Session] = None) -> Optional[str]:
    if not bgride:
        return None
    close = False
    if db is None:
        db = get_session()
        close = True
    try:
        r = db.get(BridgeName, str(bgride))
        return (r.deskripsi or '') if r else None
    finally:
        if close:
            db.close()


# Hari Lahir
def get_hari_lahir(day: int, db: Optional[Session] = None) -> Optional[str]:
    if not day:
        return None
    close = False
    if db is None:
        db = get_session()
        close = True
    try:
        row = db.get(HariLahir, int(day))
        return (row.keterangan or '') if row else None
    finally:
        if close:
            db.close()


# Rejeki PQ combined
def get_rejeki_pq(pq: str, db: Optional[Session] = None) -> Optional[str]:
    if not pq:
        return None
    close = False
    if db is None:
        db = get_session()
        close = True
    try:
        r = db.query(Rejeki).filter(Rejeki.pq == pq).first()
        if r and r.deskripsi_pq:
            return r.deskripsi_pq
        return None
    finally:
        if close:
            db.close()


# Tantangan
def get_tantangan_by_kodes(kodes: List[int], db: Optional[Session] = None) -> List[dict]:
    if not kodes:
        return []
    close = False
    if db is None:
        db = get_session()
        close = True
    try:
        rows = (
            db.query(Tantangan)
            .filter(Tantangan.kode.in_(kodes))
            .all()
        )
        idx = {r.kode: r for r in rows}
        result = []
        for k in kodes:
            r = idx.get(k)
            if r:
                result.append({'kode': k, 'penjelasan': r.penjelasan or ''})
        return result
    finally:
        if close:
            db.close()


def get_tantangan_by_kode(kode: int, db: Optional[Session] = None) -> Optional[str]:
    close = False
    if db is None:
        db = get_session()
        close = True
    try:
        r = db.get(Tantangan, kode)
        return (r.penjelasan or '') if r else None
    finally:
        if close:
            db.close()


# Harani Nama
def get_harani(no: int, db: Optional[Session] = None) -> Optional[dict]:
    close = False
    if db is None:
        db = get_session()
        close = True
    try:
        r = db.get(HaraniNama, no)
        if not r:
            return None
        return {
            'no': r.no,
            'deskripsi': r.deskripsi or '',
            'kekuatan': r.kekuatan or '',
            'kelemahan': r.kelemahan or '',
            'makna_energi': r.makna_energi or '',
        }
    finally:
        if close:
            db.close()


# Karma
def get_karma(no: int, db: Optional[Session] = None) -> Optional[dict]:
    close = False
    if db is None:
        db = get_session()
        close = True
    try:
        r = db.get(Karma, no)
        if not r:
            return None
        return {
            'no': r.no,
            'judul': r.judul or '',
            'makna': r.makna or '',
            'pelajaran': r.pelajaran or '',
            'saran': r.saran or '',
        }
    finally:
        if close:
            db.close()


# Rejeki
def get_rejeki(no: int, db: Optional[Session] = None) -> Optional[dict]:
    close = False
    if db is None:
        db = get_session()
        close = True
    try:
        r = db.get(Rejeki, no)
        if not r:
            return None
        return {
            'no': r.no,
            'deskripsi': r.deskripsi or '',
            'kekuatan': r.kekuatan or '',
            'kelemahan': r.kelemahan or '',
            'saran': r.saran or '',
            'pq': r.pq or '',
            'deskripsi_pq': r.deskripsi_pq or '',
        }
    finally:
        if close:
            db.close()


# Lintang Bali
def get_lintang(hari: str, pasaran: str, db: Optional[Session] = None) -> Optional[dict]:
    """Get lintang description by hari and pasaran."""
    close = False
    if db is None:
        db = get_session()
        close = True
    try:
        r = (
            db.query(LintangBali)
            .filter(LintangBali.hari == hari, LintangBali.pasaran == pasaran)
            .first()
        )
        if not r:
            return None
        traits = []
        if (r.watak1 or r.arti1):
            traits.append({'watak': r.watak1 or '', 'arti': r.arti1 or ''})
        if (r.watak2 or r.arti2):
            traits.append({'watak': r.watak2 or '', 'arti': r.arti2 or ''})
        return {
            'lintang': r.lintang or '',
            'deskripsi': r.deskripsi or '',
            'traits': traits,
        }
    finally:
        if close:
            db.close()


# Desk Wewaran
def get_wewaran_entry(kategori: str, nilai: int, db: Optional[Session] = None) -> Optional[dict]:
    close = False
    if db is None:
        db = get_session()
        close = True
    try:
        r = (
            db.query(DeskWewaran)
            .filter(DeskWewaran.kategori == kategori, DeskWewaran.nilai == nilai)
            .first()
        )
        if not r:
            return None
        return {'nama': r.nama or '', 'deskripsi': r.deskripsi or ''}
    finally:
        if close:
            db.close()


# Wuku Awal
def get_wuku_awal_map(db: Optional[Session] = None) -> Dict[int, dict]:
    close = False
    if db is None:
        db = get_session()
        close = True
    try:
        rows = db.query(WukuAwal).all()
        return {r.tahun: {'no_wuku': r.no_wuku, 'wuku_awal': r.wuku_awal or ''} for r in rows}
    finally:
        if close:
            db.close()


# Wuku Names
def get_wuku_names_db(db: Optional[Session] = None) -> List[str]:
    close = False
    if db is None:
        db = get_session()
        close = True
    try:
        rows = db.query(WukuName).order_by(WukuName.no.asc()).all()
        return [r.nama for r in rows] if rows else []
    finally:
        if close:
            db.close()


# Weton Arti
def get_weton_generic_desc(kategori: str, nama: str, db: Optional[Session] = None) -> Optional[str]:
    if not kategori or not nama:
        return None
    close = False
    if db is None:
        db = get_session()
        close = True
    try:
        r = (
            db.query(WetonArti)
            .filter(WetonArti.kategori == kategori, WetonArti.nama == nama)
            .first()
        )
        return (r.deskripsi or '') if r else None
    finally:
        if close:
            db.close()


def get_weton_pair_desc(hari: str, pasaran: str, db: Optional[Session] = None) -> Tuple[str, str]:
    if not hari or not pasaran:
        return ('', '')
    close = False
    if db is None:
        db = get_session()
        close = True
    try:
        r = (
            db.query(WetonArtiPair)
            .filter(WetonArtiPair.hari == hari, WetonArtiPair.pasaran == pasaran)
            .first()
        )
        if not r:
            return ('', '')
        return (r.ket_hari or '', r.ket_pasaran or '')
    finally:
        if close:
            db.close()


# Tenung
def get_tenung_deskripsi(no: int, db: Optional[Session] = None) -> Optional[str]:
    close = False
    if db is None:
        db = get_session()
        close = True
    try:
        r = db.get(TenungNama, no)
        return (r.deskripsi or '') if r else None
    finally:
        if close:
            db.close()


# Panggilan
def get_panggilan(no: int, db: Optional[Session] = None) -> Optional[dict]:
    close = False
    if db is None:
        db = get_session()
        close = True
    try:
        r = db.get(Panggilan, no)
        if not r:
            return None
        return {'no': r.no, 'deskripsi': r.deskripsi or ''}
    finally:
        if close:
            db.close()


# Tenung Karma
def get_tenung_karma(karma_id: str, db: Optional[Session] = None) -> Optional[dict]:
    """Fetch Tenung Karma details by N-D-L combination.
    
    Args:
        karma_id: Combination string like "7-2-3"
    
    Returns:
        Dict with id, arti, deskripsi or None if not found
    """
    if not karma_id:
        return None
    close = False
    if db is None:
        db = get_session()
        close = True
    try:
        r = db.get(TenungKarma, karma_id)
        if not r:
            return None
        return {
            'id': r.id,
            'arti': r.arti or '',
            'deskripsi': r.deskripsi or ''
        }
    finally:
        if close:
            db.close()


# Papan Pythagoras
def get_papan_pythagoras_desc(desc_key: str, db: Optional[Session] = None) -> str:
    """Get description for Papan Pythagoras position and count."""
    close = False
    if db is None:
        db = get_session()
        close = True
    
    try:
        r = db.query(PapanPythagoras).filter(PapanPythagoras.id == desc_key).first()
        if r:
            return r.deskripsi or ''
        return f'Deskripsi untuk {desc_key} belum tersedia'
    except Exception as e:
        print(f"Error getting papan pythagoras description: {e}")
        return f'Deskripsi untuk {desc_key} belum tersedia'
    finally:
        if close:
            db.close()


# Angka Terisolasi
def get_angka_terisolasi_desc(angka: int, db: Optional[Session] = None) -> str:
    """Get description for isolated number."""
    close = False
    if db is None:
        db = get_session()
        close = True
    
    try:
        r = db.query(AngkaTerisolasi).filter(AngkaTerisolasi.angka == angka).first()
        if r:
            return r.deskripsi or ''
        return f'Deskripsi untuk angka terisolasi {angka} belum tersedia'
    except Exception as e:
        print(f"Error getting angka terisolasi description: {e}")
        return f'Deskripsi untuk angka terisolasi {angka} belum tersedia'
    finally:
        if close:
            db.close()


# Angka Berderet
def get_angka_berderet_desc(pattern_id: str, status: str, db: Optional[Session] = None) -> str:
    """Get description for sequential number pattern."""
    close = False
    if db is None:
        db = get_session()
        close = True
    
    try:
        # Create lookup key combining pattern and status
        lookup_key = f"{pattern_id}_{status}"
        r = db.query(AngkaBerderet).filter(AngkaBerderet.id == lookup_key).first()
        if r:
            return r.deskripsi or ''
        return f'Deskripsi untuk pola {pattern_id} ({status}) belum tersedia'
    except Exception as e:
        print(f"Error getting angka berderet description: {e}")
        return f'Deskripsi untuk pola {pattern_id} ({status}) belum tersedia'
    finally:
        if close:
            db.close()


# Chaldean
def get_chaldean_desc(number: int, db: Optional[Session] = None) -> str:
    """Get description for Chaldean number (1-9)."""
    close = False
    if db is None:
        db = get_session()
        close = True
    
    try:
        r = db.query(Chaldean).filter(Chaldean.id == number).first()
        if r:
            return r.deskripsi or ''
        return f'Deskripsi untuk angka Chaldean {number} belum tersedia'
    except Exception as e:
        print(f"Error getting chaldean description: {e}")
        return f'Deskripsi untuk angka Chaldean {number} belum tersedia'
    finally:
        if close:
            db.close()
