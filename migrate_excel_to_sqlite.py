from __future__ import annotations
import os
import sys
import json
import pandas as pd
from sqlalchemy.orm import Session
from datetime import date, timedelta

from db import (
    init_db,
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
)
from sqlalchemy import text

BASE_DIR = os.path.dirname(__file__)


def _norm_cols(df: pd.DataFrame) -> dict:
    return {str(c).strip().lower(): c for c in df.columns}


def load_life_path(db: Session):
    path = os.path.join(BASE_DIR, 'life_path.xlsx')
    if not os.path.exists(path):
        return
    df = pd.read_excel(path)
    cols = _norm_cols(df)
    col_no = cols.get('no')
    col_desc = cols.get('deskripsi')
    col_detail = cols.get('detail')
    col_kekuatan = cols.get('kekuatan')
    col_tantangan = cols.get('tantangan')
    col_penjelasan = (
        cols.get('penjelasan') or cols.get('penjelasa') or cols.get('penjelasan (html)') or cols.get('penjelasan_html') or cols.get('penjelasanhtml')
    )
    for _, r in df.iterrows():
        try:
            no = int(r.get(col_no)) if col_no is not None else None
        except Exception:
            continue
        if not no:
            continue
        row = db.get(LifePath, no) or LifePath(no=no)
        row.deskripsi = str(r.get(col_desc) or '').strip()
        row.detail = str(r.get(col_detail) or '').strip()
        row.kekuatan = str(r.get(col_kekuatan) or '').strip()
        row.tantangan = str(r.get(col_tantangan) or '').strip()
        row.penjelasan_html = str(r.get(col_penjelasan) or '').strip()
        db.merge(row)
    db.commit()


def load_panggilan(db: Session):
    path = os.path.join(BASE_DIR, 'panggilan.xlsx')
    if not os.path.exists(path):
        return
    df = pd.read_excel(path)
    cols = _norm_cols(df)
    col_no = cols.get('no') or cols.get('angka') or cols.get('kode') or cols.get('panggilan')
    # Support both 'deskripsi' and common misspelling 'deskrips'
    col_desc = cols.get('deskripsi') or cols.get('deskrips') or cols.get('penjelasan') or cols.get('arti') or cols.get('meaning')
    if not col_no or not col_desc:
        return
    for _, r in df.iterrows():
        try:
            no = int(r.get(col_no)) if r.get(col_no) is not None else None
        except Exception:
            no = None
        if not no:
            continue
        row = db.get(Panggilan, no) or Panggilan(no=no)
        row.deskripsi = str(r.get(col_desc) or '').strip()
        db.merge(row)
    db.commit()


def load_wuku_names(db: Session):
    # Try multiple potential filenames
    candidates = [
        os.path.join(BASE_DIR, 'wuku_names.xlsx'),
        os.path.join(BASE_DIR, 'wuku_name.xlsx'),
        os.path.join(BASE_DIR, 'wuku_name.xls'),
    ]
    path = next((p for p in candidates if os.path.exists(p)), None)
    if not path:
        return
    df = pd.read_excel(path)
    cols = _norm_cols(df)
    # Column detection
    col_no = cols.get('no') or cols.get('index') or cols.get('kode')
    col_nama = cols.get('nama') or cols.get('wuku') or cols.get('wuku_awal') or cols.get('name')
    col_desc = cols.get('deskripsi') or cols.get('keterangan') or cols.get('arti') or cols.get('penjelasan') or cols.get('description')

    seq = 0
    for _, r in df.iterrows():
        # Determine number: from column if present, else sequential by row order
        no = None
        if col_no is not None:
            try:
                no = int(r.get(col_no)) if r.get(col_no) is not None else None
            except Exception:
                no = None
        if not no:
            seq += 1
            no = seq
        nama = str(r.get(col_nama) or '').strip() if col_nama is not None else ''
        if not nama:
            continue
        desc = str(r.get(col_desc) or '').strip() if col_desc is not None else ''
        # Fetch or create row, with fallback to add missing column at runtime
        try:
            row = db.get(WukuName, no) or WukuName(no=no)
        except Exception as e:
            if 'no such column: wuku_name.deskripsi' in str(e):
                try:
                    db.execute(text("ALTER TABLE wuku_name ADD COLUMN deskripsi TEXT DEFAULT ''"))
                    db.commit()
                except Exception:
                    pass
                # Retry fetch after altering
                row = db.get(WukuName, no) or WukuName(no=no)
            else:
                raise
        row.nama = nama
        # Store description if available
        if hasattr(row, 'deskripsi'):
            row.deskripsi = desc
        db.merge(row)
    db.commit()


def load_weton_arti(db: Session):
    path = os.path.join(BASE_DIR, 'weton_arti.xlsx')
    if not os.path.exists(path):
        return
    df = pd.read_excel(path)
    cols = _norm_cols(df)
    # Generic category/name mapping
    cat_col = cols.get('kategori') or cols.get('category') or cols.get('jenis') or cols.get('tipe')
    name_col = cols.get('nama') or cols.get('value') or cols.get('label')
    desc_col = cols.get('deskripsi') or cols.get('keterangan') or cols.get('makna') or cols.get('arti') or cols.get('meaning')
    if cat_col and name_col and desc_col:
        for _, r in df.iterrows():
            kategori = str(r.get(cat_col) or '').strip()
            nama = str(r.get(name_col) or '').strip()
            deskripsi = str(r.get(desc_col) or '').strip()
            if not kategori or not nama or not deskripsi:
                continue
            ex = (
                db.query(WetonArti)
                .filter(WetonArti.kategori == kategori, WetonArti.nama == nama)
                .first()
            )
            if not ex:
                ex = WetonArti(kategori=kategori, nama=nama)
            ex.deskripsi = deskripsi
            db.merge(ex)
        db.commit()

    # Combined Hari+Pasaran mapping (if available)
    combine_col = cols.get('combine') or cols.get('kombinasi') or cols.get('hari_pasaran')
    hari_col = cols.get('hari')
    pas_col = cols.get('pasaran')
    ket_hari_col = cols.get('ket_hari') or cols.get('keterangan_hari') or cols.get('arti_hari') or cols.get('makna_hari')
    ket_pas_col = cols.get('ket_pasaran') or cols.get('keterangan_pasaran') or cols.get('arti_pasaran') or cols.get('makna_pasaran')
    if (combine_col and (ket_hari_col or ket_pas_col)) or (hari_col and pas_col and (ket_hari_col or ket_pas_col)):
        for _, r in df.iterrows():
            # Determine keys
            hari = ''
            pas = ''
            if combine_col:
                comb = str(r.get(combine_col) or '').strip()
                if comb:
                    parts = comb.split()
                    if len(parts) >= 2:
                        hari, pas = parts[0].strip(), parts[1].strip()
            if (not hari or not pas) and hari_col and pas_col:
                hari = str(r.get(hari_col) or '').strip()
                pas = str(r.get(pas_col) or '').strip()
            if not hari or not pas:
                continue
            ket_h = str(r.get(ket_hari_col) or '').strip() if ket_hari_col else ''
            ket_p = str(r.get(ket_pas_col) or '').strip() if ket_pas_col else ''
            if not ket_h and not ket_p:
                continue
            ex = (
                db.query(WetonArtiPair)
                .filter(WetonArtiPair.hari == hari, WetonArtiPair.pasaran == pas)
                .first()
            )
            if not ex:
                ex = WetonArtiPair(hari=hari, pasaran=pas)
            ex.ket_hari = ket_h
            ex.ket_pasaran = ket_p
            db.merge(ex)
        db.commit()


def load_hari_lahir(db: Session):
    path = os.path.join(BASE_DIR, 'hari_lahir.xlsx')
    if not os.path.exists(path):
        return
    df = pd.read_excel(path)
    cols = _norm_cols(df)
    col_day = cols.get('hari_lahir') or cols.get('hari') or cols.get('day')
    col_ket = cols.get('keterangan') or cols.get('deskripsi') or cols.get('penjelasan')
    if not col_day or not col_ket:
        return
    # Coerce day column to integers 1..31 robustly
    try:
        coerced = pd.to_numeric(df[col_day], errors='coerce')
    except Exception:
        coerced = None
    if coerced is None or getattr(coerced, 'isna', lambda: True)().all():
        try:
            df['_day'] = df[col_day].astype(str).str.extract(r'(\d{1,2})', expand=False).astype('Int64')
        except Exception:
            df['_day'] = pd.Series([None] * len(df), dtype='Int64')
    else:
        try:
            df['_day'] = coerced.astype('Int64')
        except Exception:
            df['_day'] = coerced
    for _, r in df.iterrows():
        day = r.get('_day')
        if pd.isna(day) or day is None:
            continue
        day = int(day)
        if day < 1 or day > 31:
            continue
        row = db.get(HariLahir, day) or HariLahir(hari=day)
        row.keterangan = str(r.get(col_ket) or '').strip()
        db.merge(row)
    db.commit()

# --- WukuAwal sync with fallback ---

def _first_sunday(year: int) -> date:
    d = date(year, 1, 1)
    # Python weekday: Mon=0..Sun=6; compute days to next Sunday including same day
    days_since_sun = (d.weekday() + 1) % 7
    return d + timedelta(days=(0 if days_since_sun == 0 else (7 - days_since_sun)))


def _wuku_names() -> list:
    return [
        'Sinta','Landep','Ukir','Kurantil','Tolu','Gumbreg','Wariga','Warigadian','Julungwangi','Sungsang',
        'Dunggulan','Kuningan','Langkir','Medangsia','Pujut','Pahang','Krulut','Merakih','Tambir','Medangkungan',
        'Matal','Uye','Menail','Perangbakat','Bala','Ugu','Wayang','Kelawu','Dukut','Watugunung'
    ]


def sync_wuku_awal_with_fallback(db: Session, start_year: int = 1600, end_year: int = 2200, overwrite: bool = False) -> dict:
    """Synchronize WukuAwal table across a range of years using fallback logic.

    Strategy:
    - Use existing DB rows as anchors when present (prefer numeric no_wuku 1..30, else map name to index).
    - Ensure epoch 1633 exists as Sinta (index 0). If missing, create it.
    - Propagate forward and backward from nearest known anchors using week offsets between first Sundays.
    - Upsert rows for missing years. By default, do not overwrite existing valid rows unless overwrite=True.

    Returns a summary dict with counts.
    """
    if start_year > end_year:
        start_year, end_year = end_year, start_year

    names = _wuku_names()

    # Load existing rows into an index map: year -> idx (0..29)
    existing = {r.tahun: r for r in db.query(WukuAwal).all()}
    idx_map: dict[int, int] = {}

    def row_to_idx(row: WukuAwal) -> int | None:
        if row is None:
            return None
        try:
            if row.no_wuku is not None and 1 <= int(row.no_wuku) <= 30:
                return (int(row.no_wuku) - 1) % 30
        except Exception:
            pass
        name = (row.wuku_awal or '').strip()
        if name:
            try:
                return names.index(name.capitalize())
            except ValueError:
                return None
        return None

    for y, r in existing.items():
        idx = row_to_idx(r)
        if idx is not None:
            idx_map[y] = idx

    # Ensure epoch 1633 -> Sinta
    if 1633 not in idx_map:
        idx_map[1633] = 0
        if 1633 not in existing:
            db.merge(WukuAwal(tahun=1633, no_wuku=1, wuku_awal='Sinta'))
        else:
            r = existing[1633]
            if overwrite or not (r.no_wuku and 1 <= int(r.no_wuku) <= 30) or not (r.wuku_awal or '').strip():
                r.no_wuku = 1
                r.wuku_awal = 'Sinta'
                db.merge(r)
        db.commit()

    # Precompute first Sundays for the whole range and a buffer year
    first_sun = {y: _first_sunday(y) for y in range(start_year - 1, end_year + 2)}

    anchors = sorted(idx_map.keys())
    if not anchors:
        anchors = [1633]
        idx_map[1633] = 0

    # Forward fill
    min_anchor = min(anchors)
    cur_idx = idx_map[min_anchor]
    prev_year = min_anchor
    for y in range(min(min_anchor, start_year), end_year + 1):
        if y in idx_map:
            cur_idx = idx_map[y]
            prev_year = y
            continue
        weeks = max(0, (first_sun[y] - first_sun[prev_year]).days // 7)
        idx_map[y] = (cur_idx + (weeks % 30)) % 30
        cur_idx = idx_map[y]
        prev_year = y

    # Backward fill
    max_anchor = max(anchors)
    cur_idx = idx_map[max_anchor]
    next_year = max_anchor
    for y in range(max(max_anchor, end_year), start_year - 1, -1):
        if y in idx_map:
            cur_idx = idx_map[y]
            next_year = y
            continue
        weeks = max(0, (first_sun[next_year] - first_sun[y]).days // 7)
        idx_map[y] = (cur_idx - (weeks % 30)) % 30
        cur_idx = idx_map[y]
        next_year = y

    created = 0
    updated = 0
    skipped = 0

    # Upsert into DB
    for y in range(start_year, end_year + 1):
        idx = idx_map.get(y)
        if idx is None:
            continue
        name = names[idx]
        no = idx + 1
        row = existing.get(y)
        if not row:
            # Use merge to upsert safely in case the year was inserted concurrently
            db.merge(WukuAwal(tahun=y, no_wuku=no, wuku_awal=name))
            created += 1
            continue
        valid_no = (row.no_wuku is not None and 1 <= int(row.no_wuku) <= 30)
        valid_name = bool((row.wuku_awal or '').strip())
        if overwrite or not (valid_no and valid_name):
            row.no_wuku = no
            row.wuku_awal = name
            db.merge(row)
            updated += 1
        else:
            skipped += 1

    db.commit()
    return {'created': created, 'updated': updated, 'skipped': skipped, 'range': (start_year, end_year)}


def load_tantangan(db: Session):
    path = os.path.join(BASE_DIR, 'tantangan.xlsx')
    if not os.path.exists(path):
        return
    df = pd.read_excel(path)
    cols = _norm_cols(df)
    col_kode = cols.get('kode') or cols.get('no')
    col_penj = cols.get('penjelasan') or cols.get('tantangan') or cols.get('deskripsi')
    for _, r in df.iterrows():
        try:
            kode = int(r.get(col_kode)) if col_kode is not None else None
        except Exception:
            continue
        if kode is None:
            continue
        row = db.get(Tantangan, kode) or Tantangan(kode=kode)
        row.penjelasan = str(r.get(col_penj) or '').strip()
        db.merge(row)
    db.commit()


def load_harani(db: Session):
    path = os.path.join(BASE_DIR, 'harani_nama_numerology.xlsx')
    if not os.path.exists(path):
        return
    df = pd.read_excel(path)
    cols = _norm_cols(df)
    col_no = cols.get('no')
    for _, r in df.iterrows():
        try:
            no = int(r.get(col_no)) if col_no is not None else None
        except Exception:
            continue
        if not no:
            continue
        row = db.get(HaraniNama, no) or HaraniNama(no=no)
        row.deskripsi = str(r.get(cols.get('deskripsi') or '') or '').strip()
        row.kekuatan = str(r.get(cols.get('kekuatan') or '') or '').strip()
        row.kelemahan = str(r.get(cols.get('kelemahan') or '') or '').strip()
        row.makna_energi = str(r.get(cols.get('makna energi') or cols.get('makna_energi') or '') or '').strip()
        db.merge(row)
    db.commit()


def load_karma(db: Session):
    path = os.path.join(BASE_DIR, 'karma.xlsx')
    if not os.path.exists(path):
        return
    df = pd.read_excel(path)
    cols = _norm_cols(df)
    col_no = cols.get('no') or cols.get('kode') or cols.get('angka') or cols.get('karma')
    for _, r in df.iterrows():
        try:
            no = int(r.get(col_no)) if col_no is not None else None
        except Exception:
            continue
        if not no:
            continue
        row = db.get(Karma, no) or Karma(no=no)
        row.judul = str(r.get(cols.get('judul') or cols.get('title') or cols.get('deskripsi_singkat') or cols.get('deskripsi') or '') or '').strip()
        row.makna = str(r.get(cols.get('arti') or cols.get('makna') or cols.get('meaning') or cols.get('deskripsi') or '') or '').strip()
        row.pelajaran = str(r.get(cols.get('pelajaran') or cols.get('lesson') or '') or '').strip()
        row.saran = str(r.get(cols.get('saran') or cols.get('advice') or '') or '').strip()
        db.merge(row)
    db.commit()


def load_rejeki(db: Session):
    path = os.path.join(BASE_DIR, 'rejeki.xlsx')
    if not os.path.exists(path):
        return
    df = pd.read_excel(path)
    cols = _norm_cols(df)
    col_no = cols.get('no') or cols.get('kode') or cols.get('r') or cols.get('rejeki')
    for _, r in df.iterrows():
        try:
            no = int(r.get(col_no)) if col_no is not None else None
        except Exception:
            continue
        if not no:
            continue
        row = db.get(Rejeki, no) or Rejeki(no=no)
        row.deskripsi = str(r.get(cols.get('deskripsi') or cols.get('penjelasan') or cols.get('arti') or '') or '').strip()
        row.kekuatan = str(r.get(cols.get('kekuatan') or '') or '').strip()
        row.kelemahan = str(r.get(cols.get('kelemahan') or '') or '').strip()
        row.saran = str(r.get(cols.get('saran') or '') or '').strip()
        row.pq = str(r.get(cols.get('pq') or cols.get('kombinasi') or cols.get('p_q') or cols.get('p+q') or '') or '').strip()
        row.deskripsi_pq = str(r.get(cols.get('deskripsi_pq') or cols.get('penjelasan_pq') or '') or '').strip()
        db.merge(row)
    db.commit()


def load_arah_sukses(db: Session):
    path = os.path.join(BASE_DIR, 'arah_sukses.xlsx')
    if not os.path.exists(path):
        return
    df = pd.read_excel(path)
    cols = _norm_cols(df)
    col_arah = cols.get('arah')
    col_desc = cols.get('deskripsi')
    for _, r in df.iterrows():
        arah = str(r.get(col_arah) or '').strip()
        if not arah:
            continue
        row = db.query(ArahSukses).filter(ArahSukses.arah == arah).first() or ArahSukses(arah=arah)
        row.deskripsi = str(r.get(col_desc) or '').strip()
        db.merge(row)
    db.commit()


def load_lintang_bali(db: Session):
    path = os.path.join(BASE_DIR, 'lintang_bali.xlsx')
    if not os.path.exists(path):
        return
    df = pd.read_excel(path)
    cols = _norm_cols(df)
    col_hari = cols.get('hari') or cols.get('day')
    col_pasaran = cols.get('pasaran') or cols.get('market')
    col_lintang = cols.get('lintang') or cols.get('name')
    col_desc = cols.get('deskripsi') or cols.get('arti') or cols.get('penjelasan')
    col_w1 = cols.get('watak1') or cols.get('watak 1')
    col_a1 = cols.get('arti1') or cols.get('arti 1')
    col_w2 = cols.get('watak2') or cols.get('watak 2')
    col_a2 = cols.get('arti2') or cols.get('arti 2')
    for _, r in df.iterrows():
        raw_hari = r.get(col_hari) if col_hari is not None else None
        raw_pas = r.get(col_pasaran) if col_pasaran is not None else None
        # Guard against NaN and None
        if pd.isna(raw_hari) or pd.isna(raw_pas):
            continue
        hari = str(raw_hari).strip()
        pasaran = str(raw_pas).strip()
        if not hari or not pasaran or hari.lower() == 'nan' or pasaran.lower() == 'nan':
            continue
        row = db.query(LintangBali).filter(LintangBali.hari == hari, LintangBali.pasaran == pasaran).first()
        if not row:
            row = LintangBali(hari=hari, pasaran=pasaran)
        # Normalize values with NaN handling
        def norm(v):
            if pd.isna(v) or v is None:
                return ''
            s = str(v).strip()
            return '' if s.lower() == 'nan' else s
        row.lintang = norm(r.get(col_lintang))
        row.deskripsi = norm(r.get(col_desc))
        row.watak1 = norm(r.get(col_w1))
        row.arti1 = norm(r.get(col_a1))
        row.watak2 = norm(r.get(col_w2))
        row.arti2 = norm(r.get(col_a2))
        db.merge(row)
    db.commit()


def load_desk_wewaran(db: Session):
    path = os.path.join(BASE_DIR, 'desk_wewaran.xlsx')
    if not os.path.exists(path):
        return
    df = pd.read_excel(path)
    cols = _norm_cols(df)
    col_kat = cols.get('kategori')
    col_nilai = cols.get('nilai')
    col_nama = cols.get('nama')
    col_desc = cols.get('deskripsi')
    for _, r in df.iterrows():
        kategori = str(r.get(col_kat) or '').strip()
        try:
            nilai = int(r.get(col_nilai)) if col_nilai is not None else None
        except Exception:
            nilai = None
        if not kategori or nilai is None:
            continue
        row = (
            db.query(DeskWewaran)
            .filter(DeskWewaran.kategori == kategori, DeskWewaran.nilai == nilai)
            .first()
        ) or DeskWewaran(kategori=kategori, nilai=nilai)
        row.nama = str(r.get(col_nama) or '').strip()
        row.deskripsi = str(r.get(col_desc) or '').strip()
        db.merge(row)
    db.commit()


def load_wuku_awal(db: Session):
    path = os.path.join(BASE_DIR, 'wuku_awal.xlsx')
    if not os.path.exists(path):
        return
    df = pd.read_excel(path)
    cols = _norm_cols(df)
    col_year = cols.get('tahun') or cols.get('year')
    col_no = cols.get('no_wuku') or cols.get('nomer_wuku') or cols.get('no') or cols.get('index')
    col_name = cols.get('wuku_awal') or cols.get('nama_wuku') or cols.get('wuku') or cols.get('name')
    for _, r in df.iterrows():
        try:
            year = int(r.get(col_year)) if col_year is not None else None
        except Exception:
            continue
        if year is None:
            continue
        row = db.get(WukuAwal, year) or WukuAwal(tahun=year)
        try:
            row.no_wuku = int(r.get(col_no)) if col_no is not None else None
        except Exception:
            row.no_wuku = None
        row.wuku_awal = str(r.get(col_name) or '').strip()
        db.merge(row)
    db.commit()


def load_tenung_nama(db: Session):
    path = os.path.join(BASE_DIR, 'tenung_nama.xlsx')
    if not os.path.exists(path):
        return
    df = pd.read_excel(path)
    cols = _norm_cols(df)
    col_no = cols.get('no') or cols.get('angka') or cols.get('kode') or cols.get('tenung')
    col_desc = cols.get('deskripsi') or cols.get('penjelasan') or cols.get('arti') or cols.get('meaning') or cols.get('makna')
    for _, r in df.iterrows():
        try:
            no = int(r.get(col_no)) if col_no is not None else None
        except Exception:
            continue
        if not no:
            continue
        row = db.get(TenungNama, no) or TenungNama(no=no)
        row.deskripsi = str(r.get(col_desc) or '').strip()
        db.merge(row)
    db.commit()


def main():
    init_db()
    db = SessionLocal()
    try:
        load_life_path(db)
        load_tantangan(db)
        load_harani(db)
        load_karma(db)
        load_rejeki(db)
        load_arah_sukses(db)
        load_lintang_bali(db)
        load_desk_wewaran(db)
        load_hari_lahir(db)
        load_wuku_names(db)
        load_weton_arti(db)
        load_wuku_awal(db)
        load_tenung_nama(db)
        load_panggilan(db)
        # Ensure WukuAwal table synchronized with fallback
        try:
            summary = sync_wuku_awal_with_fallback(db, start_year=1600, end_year=2200, overwrite=False)
            print(f"WukuAwal sync summary: {summary}")
        except Exception as e:
            print(f"WukuAwal sync failed: {e}")
        print('Migration completed.')
    finally:
        db.close()


if __name__ == '__main__':
    main()
