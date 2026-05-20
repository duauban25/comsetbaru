import os
from dotenv import load_dotenv
load_dotenv()
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Length, ValidationError, Regexp
from flask_wtf.csrf import CSRFProtect, CSRFError, generate_csrf
from flask_cors import CORS
from datetime import datetime, timedelta

import urllib.parse
import pandas as pd
import re
import sys
import traceback
import logging
import json
from db import init_db, SessionLocal, Upload, UploadRow, User
from db_access import (
    get_life_path, get_tantangan_by_kode, get_hari_lahir, get_wuku_names_db,
    get_weton_pair_desc, get_weton_generic_desc, get_karmic_debt, 
    get_heart_desire, get_personality, get_tenung_karma, get_arah_deskripsi,
    get_harani, get_karma, get_rejeki, get_lintang, get_wewaran_entry,
    get_tenung_deskripsi, get_panggilan, get_bridge_details, get_bridge_name,
    get_chaldean_desc, get_soul_urge, get_outer_expression
)

# Simple email sender with console fallback
def send_email(to_email: str, subject: str, body: str) -> None:
    try:
        host = os.environ.get('SMTP_HOST')
        port = int(os.environ.get('SMTP_PORT', '0') or '0')
        user = os.environ.get('SMTP_USER')
        password = os.environ.get('SMTP_PASS')
        mail_from = os.environ.get('MAIL_FROM') or 'no-reply@example.com'
        if not host or not port or not user or not password:
            print(f"[EMAIL-FAKE] To: {to_email}\nSubject: {subject}\n{body}")
            return
        import smtplib
        from email.mime.text import MIMEText
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = mail_from
        msg['To'] = to_email
        with smtplib.SMTP(host, port) as server:
            server.starttls()
            server.login(user, password)
            server.sendmail(mail_from, [to_email], msg.as_string())
    except Exception as _e:
        print(f"[EMAIL-FAKE][ERR] To: {to_email} | {subject} | {body} | err={_e}")
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from numerology_utils import (
    life_path_calculation,
    get_life_path_details,
    harani_calculation,
    karma_number_from_missing_digits,
    weton_calculation,
    get_weton_meaning,
    rejeki_pythagoras_from_birthdate,
    chaldean_calculation,
    compute_challenges,
    calculate_ekawara,
    calculate_dwiwara,
    calculate_triwara,
    calculate_caturwara,
    calculate_sadwara,
    calculate_astawara,
    calculate_sangawara,
    calculate_dasawara,
    get_wuku_names,
    heart_desire_calculation,
    personality_calculation,
)

# Initialize CSRF protection instance
csrf = CSRFProtect()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Konfigurasi aplikasi
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or 'your-secure-secret-key-here'  # Gunakan environment variable untuk production

# Initialize CSRF protection
csrf.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    try:
        db = SessionLocal()
        try:
            return db.query(User).get(int(user_id))
        finally:
            db.close()
    except Exception:
        return None

# Initialize SQLite database (tables will be created if not present)
try:
    init_db()
except Exception as _db_init_err:
    # Do not crash the app; just log the error
    print(f"[DB] init_db failed: {_db_init_err}")

# Add urlencode/urldecode filters to Jinja2
app.jinja_env.filters['urlencode'] = lambda s: urllib.parse.quote_plus(str(s)) if s else ''
app.jinja_env.filters['urldecode'] = lambda s: urllib.parse.unquote_plus(str(s)) if s else ''

# Global inline formatter for highlighting markers from Excel
# [[text]] => <mark>text</mark>, **text** => <strong>, //text// => <em>, __text__ => <u>
def _format_inline(text: str) -> str:
    try:
        s = '' if text is None else str(text)
        s = re.sub(r"\[\[([^\]]+)\]\]", r"<mark>\1</mark>", s)      # [[...]]
        s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)      # **...**
        s = re.sub(r"//(.+?)//", r"<em>\1</em>", s)                      # //...//
        s = re.sub(r"__(.+?)__", r"<u>\1</u>", s)                        # __...__
        return s
    except Exception:
        return str(text) if text is not None else ''

app.jinja_env.filters['fmt'] = _format_inline

# Expose canonical Wuku names to all templates for consistent dropdowns
@app.context_processor
def inject_globals():
    """Inject global constants into templates. Prefer DB for Wuku names, fallback to utils."""
    try:
        names = get_wuku_names_db()
        if names:
            return {'WUKU_NAMES': names}
    except Exception:
        pass
    # Fallback to Python helper as a safe default
    try:
        return {'WUKU_NAMES': get_wuku_names()}
    except Exception:
        return {'WUKU_NAMES': []}

# Konfigurasi Session dan CSRF
app.config.update(
    # Session Configuration
    SESSION_COOKIE_SECURE=False,  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=3600,  # 1 hour
    SESSION_REFRESH_EACH_REQUEST=True,
    
    # CSRF Configuration
    WTF_CSRF_ENABLED=False,  # Set to True in production
    WTF_CSRF_SECRET_KEY=os.environ.get('CSRF_SECRET_KEY') or 'another-secure-key-here',
    WTF_CSRF_TIME_LIMIT=3600,  # 1 hour token expiration
    WTF_CSRF_SSL_STRICT=False,  # Set to True in production with HTTPS
    WTF_CSRF_CHECK_DEFAULT=False,  # Disable CSRF by default for all views
    WTF_CSRF_HEADERS=['X-CSRFToken'],
    WTF_CSRF_METHODS=['POST', 'PUT', 'PATCH', 'DELETE']
)

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size
app.config['SESSION_TYPE'] = 'filesystem'
app.config['ALLOWED_EXTENSIONS'] = {'xlsx', 'xls'}
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Configure CORS with proper headers
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "supports_credentials": True,
        "allow_headers": ["Content-Type", "X-CSRFToken", "X-Requested-With"]
    }
})

# Handler untuk error CSRF
@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    app.logger.error(f'CSRF Error: {str(e)}')
    if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'status': 'error',
            'message': 'CSRF token error',
            'details': 'Session expired or invalid CSRF token. Please refresh the page and try again.'
        }), 400
    return render_template('error.html', error="CSRF Token Error"), 400

# Pastikan folder upload ada
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.after_request
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# ----------------------
# Helpers for numerology
# ----------------------
def _reduce_number(n: int) -> int:
    """Reduce number to 1-9 while preserving master numbers 11 and 22."""
    try:
        while n > 9 and n not in (11, 22):
            n = sum(int(d) for d in str(n))
        return int(n)
    except Exception:
        return 0

def _ensure_excel(filepath: str, records: list):
    """Create an Excel file with given records if it doesn't exist."""
    try:
        if not os.path.exists(filepath):
            df = pd.DataFrame.from_records(records)
            # Ensure column order
            cols = []
            # Handle different Excel file types
            if 'arah_sukses' in filepath:
                cols = ['No', 'Arah', 'Deskripsi']
            else:
                cols = [c for c in ['No', 'deskripsi', 'kekuatan', 'kelemahan', 'saran', 'arah'] if c in df.columns]
            
            # Only include columns that exist in the dataframe
            cols = [c for c in cols if c in df.columns]
            if cols:
                df = df[cols]
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
            
            df.to_excel(filepath, index=False, engine='openpyxl')
            print(f"Created/Updated Excel: {filepath}")
            return True
    except Exception as e:
        print(f"Error in _ensure_excel for {filepath}: {str(e)}")
    return False

def _default_karma_records():
    base = []
    for i in range(1, 10):
        base.append({
            'No': i,
            'deskripsi': f"Karma {i}: Pelajaran hidup terkait energi angka {i}.",
            'kekuatan': ";".join(["Kesadaran", "Pertumbuhan", "Introspeksi"]),
            'kelemahan': ";".join(["Kecemasan", "Keraguan", "Pola Lama"]),
            'saran': "Fokus pada perbaikan diri dan keseimbangan."
        })
    return base

def _default_rejeki_records():
    base = []
    for i in range(1, 10):
        base.append({
            'No': i,
            'deskripsi': f"Rejeki {i}: Pola rejeki selaras dengan angka {i}.",
            'kekuatan': ";".join(["Peluang", "Ketekunan", "Jaringan"]),
            'kelemahan': ";".join(["Borodana", "Kurang Fokus", "Emosional"]),
            'saran': "Kelola keuangan dan disiplin tujuan."
        })
    return base

def _default_arah_records():
    directions = {
        1: 'Timur', 2: 'Tenggara', 3: 'Selatan', 4: 'Barat Daya', 5: 'Barat',
        6: 'Barat Laut', 7: 'Utara', 8: 'Timur Laut', 9: 'Pusat'
    }
    return [{'No': k, 'Arah': v, 'Deskripsi': f'Deskripsi untuk arah {v}'} 
            for k, v in directions.items()]

def _default_panggilan_records():
    # Minimal placeholder rows for numbers 1..9
    rows = []
    for i in range(1, 10):
        rows.append({'No': i, 'deskrips': f'Contoh deskripsi untuk angka {i} (Nama Panggilan).'})
    return rows

def process_excel(filepath):
    """Process Excel file and return data as list of dictionaries"""
    try:
        # Baca file Excel
        df = pd.read_excel(filepath)
        # Konversi ke list of dictionaries
        data = df.to_dict('records')
        return data, None
    except Exception as e:
        return None, str(e)

def save_upload_to_db(filename: str, records: list) -> int:
    """Save uploaded Excel's rows into SQLite. Returns created upload_id.

    Each record is stored as JSON in `upload_rows` tied to an entry in `uploads`.
    """
    try:
        if not records:
            # create empty upload for tracking
            db = SessionLocal()
            try:
                up = Upload(filename=filename)
                db.add(up)
                db.commit()
                db.refresh(up)
                return up.id
            finally:
                db.close()
        db = SessionLocal()
        try:
            up = Upload(filename=filename)
            db.add(up)
            db.commit()
            db.refresh(up)
            # Bulk insert rows
            rows = []
            for idx, rec in enumerate(records):
                try:
                    row_json = json.dumps(rec, ensure_ascii=False)
                except Exception:
                    row_json = json.dumps({"_error": "unserializable", "raw": str(rec)})
                rows.append(UploadRow(upload_id=up.id, row_index=idx, row_json=row_json))
            if rows:
                db.bulk_save_objects(rows)
                db.commit()
            return up.id
        finally:
            db.close()
    except Exception as e:
        app.logger.error(f"Failed to save upload to DB: {e}")
        return 0

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_pwd = request.form.get('current_password', '')
        new_pwd = request.form.get('new_password', '')
        confirm_pwd = request.form.get('confirm_password', '')
        if not new_pwd or len(new_pwd) < 6:
            flash('Password baru minimal 6 karakter', 'error')
            return render_template('change_password.html')
        if new_pwd != confirm_pwd:
            flash('Konfirmasi password tidak cocok', 'error')
            return render_template('change_password.html')
        db = SessionLocal()
        try:
            u = db.query(User).get(int(current_user.id))
            if not u or not check_password_hash(u.password_hash, current_pwd):
                flash('Password saat ini salah', 'error')
                return render_template('change_password.html')
            u.password_hash = generate_password_hash(new_pwd)
            db.add(u)
            db.commit()
            flash('Password berhasil diubah', 'success')
            return redirect(url_for('profile'))
        finally:
            db.close()
    return render_template('change_password.html')

@app.route('/')
def home():
    # Root should point to input form
    return redirect(url_for('login'))

@app.route('/cards', methods=['GET', 'POST'])
@login_required
def show_cards():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        
        # Handle both old date format and new separate fields
        birth_date = request.form.get('birth_date', '').strip()
        
        # If birth_date is empty, try to construct from separate fields
        if not birth_date:
            birth_day = request.form.get('birth_day', '').strip()
            birth_month = request.form.get('birth_month', '').strip()
            birth_year = request.form.get('birth_year', '').strip()
            
            if birth_day and birth_month and birth_year:
                birth_date = f"{birth_year}-{birth_month}-{birth_day}"
        
        if not name or not birth_date:
            flash('Mohon isi semua field yang diperlukan', 'error')
            return redirect(url_for('home'))
            
        # Validate date format
        try:
            from datetime import datetime
            datetime.strptime(birth_date, '%Y-%m-%d')
        except ValueError:
            flash('Format tanggal lahir tidak valid', 'error')
            return redirect(url_for('home'))
            
        # Store the form data in the session
        session['form_data'] = {
            'name': name,
            'birth_date': birth_date
        }
        
        return render_template('calculation_options.html')
    # GET request: allow admin/platinum to override via query params
    if getattr(current_user, 'role', '') in ['admin', 'platinum']:
        q_name = request.args.get('name', '').strip()
        q_birth = request.args.get('birth_date', '').strip()
        if q_name and q_birth:
            try:
                datetime.strptime(q_birth, '%Y-%m-%d')
                session['form_data'] = {'name': q_name, 'birth_date': q_birth}
                session.modified = True
            except Exception:
                pass
    # Render with session data
    form_data = session.get('form_data', {})
    return render_template('calculation_options.html',
                           name=form_data.get('name', ''),
                           birth_date=form_data.get('birth_date', ''))

@app.route('/old', methods=['GET', 'POST'])
def old_home():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        birth_date = request.form.get('birth_date', '').strip()
        calculation_type = request.form.get('calculation_type', 'all')
        
        if not name or not birth_date:
            flash('Mohon isi semua field yang diperlukan', 'error')
            return redirect(url_for('old_home'))
            
        try:
            # Convert date format from YYYY-MM-DD to DD/MM/YYYY
            day, month, year = birth_date.split('-')
            formatted_date = f"{day}/{month}/{year}"
            
            result_data = {
                'name': name,
                'birth_date': birth_date,
                'formatted_date': formatted_date
            }
            
            # Store the calculation type in session
            session['calculation_type'] = calculation_type
            
            # Calculate based on the requested type
            if calculation_type in ['all', 'life_path']:
                life_path_info = life_path_calculation(birth_date)
                if not life_path_info:
                    flash('Format tanggal lahir tidak valid', 'error')
                    return redirect(url_for('home'))
                result_data.update(life_path_info)
            
            if calculation_type in ['all', 'name_number']:
                harani_info = harani_calculation(name)
                name_number = harani_info.get('number', 0)
                result_data['name_number'] = name_number
                
                # Get detailed name number information
                name_number_detail = get_name_number_detail(name_number)
                if name_number_detail:
                    result_data.update(name_number_detail)
            
            if calculation_type in ['all', 'weton']:
                weton = weton_calculation(birth_date)
                if not weton:
                    flash('Gagal menghitung weton', 'error')
                    return redirect(url_for('home'))
                result_data['weton'] = weton
            
            # Store results in session
            session['result_data'] = result_data
            
            # Redirect to the appropriate result page
            if calculation_type == 'all':
                return redirect(url_for('result'))
            else:
                return redirect(url_for('numerology_result', result_type=calculation_type))
                
        except ValueError as e:
            flash('Format tanggal tidak valid. Gunakan format YYYY-MM-DD', 'error')
            return redirect(url_for('home'))
        except Exception as e:
            flash(f'Terjadi kesalahan: {str(e)}', 'error')
            return redirect(url_for('home'))
            
    from datetime import datetime
    return render_template('index.html', now=datetime.now())

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.email == email).first()
        finally:
            db.close()
        if not user:
            flash('Email belum terdaftar. Silakan buat akun baru.', 'info')
            return redirect(url_for('register_request', email=email))
        if user and check_password_hash(user.password_hash, password) and user.is_active:
            login_user(user)
            # Load profile to session if available; else require profile completion
            if getattr(user, 'full_name', None) and getattr(user, 'birth_date', None):
                session['form_data'] = {
                    'name': user.full_name,
                    'birth_date': user.birth_date,
                }
                session.modified = True
                next_url = request.args.get('next') or url_for('show_cards')
                return redirect(next_url)
            else:
                return redirect(url_for('profile'))
        flash('Email atau password salah', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
    return redirect(url_for('login'))

# Tentang (About) page
@app.route('/tentang', methods=['GET'])
def tentang():
    """Public About page."""
    return render_template('tentang.html')

# ---- Role-based access helpers ----
ROLE_RANK = {'bronze': 1, 'silver': 2, 'gold': 3, 'admin': 4, 'platinum': 5}

def _has_role(required: str) -> bool:
    try:
        return ROLE_RANK.get(getattr(current_user, 'role', ''), 0) >= ROLE_RANK.get(required, 1)
    except Exception:
        return False

def _enforce_role(required: str):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    if not _has_role(required):
        flash('Fitur terkunci untuk level Anda', 'error')
        return redirect(url_for('show_cards'))
    return None

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    db = SessionLocal()
    try:
        u = db.query(User).get(int(current_user.id))
        if request.method == 'POST':
            full_name = request.form.get('full_name', '').strip()
            birth_date = request.form.get('birth_date', '').strip()
            # Basic validation YYYY-MM-DD
            try:
                datetime.strptime(birth_date, '%Y-%m-%d')
            except Exception:
                flash('Format tanggal lahir harus YYYY-MM-DD', 'error')
                return render_template('profile.html', full_name=full_name, birth_date=birth_date)
            if not full_name:
                flash('Nama lengkap wajib diisi', 'error')
                return render_template('profile.html', full_name=full_name, birth_date=birth_date)
            u.full_name = full_name
            u.birth_date = birth_date
            db.add(u)
            db.commit()
            # Sync session for calculations
            session['form_data'] = {'name': u.full_name, 'birth_date': u.birth_date}
            session.modified = True
            flash('Profil berhasil diperbarui', 'success')
            return redirect(url_for('show_cards'))
        # GET
        return render_template('profile.html', full_name=u.full_name or '', birth_date=u.birth_date or '')
    finally:
        db.close()

@app.route('/register_request', methods=['GET', 'POST'])
def register_request():
    prefill_email = request.args.get('email', '').strip().lower()
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        full_name = request.form.get('full_name', '').strip()
        birth_date = request.form.get('birth_date', '').strip()
        password = request.form.get('password', '')
        if not email or not password or not full_name or not birth_date:
            flash('Semua field wajib diisi', 'error')
            return render_template('register_request.html', email=email, full_name=full_name, birth_date=birth_date)
        try:
            datetime.strptime(birth_date, '%Y-%m-%d')
        except Exception:
            flash('Format tanggal lahir harus YYYY-MM-DD', 'error')
            return render_template('register_request.html', email=email, full_name=full_name, birth_date=birth_date)
        db = SessionLocal()
        try:
            exists = db.query(User).filter(User.email == email).first()
            if exists:
                flash('Email sudah terdaftar. Silakan login.', 'info')
                return redirect(url_for('login'))
            u = User(email=email,
                     password_hash=generate_password_hash(password),
                     role='bronze',
                     is_active=False,
                     full_name=full_name,
                     birth_date=birth_date)
            db.add(u)
            db.commit()
            # Notify admin (console fallback)
            admin_email = os.environ.get('ADMIN_EMAIL') or 'admin@example.com'
            send_email(admin_email, 'Request Akun Baru', f'Email: {email}\nNama: {full_name}\nTanggal Lahir: {birth_date}')
            flash('Permintaan akun berhasil dikirim. Admin akan memverifikasi dan mengaktifkan akun Anda.', 'success')
            return redirect(url_for('login'))
        finally:
            db.close()
    return render_template('register_request.html', email=prefill_email)

@app.route('/password_reset_request', methods=['GET', 'POST'])
def password_reset_request():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        db = SessionLocal()
        token = None
        try:
            user = db.query(User).filter(User.email == email).first()
            if user:
                import uuid
                from datetime import datetime, timedelta
                token = str(uuid.uuid4())
                user.reset_token = token
                user.reset_expires_at = datetime.utcnow() + timedelta(minutes=60)
                db.add(user)
                db.commit()
        finally:
            db.close()
        if token:
            reset_link = url_for('password_reset', token=token, _external=True)
            subject = "Reset Password Anda"
            body = (
                f"Halo,\n\n"
                f"Kami menerima permintaan untuk mereset password akun Anda.\n"
                f"Silakan klik tautan berikut untuk mereset password Anda:\n"
                f"{reset_link}\n\n"
                f"Tautan ini berlaku selama 60 menit.\n"
                f"Jika Anda tidak meminta reset password, silakan abaikan email ini.\n"
            )
            send_email(email, subject, body)
        
        flash('Jika email terdaftar, link untuk mereset password telah dikirim ke email Anda.', 'info')
        return redirect(url_for('password_reset_request'))
    return render_template('password_reset_request.html')

@app.route('/password_reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.reset_token == token).first()
        if not user:
            flash('Token tidak valid', 'error')
            return redirect(url_for('login'))
        
        # Periksa apakah token sudah kedaluwarsa
        if user.reset_expires_at and user.reset_expires_at < datetime.utcnow():
            flash('Token reset password telah kedaluwarsa', 'error')
            return redirect(url_for('login'))
            
        if request.method == 'POST':
            pw1 = request.form.get('password', '')
            pw2 = request.form.get('password_confirm', '')
            if not pw1 or pw1 != pw2:
                flash('Password tidak cocok', 'error')
                return render_template('password_reset.html', token=token)
            user.password_hash = generate_password_hash(pw1)
            user.reset_token = None
            user.reset_expires_at = None
            db.add(user)
            db.commit()
            flash('Password berhasil direset. Silakan login.', 'success')
            return redirect(url_for('login'))
        return render_template('password_reset.html', token=token)
    finally:
        db.close()

@app.route('/admin/users/new', methods=['GET', 'POST'])
@login_required
def admin_create_user():
    if getattr(current_user, 'role', '') not in ['admin', 'platinum']:
        return redirect(url_for('show_cards'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        role = request.form.get('role', 'bronze').strip().lower()
        password = request.form.get('password', '')
        if not email or not password:
            flash('Email dan password wajib diisi', 'error')
            return render_template('admin_create_user.html')
        db = SessionLocal()
        try:
            exists = db.query(User).filter(User.email == email).first()
            if exists:
                flash('Email sudah terdaftar', 'error')
                return render_template('admin_create_user.html')
            u = User(email=email, password_hash=generate_password_hash(password), role=role, is_active=True)
            db.add(u)
            db.commit()
            flash('User berhasil dibuat', 'success')
            return redirect(url_for('admin_create_user'))
        finally:
            db.close()
    return render_template('admin_create_user.html')

@app.route('/webhooks/payment', methods=['POST'])
def payment_webhook():
    try:
        payload = request.get_json(silent=True) or {}
        logger.info(f"[WEBHOOK] payment payload: {payload}")
        # TODO: verify signature, locate user by email/id, update role accordingly
        return jsonify({'status': 'ok'}), 200
    except Exception as e:
        logger.error(f"[WEBHOOK] error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/admin/users', methods=['GET', 'POST'])
@login_required
def admin_manage_users():
    # Only admin/platinum can access
    if getattr(current_user, 'role', '') not in ['admin', 'platinum']:
        return redirect(url_for('show_cards'))
    db = SessionLocal()
    try:
        if request.method == 'POST':
            # Update a user's role/active
            user_id = request.form.get('user_id', '').strip()
            role = request.form.get('role', '').strip().lower()
            is_active = True if request.form.get('is_active') == 'on' else False
            if not user_id or role not in ['bronze','silver','gold','admin','platinum']:
                flash('Input tidak valid', 'error')
            else:
                u = db.query(User).get(int(user_id))
                if u:
                    prev_role = u.role
                    prev_active = u.is_active
                    u.role = role
                    u.is_active = is_active
                    db.add(u)
                    db.commit()
                    flash('User diperbarui', 'success')
                    # Notify user if activation or role changed
                    if (prev_role != u.role) or (prev_active != u.is_active and u.is_active):
                        try:
                            subject = 'Akun Anda Telah Diperbarui'
                            status = 'AKTIF' if u.is_active else 'NON-AKTIF'
                            body = f"Halo,\n\nAkun Anda telah diperbarui oleh Admin.\nStatus: {status}\nRole: {u.role}\n\nAnda dapat login di http://127.0.0.1:{int(os.environ.get('PORT', 5003))}/login\n"
                            send_email(u.email, subject, body)
                        except Exception:
                            pass
        # GET or after POST: list users
        users = db.query(User).order_by(User.created_at.desc()).all()
        return render_template('admin_manage_users.html', users=users)
    finally:
        db.close()

@app.route('/admin/analyze', methods=['GET', 'POST'])
@login_required
def admin_analyze():
    # Only admin/platinum can access
    if getattr(current_user, 'role', '') not in ['admin', 'platinum']:
        return redirect(url_for('show_cards'))
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        birth_date = request.form.get('birth_date', '').strip()
        try:
            datetime.strptime(birth_date, '%Y-%m-%d')
        except Exception:
            flash('Format tanggal lahir harus YYYY-MM-DD', 'error')
            return render_template('admin_analyze.html', name=name, birth_date=birth_date)
        if not name:
            flash('Nama wajib diisi', 'error')
            return render_template('admin_analyze.html', name=name, birth_date=birth_date)
        session['form_data'] = {'name': name, 'birth_date': birth_date}
        session.modified = True
        return redirect(url_for('show_cards'))
    # GET: prefill from query for convenience
    name = request.args.get('name', '').strip()
    birth_date = request.args.get('birth_date', '').strip()
    # If both provided and valid, set session and go directly to cards
    if name and birth_date:
        try:
            datetime.strptime(birth_date, '%Y-%m-%d')
            session['form_data'] = {'name': name, 'birth_date': birth_date}
            session.modified = True
            return redirect(url_for('show_cards'))
        except Exception:
            pass
    return render_template('admin_analyze.html', name=name, birth_date=birth_date)

@app.route('/upload', methods=['POST'])
def upload_file():
    # Cek jika file ada dalam request
    if 'file' not in request.files:
        flash('Tidak ada file yang dipilih', 'error')
        return redirect(request.url)
    
    file = request.files['file']
    
    # Jika user tidak memilih file
    if file.filename == '':
        flash('Tidak ada file yang dipilih', 'error')
        return redirect(url_for('home'))
    
    # Jika file diizinkan
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Proses file Excel
        data, error = process_excel(filepath)
        
        if error:
            flash(f'Error memproses file: {error}', 'error')
            return redirect(url_for('home'))
        
        # Simpan ke SQLite
        try:
            upload_id = save_upload_to_db(filename, data)
        except Exception as e:
            app.logger.error(f"Failed to persist upload to DB: {e}")
            upload_id = 0
        
        # Tampilkan data di template
        return render_template('index.html', data=data, upload_id=upload_id)
    else:
        flash('Format file tidak didukung. Harap unggah file Excel (.xlsx, .xls)', 'error')
        return redirect(url_for('home'))

@app.route('/api/upload', methods=['POST'])
def api_upload():
    """API endpoint untuk upload file"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        data, error = process_excel(filepath)
        
        if error:
            return jsonify({'error': f'Error processing file: {error}'}), 500

        # Persist to SQLite
        try:
            upload_id = save_upload_to_db(filename, data)
        except Exception as e:
            app.logger.error(f"Failed to persist upload to DB (API): {e}")
            upload_id = 0

        return jsonify({
            'message': 'File berhasil diunggah, diproses, dan disimpan ke database',
            'filename': filename,
            'upload_id': upload_id,
            'row_count': len(data),
            'columns': list(data[0].keys()) if data else [],
            'data': data[:100]  # Batasi data yang dikembalikan
        })
    
    return jsonify({'error': 'File type not allowed'}), 400

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        calculation_type = request.form.get('calculation_type', 'life_path')
        name = request.form.get('name', '').strip()
        birth_date = request.form.get('birth_date')
        
        if not birth_date:
            flash('Mohon isi tanggal lahir', 'error')
            return render_template('input_form.html')
            
        # Format the birth date for display
        try:
            # Try parsing as YYYY-MM-DD first
            dt = datetime.strptime(birth_date, '%Y-%m-%d')
            birth_date_disp = dt.strftime('%d/%m/%Y')
            birth_date_iso = birth_date  # Already in ISO format
        except ValueError:
            try:
                # Try parsing as DD/MM/YYYY if YYYY-MM-DD fails
                dt = datetime.strptime(birth_date, '%d/%m/%Y')
                birth_date_disp = birth_date  # Keep original format
                birth_date_iso = dt.strftime('%Y-%m-%d')  # Convert to ISO for calculations
            except ValueError:
                flash('Format tanggal lahir tidak valid. Gunakan format DD/MM/YYYY atau YYYY-MM-DD', 'error')
                return redirect(url_for('input_data'))

        # Calculate life path using the normalized ISO date
        life_info = life_path_calculation(birth_date_iso)
        if not life_info:
            flash('Gagal menghitung Life Path. Format tanggal tidak valid.', 'error')
            return redirect(url_for('input_data'))
            
        # Get life path details
        lp_number = life_info.get('life_path')
        details = get_life_path_details(lp_number)

        # Load Excel-based meanings for Life Path (reverted per user request)
        lp_deskripsi = ''
        lp_detail = ''
        lp_kekuatan = []
        lp_tantangan = []
        lp_penjelasan = ''
        challenge_numbers = []
        challenge_explanations = []
        lp_detail_paragraphs = []
        try:
            excel_path = os.path.join(os.path.dirname(__file__), 'life_path.xlsx')
            if os.path.exists(excel_path):
                df_lp = pd.read_excel(excel_path)
                # Normalize column names
                cols = {str(c).strip().lower(): c for c in df_lp.columns}
                col_no = cols.get('no')
                col_desc = cols.get('deskripsi')
                col_detail = cols.get('detail')
                col_kekuatan = cols.get('kekuatan')
                col_tantangan = cols.get('tantangan')
                col_penjelasan = (
                    cols.get('penjelasan') or cols.get('penjelasa') or cols.get('penjelasan (html)') or cols.get('penjelasan_html') or cols.get('penjelasanhtml')
                )
                if col_no:
                    try:
                        df_lp[col_no] = pd.to_numeric(df_lp[col_no], errors='coerce').astype('Int64')
                    except Exception:
                        pass
                    row = df_lp.loc[df_lp[col_no] == lp_number]
                    if not row.empty:
                        r0 = row.iloc[0]
                        def clean(v):
                            try:
                                return '' if v is None or (isinstance(v, float) and pd.isna(v)) else str(v).strip()
                            except Exception:
                                return str(v).strip() if v is not None else ''
                        lp_deskripsi = clean(r0.get(col_desc)) if col_desc else ''
                        lp_detail = clean(r0.get(col_detail)) if col_detail else ''
                        raw_kekuatan = clean(r0.get(col_kekuatan)) if col_kekuatan else ''
                        raw_tantangan = clean(r0.get(col_tantangan)) if col_tantangan else ''
                        lp_penjelasan = clean(r0.get(col_penjelasan)) if col_penjelasan else ''
                        # Split into sentences/paragraphs
                        def to_sentences(text: str):
                            if not text:
                                return []
                            t = text.replace('\r\n', '\n').strip()
                            parts = [seg.strip() for seg in re.findall(r'[^.!?\n]+[.!?]?', t) if seg and seg.strip()]
                            if len(parts) <= 1 and ('\n' in t):
                                parts = [seg.strip() for seg in t.split('\n') if seg.strip()]
                            return parts
                        if raw_kekuatan:
                            lp_kekuatan = to_sentences(raw_kekuatan)
                        if raw_tantangan:
                            lp_tantangan = to_sentences(raw_tantangan)
                        # Build paragraphs for lp_detail if plain text
                        try:
                            if lp_detail and ('<' not in lp_detail and '>' not in lp_detail):
                                text = lp_detail.replace('\r\n', '\n')
                                parts = [p.strip() for p in text.split('\n\n') if p.strip()]
                                if len(parts) <= 1:
                                    parts = [p.strip() for p in text.split('\n') if p.strip()]
                                lp_detail_paragraphs = parts
                        except Exception:
                            lp_detail_paragraphs = []
        except Exception as e:
            app.logger.warning(f"Failed to load life_path.xlsx: {e}")
         
        # Compute Challenge numbers from birth_date and fetch explanations by kode
        try:
            challenges = compute_challenges(birth_date_iso)
            challenge_numbers = challenges.get('numbers', [])
            challenge_components = challenges.get('components', {})
        except Exception as e:
            app.logger.warning(f"Failed to compute challenges: {e}")
            challenge_numbers = []
            challenge_components = {}
        # Read Tantangan from DB if available
        try:
            if challenge_numbers:
                challenge_explanations = get_tantangan_by_kodes(challenge_numbers) or []
            # Prefer C4 as main explanation
            c4_value = challenge_numbers[3] if len(challenge_numbers) >= 4 else None
            c4_explanation = ''
            if c4_value is not None:
                c4 = get_tantangan_by_kode(c4_value)
                if c4:
                    c4_explanation = c4
        except Exception as e:
            app.logger.warning(f"Failed to load Tantangan from DB: {e}")
        
        # Add additional context for the template
        context = {
            'name': name,
            'birth_date': birth_date_disp,
            'life_path': life_info,
            'life_path_number': lp_number,
            'details': details,
            'calculation_steps': life_info.get('steps', []),
            # Excel-backed fields
            'lp_deskripsi': lp_deskripsi,
            'lp_detail': lp_detail,
            'lp_detail_paragraphs': lp_detail_paragraphs,
            'lp_kekuatan': lp_kekuatan,
            'lp_tantangan': lp_tantangan,
            'lp_penjelasan': lp_penjelasan,
            # Challenges (computed) and explanations (from Excel by kode)
            'lp_challenges': challenge_numbers,
            'challenge_explanations': challenge_explanations,
            'c4_value': c4_value if 'c4_value' in locals() else None,
            'c4_explanation': c4_explanation if 'c4_explanation' in locals() else '',
            'c4_steps': '',
            'c4_paragraphs': [],
        }
        
        # Build human-readable steps for C4 using reduced M and Y
        try:
            if 'M' in challenge_components and 'Y' in challenge_components:
                Mv = challenge_components['M']
                Yv = challenge_components['Y']
                if 'c4_value' in locals() and c4_value is not None:
                    context['c4_steps'] = f"M = {Mv}, Y = {Yv} → |M − Y| = |{Mv} − {Yv}| = {c4_value}"
                elif len(challenge_numbers) >= 4:
                    context['c4_steps'] = f"M = {Mv}, Y = {Yv} → |M − Y| = |{Mv} − {Yv}| = {challenge_numbers[3]}"
        except Exception:
            context['c4_steps'] = ''
        
        # Split C4 explanation text into paragraphs
        if 'c4_explanation' in locals() and c4_explanation:
            text = str(c4_explanation).replace('\r\n', '\n')
            parts = [p.strip() for p in text.split('\n\n') if p.strip()]
            if len(parts) <= 1:
                parts = [p.strip() for p in text.split('\n') if p.strip()]
            context['c4_paragraphs'] = parts
        
        return render_template('result_life_path.html', **context)
        
    except Exception as e:
        app.logger.error(f"Error in life_path_result: {str(e)}")
        flash('Terjadi kesalahan saat memproses permintaan Anda. Silakan coba lagi.', 'error')
        flash('Terjadi kesalahan saat memproses data Anda. Silakan isi ulang.', 'error')
        return redirect(url_for('input_data'))

@app.route('/harani', methods=['GET', 'POST'])
@app.route('/harani_form', methods=['GET', 'POST'])
def harani_form():
    # Debug session data
    print("Current session data:", session)
    
    # Pastikan data user ada di session
    if 'form_data' not in session:
        print("No form_data in session, redirecting to input")
        flash('Silakan isi data terlebih dahulu', 'error')
        return redirect(url_for('input_data'))
    
    form = HaraniForm()
    result = None
    
    # Handle form submission
    if request.method == 'POST' and form.validate_on_submit():
        try:
            full_name = form.full_name.data.strip()
            if not full_name:
                flash('Nama tidak valid', 'error')
                return redirect(url_for('harani_form'))
            # Simpan nama ke session untuk dipakai di harani_result
            session['harani_data'] = {
                'full_name': full_name,
                'birth_date': session['form_data'].get('birth_date', '')
            }
            session.modified = True
            return redirect(url_for('harani_result'))
        except Exception as e:
            print(f"Error in harani_form: {str(e)}")
            import traceback
            traceback.print_exc()
            flash('Terjadi kesalahan saat memproses data', 'error')
    
    # Pre-fill the form with session data if available
    if 'harani_data' in session and not form.full_name.data:
        form.full_name.data = session['harani_data'].get('full_name', '')
    
    return render_template('harani_form.html', form=form, result=result)

@app.route('/harani_result', methods=['GET'])
@login_required
def harani_result():
    # Prefer latest name and birth_date from form_data, fall back to harani_data if missing
    full_name = ''
    birth_date = ''
    if 'form_data' in session:
        full_name = session['form_data'].get('name', '')
        birth_date = session['form_data'].get('birth_date', '')
    if (not full_name or not birth_date) and 'harani_data' in session:
        full_name = full_name or session['harani_data'].get('full_name', '')
        birth_date = birth_date or session['harani_data'].get('birth_date', '')
    if full_name and birth_date:
        # Refresh cached harani_data for consistency
        session['harani_data'] = {
            'full_name': full_name,
            'birth_date': birth_date,
        }
        session.modified = True
    else:
        flash('Silakan isi data terlebih dahulu', 'error')
        return redirect(url_for('input_data'))

    if not full_name:
        flash('Nama tidak valid', 'error')
        return redirect(url_for('harani_form'))
    
    try:
        # Hitung numerologi nama (baru)
        harani_info = harani_calculation(full_name)
        name_number = harani_info.get('number', 0)
        
        # Baca data dari SQLite
        # Coba ambil persis berdasarkan name_number; jika tidak ada, wrap ke 1..9
        number = int(name_number or 0)
        row = get_harani(number) if number else None
        if not row:
            # fallback wrap ke 1..9
            wrapped = ((number - 1) % 9) + 1 if number else 1
            row = get_harani(wrapped)
            number = wrapped
        if not row:
            flash('Data numerologi tidak ditemukan di database', 'error')
            return redirect(url_for('harani_form'))
        
        # Format data untuk template
        def to_sentences(text: str):
            if not text:
                return []
            t = str(text).replace('\r\n', '\n').strip()
            import re as _re
            parts = [seg.strip() for seg in _re.findall(r'[^.!?\n]+[.!?]?', t) if seg and seg.strip()]
            if len(parts) <= 1 and ('\n' in t or ';' in t or ', ' in t):
                # fallback to newline or semicolon, then comma
                tmp = []
                for chunk in t.replace(';', '\n').split('\n'):
                    tmp.extend([p.strip() for p in chunk.split(',') if p.strip()])
                parts = tmp
            return parts
        name_meaning = {
            'deskripsi': str(row.get('deskripsi', 'Data tidak tersedia')),
            'kekuatan': to_sentences(str(row.get('kekuatan', ''))),
            'kelemahan': to_sentences(str(row.get('kelemahan', ''))),
            'makna_energi': str(row.get('makna_energi', 'Data tidak tersedia')),
        }
        
        # Debug info
        print(f"Showing result for name: {full_name}, number: {name_number}")
        print(f"Name meaning data: {name_meaning}")
        
        # Calculate Heart's Desire
        from numerology_utils import heart_desire_calculation, personality_calculation
        from db_access import get_heart_desire, get_personality
        
        heart_desire_info = heart_desire_calculation(full_name)
        heart_desire_number = heart_desire_info.get('number', 0)
        heart_desire_meaning = None
        
        if heart_desire_number and 1 <= heart_desire_number <= 9:
            try:
                heart_desire_meaning = get_heart_desire(heart_desire_number)
            except Exception as e:
                print(f'Heart Desire DB error: {e}')
                # Provide fallback data if database is not available
                heart_desire_meaning = {
                    'deskripsi': f'Heart\'s Desire Number {heart_desire_number} represents your inner desires and motivations. This number reveals what your soul truly yearns for in life.',
                    'kekuatan': 'Database not available - please initialize Heart\'s Desire data.',
                    'kelemahan': '',
                    'saran': 'Run the init_heart_desire.py script to load complete descriptions.'
                }
        
        # Calculate Personality Number
        personality_info = personality_calculation(full_name)
        personality_number = personality_info.get('number', 0)
        personality_meaning = None
        
        if personality_number and (1 <= personality_number <= 9 or personality_number in (11, 22)):
            try:
                personality_meaning = get_personality(personality_number)
            except Exception as e:
                print(f'Personality DB error: {e}')
                # Provide fallback data if database is not available
                personality_meaning = f'Personality Number {personality_number} represents how others see you and your outer self. This number reveals the first impression you make on others.'
        
        # Format birth date for display as D/M/YYYY (no leading zeros)
        def fmt_dmy(date_str: str) -> str:
            for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y'):
                try:
                    dt = datetime.strptime(date_str, fmt)
                    # Build non-padded day/month
                    return f"{dt.day}/{dt.month}/{dt.year}"
                except Exception:
                    continue
        birth_date_disp = fmt_dmy(birth_date)
        return render_template('harani_result.html',
                            full_name=full_name,
                            name=full_name,  # alias for template compatibility
                            birth_date=birth_date_disp,
                            name_number=name_number,
                            name_meaning=name_meaning,
                            heart_desire_number=heart_desire_number,
                            heart_desire_meaning=heart_desire_meaning,
                            personality_number=personality_number,
                            personality_meaning=personality_meaning,
                            letters=harani_info.get('letters', []),
                            total_raw=harani_info.get('total', 0))
        
    except Exception as e:
        print(f"Error in harani_result: {str(e)}")
        flash(f'Terjadi kesalahan: {str(e)}', 'error')
        return redirect(url_for('harani_form'))

@app.route('/karma', methods=['GET'])
def karma_form():
    return render_template('karma_form.html')

@app.route('/rejeki', methods=['GET'])
def rejeki_form():
    return render_template('rejeki_form.html')

def validate_date_format(form, field):
    try:
        date_str = field.data
        if not date_str:
            raise ValidationError('Tanggal lahir harus diisi')
            
        # Coba format DD/MM/YYYY
        try:
            datetime.strptime(date_str, '%d/%m/%Y')
            return
        except ValueError:
            pass
            
        # Coba format YYYY-MM-DD
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return
        except ValueError:
            pass
            
        raise ValidationError('Format tanggal tidak valid. Gunakan DD/MM/YYYY atau YYYY-MM-DD')
        
    except Exception as e:
        raise ValidationError(str(e))

class ArahForm(FlaskForm):
    name = StringField('Nama Lengkap', validators=[
        DataRequired(message='Nama lengkap harus diisi'),
        Length(min=2, max=100, message='Nama harus antara 2-100 karakter')
    ], render_kw={
        'placeholder': 'Masukkan nama lengkap Anda',
        'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
        'autocomplete': 'name'
    })
    
    birth_date = StringField('Tanggal Lahir', validators=[
        DataRequired(message='Tanggal lahir harus diisi'),
        validate_date_format
    ], render_kw={
        'placeholder': 'DD/MM/YYYY atau YYYY-MM-DD',
        'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
        'autocomplete': 'bday'
    })

@app.route('/arah', methods=['GET', 'POST'])
def arah_form():
    """Nonaktifkan form Arah terpisah; gunakan data dari form awal saja."""
    form_data = session.get('form_data') or {}
    if not form_data or not form_data.get('birth_date'):
        flash('Silakan isi data terlebih dahulu', 'error')
        return redirect(url_for('input_data'))

    # Selalu arahkan ke hasil yang berbasis session
    return redirect(url_for('arah_result'))

# Arah Sukses result (calculation and display)
@app.route('/arah_result', methods=['GET'])
@login_required
def arah_result():
    guard = _enforce_role('silver')
    if guard:
        return guard
    """Hitung Arah Sukses menggunakan data dari form input pertama (session['form_data'])."""
    logger.info("Arah result accessed")
    
    # Check if we have form data in session; if missing, try to rebuild from query params
    if 'form_data' not in session or not session['form_data']:
        q_name = request.args.get('name', '').strip()
        q_birth = request.args.get('birth_date', '').strip()
        if q_name and q_birth:
            session['form_data'] = {'name': q_name, 'birth_date': q_birth}
            session.modified = True
            logger.info("Rebuilt session form_data from query params for arah_result")
        else:
            logger.warning("No form data in session and no query params provided; redirecting to calculation_options")
            flash('Data sesi tidak ditemukan. Silakan kembali ke menu utama dan klik Arah lagi.', 'info')
            return redirect(url_for('calculation_options'))
    
    # Additional safety check for form_data content
    if not session.get('form_data'):
        logger.warning("Session form_data is None; redirecting to calculation_options")
        flash('Data sesi tidak valid. Silakan kembali ke menu utama dan klik Arah lagi.', 'info')
        return redirect(url_for('calculation_options'))
    
    try:
        form_data = session['form_data']
        name = form_data.get('name', '').strip()
        birth_date = form_data.get('birth_date', '').strip()
        
        if not birth_date:
            logger.warning("No birth date in form data; falling back to today")
            flash('Tanggal lahir tidak ditemukan di sesi. Menggunakan tanggal hari ini sebagai sementara.', 'warning')
            birth_date = datetime.now().strftime('%Y-%m-%d')
        
        # Normalize name for display
        try:
            decoded_name = urllib.parse.unquote_plus(name) if name else ''
            normalized_name = ' '.join(decoded_name.replace('+', ' ').split()) if decoded_name else ''
        except Exception as e:
            logger.warning(f"Error decoding name: {str(e)}")
            normalized_name = name
        
        # Parse date with multiple format support
        dt = None
        for fmt in ('%d/%m/%Y', '%m/%d/%Y', '%Y-%m-%d', '%d-%m-%Y', '%m-%d-%Y'):
            try:
                dt = datetime.strptime(birth_date, fmt)
                break
            except ValueError:
                continue
                
        if not dt:
            # Jika gagal parsing, gunakan tanggal hari ini sebagai fallback agar tidak looping
            error_msg = f"Format tanggal tidak valid: {birth_date}. Menggunakan tanggal hari ini."
            logger.warning(error_msg)
            flash(error_msg, 'warning')
            dt = datetime.now()
        
        # Check if date is in the future
        if dt > datetime.now():
            error_msg = 'Tanggal lahir berada di masa depan. Menggunakan tanggal hari ini sebagai sementara.'
            logger.warning(error_msg)
            flash(error_msg, 'warning')
            dt = datetime.now()
        
        # Format date consistently for calculation
        formatted_date = dt.strftime('%Y-%m-%d')
        
        # Calculate direction
        logger.info(f"Calculating arah_result for birth_date={formatted_date}, name='{normalized_name}'")
        from numerology_utils import calculate_arah_sukses
        
        result = calculate_arah_sukses(formatted_date)
        if not result or 'best_direction' not in result:
            # Paksa struktur minimal agar halaman tetap bisa dirender tanpa looping
            logger.error('calculate_arah_sukses tidak mengembalikan hasil yang lengkap; menggunakan default minimal.')
            flash('Terjadi masalah saat menghitung arah. Menampilkan hasil sementara.', 'warning')
            result = result or {}
            result.setdefault('best_direction', 'Tidak Diketahui')
            result.setdefault('best_score', 0)
            result.setdefault('direction_scores', {})
            result.setdefault('values', {})
            result.setdefault('steps', [])
            result.setdefault('birth_date', dt.strftime('%d/%m/%Y'))
        
        # Prepare result data
        result.update({
            'name': normalized_name,
            'birth_date': dt.strftime('%d/%m/%Y'),
            'deskripsi': _get_arah_description(result.get('best_direction', ''))
        })
        
        # Prepare direction scores for display
        direction_scores = []
        for direction, score in result.get('direction_scores', {}).items():
            # Recommendation rule: scores 7 and 6 are recommended
            is_recommended = score in (7, 6)
            direction_scores.append({
                'name': direction,
                'score': score,
                'is_best': direction == result['best_direction'],
                'is_recommended': is_recommended,
            })
        
        # Sort by score (highest first)
        direction_scores.sort(key=lambda x: x['score'], reverse=True)
        result['direction_scores'] = direction_scores
        
        # Ensure all required keys exist
        result.setdefault('values', {})
        result.setdefault('steps', [])
        
        # Calculate Papan Pythagoras
        pythagoras_data = None
        if normalized_name:
            try:
                from numerology_utils import papan_pythagoras_calculation
                pythagoras_data = papan_pythagoras_calculation(normalized_name)
                logger.info(f"Papan Pythagoras calculated for {normalized_name}")
            except Exception as e:
                logger.warning(f"Error calculating Papan Pythagoras: {e}")
                pythagoras_data = {'error': f'Error calculating Papan Pythagoras: {str(e)}'}
        
        logger.info(f"Rendering arah_result for {normalized_name} ({formatted_date})")
        logger.info(f"Result best_direction: {result.get('best_direction', 'NOT_FOUND')}")
        logger.info(f"Result keys: {list(result.keys())}")
        return render_template('result_arah.html',
                            name=normalized_name,
                            birth_date=result['birth_date'],
                            result=result,
                            pythagoras_data=pythagoras_data)
        
    except Exception as e:
        error_msg = f"Terjadi kesalahan tak terduga: {str(e)}"
        logger.error(f"Error in arah_result: {error_msg}\n{traceback.format_exc()}")
        flash(error_msg, 'error')

        # Create a default result with error information
        result = {
            'name': normalized_name if 'normalized_name' in locals() else '',
            'birth_date': dt.strftime('%d/%m/%Y') if 'dt' in locals() else '',
            'best_direction': 'Error',
            'best_score': 0,
            'direction_scores': [],
            'values': {},
            'steps': [],
            'deskripsi': 'Terjadi kesalahan saat menghitung arah. Silakan coba lagi atau hubungi dukungan.'
        }

        # Render the result template with error
        return render_template('result_arah.html',
                               name=result['name'],
                               birth_date=result['birth_date'],
                               result=result,
                               pythagoras_data=None)

def _read_excel_row_by_number(filepath: str, number: int):
    df = pd.read_excel(filepath)
    if 'No' not in df.columns:
        raise ValueError("Kolom 'No' tidak ditemukan pada file Excel")
    # Normalize numeric
    try:
        df['No'] = pd.to_numeric(df['No'], errors='coerce').astype('Int64')
    except Exception:
        pass
    row = df[df['No'] == int(number)]
    if row.empty:
        # Fallback wrap-around
        unique_numbers = [n for n in df['No'].dropna().unique().tolist() if str(n).isdigit()]
        if unique_numbers:
            idx = (int(number) - 1) % len(unique_numbers)
            row = df[df['No'] == unique_numbers[idx]]
    return row.iloc[0].to_dict()

def _extract_rejeki_fields(row_dict: dict):
    """Normalize possible Excel columns for Rejeki into unified fields.
    Supports either single text columns or multiple columns with prefixes.
    Returns: deskripsi:str, kekuatan:list[str], kelemahan:list[str], saran:str
    """
    if not row_dict:
        return '', [], [], ''
    # Description: prefer 'deskripsi' then alternatives
    desc = str(row_dict.get('deskripsi') or row_dict.get('Deskripsi') or row_dict.get('description') or '').strip()
    # Kekuatan
    kekuatan = []
    if row_dict.get('kekuatan') or row_dict.get('Kekuatan'):
        raw = str(row_dict.get('kekuatan') or row_dict.get('Kekuatan') or '')
        kekuatan = [s.strip() for s in raw.replace('\n',';').split(';') if s and str(s).strip()]
    else:
        # collect prefixed columns kekuatan1..kekuatanN
        for k, v in row_dict.items():
            if isinstance(k, str) and k.lower().startswith('kekuatan') and str(v).strip():
                kekuatan.append(str(v).strip())
        # keep stable order by sorting keys that end with digits
        if kekuatan:
            pass
    # Kelemahan
    kelemahan = []
    if row_dict.get('kelemahan') or row_dict.get('Kelemahan'):
        raw = str(row_dict.get('kelemahan') or row_dict.get('Kelemahan') or '')
        kelemahan = [s.strip() for s in raw.replace('\n',';').split(';') if s and str(s).strip()]
    else:
        for k, v in row_dict.items():
            if isinstance(k, str) and k.lower().startswith('kelemahan') and str(v).strip():
                kelemahan.append(str(v).strip())
    # Saran
    saran = str(row_dict.get('saran') or row_dict.get('Saran') or row_dict.get('tips') or '').strip()
    return desc, kekuatan, kelemahan, saran

@app.route('/karma_result', methods=['GET'])
@login_required
def karma_result():
    guard = _enforce_role('silver')
    if guard:
        return guard
    if 'form_data' not in session:
        flash('Silakan isi data terlebih dahulu', 'error')
        return redirect(url_for('input_data'))
    name = session['form_data'].get('name', '')
    birth_date = session['form_data'].get('birth_date', '')  # YYYY-MM-DD
    # New official method: sum of missing digits from name's digit mapping (1..9), digital-rooted
    try:
        karma_number = int(karma_number_from_missing_digits(name))
    except Exception:
        karma_number = 0
    # Ensure Excel
    filepath = os.path.join(os.path.dirname(__file__), 'karma.xlsx')
    _ensure_excel(filepath, _default_karma_records())
    try:
        data = _read_excel_row_by_number(filepath, karma_number)
    except Exception as e:
        flash(f'Gagal membaca data Karma: {e}', 'error')
        return redirect(url_for('calculation_options'))
    return render_template('result_karma.html',
                           name=name,
                           birth_date=birth_date,
                           number=karma_number,
                           deskripsi=str(data.get('deskripsi', '')),
                           kekuatan=[s.strip() for s in str(data.get('kekuatan','')).replace('\n',';').split(';') if s.strip()],
                           kelemahan=[s.strip() for s in str(data.get('kelemahan','')).replace('\n',';').split(';') if s.strip()],
                           saran=str(data.get('saran','')))

@app.route('/rejeki_result', methods=['GET'])
@login_required
def rejeki_result():
    guard = _enforce_role('silver')
    if guard:
        return guard
    if 'form_data' not in session:
        flash('Silakan isi data terlebih dahulu', 'error')
        return redirect(url_for('input_data'))
    name = session['form_data'].get('name', '')
    birth_date = session['form_data'].get('birth_date', '')
    # New: Use Pythagoras-based Rejeki from birth date only (A..Z mapping per table)
    calc = rejeki_pythagoras_from_birthdate(birth_date)
    number = int(calc.get('rejeki', calc.get('number', 0)))
    P = int(calc.get('P', 0))
    Q = int(calc.get('Q', 0))
    pq_str = str(calc.get('pq', '')) or f"{P}{Q}" if (P and Q) else ''
    deskripsi_p = calc.get('deskripsi_p', '')
    deskripsi_q = calc.get('deskripsi_q', '')
    deskripsi_pq = calc.get('deskripsi_pq', '')
    values = calc.get('values', {})
    filepath = os.path.join(os.path.dirname(__file__), 'rejeki.xlsx')
    _ensure_excel(filepath, _default_rejeki_records())
    try:
        data_row = _read_excel_row_by_number(filepath, number)
        deskripsi, kekuatan, kelemahan, saran = _extract_rejeki_fields(data_row)
        # If calc already provided description, prefer it
        if calc.get('deskripsi'):
            deskripsi = calc['deskripsi']
        # Fetch P&Q description from rejeki database table using P&Q number
        pair_deskripsi = ''
        if pq_str and pq_str.isdigit():
            try:
                from db_access import get_rejeki
                pq_data = get_rejeki(int(pq_str))
                if pq_data:
                    pair_deskripsi = pq_data.get('deskripsi', '')
            except Exception:
                pair_deskripsi = ''
    except Exception as e:
        flash(f'Gagal membaca data Rejeki: {e}', 'error')
        return redirect(url_for('calculation_options'))
    return render_template('result_rejeki.html',
                           name=name,
                           birth_date=birth_date,
                           number=number,
                           R=number,
                           P=P,
                           Q=Q,
                           pq=pq_str,
                           deskripsi=deskripsi,
                           deskripsi_p=deskripsi_p,
                           deskripsi_q=deskripsi_q,
                           deskripsi_pq=deskripsi_pq,
                           kekuatan=kekuatan,
                           kelemahan=kelemahan,
                           saran=saran,
                           pair_deskripsi=pair_deskripsi,
                           pair_title=f"Deskripsi P&Q ({pq_str})" if pq_str else 'Deskripsi P&Q',
                           values=values)

def _get_arah_description(direction: str) -> str:
    """Get description for a direction from SQLite (arah_sukses table)."""
    try:
        if not direction:
            return ''
        desc = get_arah_deskripsi(direction)
        if desc:
            return desc
    except Exception as e:
        logger.error(f"Error in _get_arah_description (DB): {str(e)}")
    # Fallback description if not found
    return f"Arah {direction} adalah arah keberuntungan Anda berdasarkan perhitungan numerologi."

@app.route('/api/calculate_life_path', methods=['POST'])
def api_calculate_life_path():
    form = LifePathForm()
    
    if form.validate_on_submit():
        name = form.name.data.strip()
        birth_date = form.birth_date.data.strip()
        
        try:
            # Format tanggal lahir
            formatted_date = datetime.strptime(birth_date, '%Y-%m-%d').strftime('%d/%m/%Y')
            
            # Hitung life path
            life_path_info = life_path_calculation(birth_date)
            if not life_path_info:
                return jsonify({
                    'success': False,
                    'error': 'Gagal menghitung life path. Format tanggal tidak valid.'
                }), 400
                
            life_path_number = life_path_info.get('life_path')
            
            # Dapatkan detail life path dari Excel
            life_path_data = get_life_path_details(life_path_number)
            if not life_path_data:
                return jsonify({
                    'success': False,
                    'error': 'Data life path tidak ditemukan'
                }), 404
            
            # Siapkan data hasil
            result = {
                'success': True,
                'data': {
                    'name': name,
                    'birth_date': formatted_date,
                    'life_path_number': life_path_number,
                    'life_path_meaning': life_path_data.get('deskripsi', ''),
                    'additional_info': life_path_data.get('informasi_tambahan', ''),
                    'personality_traits': life_path_data.get('sifat_pribadi', []),
                    'challenges': life_path_data.get('tantangan', []),
                    'career_suggestions': life_path_data.get('saran_karir', [])
                }
            }
            
            return jsonify(result)
                                
        except ValueError as e:
            return jsonify({
                'success': False,
                'error': 'Format tanggal tidak valid. Gunakan format YYYY-MM-DD'
            }), 400
        except Exception as e:
            print(f"Error in api_calculate_life_path: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': 'Terjadi kesalahan saat memproses permintaan Anda'
            }), 500

@app.route('/weton_result', methods=['GET'])
@login_required
def weton_result():
    """Handle Weton calculation and display results with proper validation."""
    try:
        # Get data from query params or session
        name = request.args.get('name', '').strip()
        birth_date_str = request.args.get('birth_date', '').strip()
        
        # If no query params, try to get from session
        if not all([name, birth_date_str]) and 'form_data' in session:
            name = session['form_data'].get('name', '')
            birth_date_str = session['form_data'].get('birth_date', '')
        
        # Decode and normalize name (handle '+' and URL-encoded input)
        try:
            decoded_name = urllib.parse.unquote_plus(name) if name else ''
            normalized_name = ' '.join(decoded_name.replace('+', ' ').split())
            display_name = normalized_name.title()
        except Exception:
            normalized_name = name
            display_name = name

        # Validate inputs
        if not normalized_name:
            flash('Nama tidak boleh kosong', 'error')
            return redirect(url_for('weton_form'))
            
        if not birth_date_str:
            flash('Tanggal lahir tidak boleh kosong', 'error')
            return redirect(url_for('weton_form'))
        
        # Normalize and validate date format
        birth_dt = None
        for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y'):
            try:
                birth_dt = datetime.strptime(birth_date_str, fmt)
                birth_iso = birth_dt.strftime('%Y-%m-%d')
                break
            except ValueError:
                continue
        
        if not birth_dt:
            flash('Format tanggal lahir tidak valid. Gunakan format DD/MM/YYYY atau YYYY-MM-DD', 'error')
            return redirect(url_for('weton_form'))
        
        # Validate date is not in the future
        if birth_dt > datetime.now():
            flash('Tanggal lahir tidak boleh di masa depan', 'error')
            return redirect(url_for('weton_form'))
        
        # Calculate Weton information
        weton_info = weton_calculation(birth_iso)
        if not weton_info:
            flash('Gagal menghitung weton. Pastikan tanggal lahir valid.', 'error')
            return redirect(url_for('weton_form'))
        
        # Get Weton meaning with error handling
        try:
            weton_meaning = get_weton_meaning(weton_info) or ''
        except Exception as e:
            app.logger.error(f"Error getting weton meaning: {str(e)}", exc_info=True)
            weton_meaning = '<p>Maaf, terjadi kesalahan saat memproses makna weton.</p>'
        
        # Compute Lintang from (Hari, Pasaran) using DB (lintang_bali table)
        lintang_name = ''
        lintang_desc = ''
        lintang_traits = []  # list of {'watak':..., 'arti':...}
        try:
            h = str(weton_info.get('hari', '')).strip()
            p = str(weton_info.get('pasaran', '')).strip()
            # Accept alias: Umanis == Legi
            row = get_lintang(h, p) or (get_lintang(h, 'Legi') if p.lower() == 'umanis' else None)
            if row:
                lintang_name = row.get('lintang', '')
                lintang_desc = row.get('deskripsi', '')
                lintang_traits = row.get('traits', []) or []
        except Exception as e:
            app.logger.warning(f"Gagal membaca lintang_bali dari DB: {e}")

        
        # Calculate Wewaran list (parse HTML to list items)
        wewaran_list = []
        try:
            # Normalize inputs
            hari_name = str(weton_info.get('hari', '')).strip()
            pasaran_name = str(weton_info.get('pasaran', '')).strip()
            wuku_name = str(weton_info.get('wuku', '')).strip()

            # Maps for neptu values
            neptu_hari_map = {'Senin': 4, 'Selasa': 3, 'Rabu': 7, 'Kamis': 8, 'Jumat': 6, 'Sabtu': 9, 'Minggu': 5}
            neptu_pas_map = {'Legi': 5, 'Pahing': 9, 'Pon': 7, 'Wage': 4, 'Kliwon': 8, 'Umanis': 5}
            neptu_hari = neptu_hari_map.get(hari_name.capitalize(), 0)
            neptu_pas = neptu_pas_map.get(pasaran_name.capitalize(), 0)

            # Wuku index (1..30)
            wuku_names = [
                'Sinta','Landep','Wukir','Kurantil','Tolu','Gumbreg','Wariga','Warigadian','Julungwangi','Sungsang',
                'Dunggulan','Kuningan','Langkir','Medangsia','Pujut','Pahang','Krulut','Merakih','Tambir','Medangkungan',
                'Matal','Uye','Menail','Prangbakat','Bala','Wugu','Wayang','Kelawu','Dukut','Watugunung'
            ]
            try:
                wuku_num = wuku_names.index(wuku_name.capitalize()) + 1 if wuku_name else 0
            except ValueError:
                wuku_num = 0

            # Day index for Wewaran: Sunday=0 .. Saturday=6
            day_order = ['Minggu','Senin','Selasa','Rabu','Kamis','Jumat','Sabtu']
            try:
                day_idx = day_order.index(hari_name.capitalize())
            except ValueError:
                day_idx = 0

            # Compute values
            day_num_1based = day_idx + 1  # Align with numerology_utils expectations (Minggu=1..Sabtu=7)
            values = {
                'Ekawara': calculate_ekawara(neptu_hari, neptu_pas),
                'Dwiwara': calculate_dwiwara(neptu_hari, neptu_pas),
                'Triwara': calculate_triwara(wuku_num, day_idx),
                'Caturwara': calculate_caturwara(wuku_num, day_num_1based, hari_name),
                'Sadwara': calculate_sadwara(wuku_num, day_idx),
                'Astawara': calculate_astawara(wuku_num, day_num_1based, hari_name),
                'Sangawara': calculate_sangawara(wuku_num, day_idx),
                'Dasawara': calculate_dasawara(neptu_hari, neptu_pas),
            }
            
            # Debug logging
            app.logger.info(f"Wewaran calculation inputs: neptu_hari={neptu_hari}, neptu_pas={neptu_pas}, wuku_num={wuku_num}, day_idx={day_idx}, hari_name={hari_name}")
            app.logger.info(f"Calculated Wewaran values: {values}")

            # Define the order of Wewaran types
            order = ['Ekawara', 'Dwiwara', 'Triwara', 'Caturwara', 
                    'Sadwara', 'Astawara', 'Sangawara', 'Dasawara']
            
            # Build the wewaran_list using DB-backed descriptions
            wewaran_list = []
            processed_count = 0
            
            for level in order:
                try:
                    # Get the calculated Wewaran name
                    calculated_name = values.get(level, '')
                    
                    # Initialize with default values
                    description = f"Informasi untuk {level} tidak tersedia."
                    display_value = calculated_name or "-"
                    
                    # Calculate the correct nilai for Excel lookup
                    calc_nilai = -1
                    
                    if level == 'Ekawara':
                        # Ekawara logic: if neptu total is even = empty, if odd = "Luang"
                        neptu_total = neptu_hari + neptu_pas
                        if neptu_total % 2 == 0:  # Even (genap)
                            # For even neptu, Ekawara is empty - no Excel lookup
                            display_value = "-"
                            description = "Tidak ada Ekawara untuk neptu genap."
                        else:  # Odd (ganjil)
                            calc_nilai = 1  # Use nilai=1 for "Luang" in Excel
                            display_value = "Luang"
                    elif level == 'Dwiwara':
                        calc_nilai = (neptu_hari + neptu_pas) % 2
                    elif level == 'Triwara':
                        calc_nilai = (max(0, wuku_num - 1) + day_idx) % 3
                    elif level == 'Caturwara':
                        w0 = max(0, wuku_num - 1)
                        # Use 1-based day number for Caturwara to match numerology_utils (Minggu=1..Sabtu=7)
                        day_num = day_idx + 1
                        # Match logic with numerology_utils.calculate_caturwara
                        if wuku_num <= 11 and hari_name != 'Senin':
                            calc_nilai = ((w0 * 7) + day_num) % 4
                        elif wuku_num == 11 and hari_name == 'Senin':
                            calc_nilai = ((w0 * 7) + 2 + day_num) % 4
                        else:
                            calc_nilai = ((w0 * 7) + day_num) % 4
                    elif level == 'Sadwara':
                        calc_nilai = (max(0, wuku_num - 1) + day_idx) % 6
                    elif level == 'Astawara':
                        w0 = max(0, wuku_num - 1)
                        # Use 1-based day number to match numerology_utils (Minggu=1..Sabtu=7)
                        day_num = day_idx + 1
                        # Option B: add +1 when wuku<=11 and not Monday; add +2 when wuku==11 and Monday; else base formula
                        if wuku_num <= 11 and hari_name != 'Senin':
                            calc_nilai = ((w0 * 7) + 1 + day_num) % 8
                        elif wuku_num == 11 and hari_name == 'Senin':
                            calc_nilai = ((w0 * 7) + 2 + day_num) % 8
                        else:
                            calc_nilai = ((w0 * 7) + day_num) % 8  # Excel uses 0-based indexing
                    elif level == 'Sangawara':
                        calc_nilai = ((max(0, wuku_num - 1) * 7) + day_idx + 6) % 9
                    elif level == 'Dasawara':
                        calc_nilai = (neptu_hari + neptu_pas) % 10
                    
                    # Look up in DB if we have a valid calc_nilai
                    if calc_nilai >= 0:
                        entry = get_wewaran_entry(level, calc_nilai)
                        if entry and (entry.get('deskripsi') or entry.get('nama')):
                            description = entry.get('deskripsi') or description
                            # If no calculated name, use DB name
                            if not calculated_name and entry.get('nama'):
                                display_value = entry.get('nama')
                            # Handle spelling variations
                            if isinstance(display_value, str) and display_value.lower() == 'menge':
                                display_value = 'Menga'
                            processed_count += 1
                            app.logger.debug(f"Found DB data for {level}[{calc_nilai}]: {display_value} - {description[:50]}...")
                        else:
                            app.logger.warning(f"No DB data found for {level}[{calc_nilai}]")
                    
                    app.logger.debug(f"Processing {level}: calc_nilai={calc_nilai}, display_value='{display_value}', desc='{description[:50]}...'")
                    
                    
                    # Add to results
                    wewaran_list.append({
                        'nama': level,
                        'nilai': display_value,
                        'keterangan': description
                    })
                    
                    app.logger.debug(f"Processed {level}: {display_value} - {description[:30]}...")
                    
                except Exception as e:
                    app.logger.error(f"Error processing {level}: {str(e)}", exc_info=True)
                    # Add a placeholder to prevent breaking the UI
                    wewaran_list.append({
                        'nama': level,
                        'nilai': 'Error',
                        'keterangan': f'Gagal memproses data: {str(e)}'
                    })
            
            # Log processing summary
            if processed_count == 0 and wewaran_list:
                app.logger.warning("No Wewaran descriptions were matched. Check if the Excel data format is correct.")
            else:
                app.logger.info(f"Successfully processed {processed_count} out of {len(order)} Wewaran types")
        except Exception as e:
            app.logger.warning(f"Gagal menghitung Wewaran secara langsung: {e}")
            wewaran_list = []
        
        # Format display data
        try:
            # Display birth date in D/M/YYYY
            def fmt_dmy(date_str: str) -> str:
                for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y'):
                    try:
                        dt = datetime.strptime(date_str, fmt)
                        # Build non-padded day/month
                        return f"{dt.day}/{dt.month}/{dt.year}"
                    except Exception:
                        continue
            birth_date_disp = fmt_dmy(birth_iso)
        except Exception:
            birth_date_disp = birth_iso
        
        # Update session with form data
        session['form_data'] = {
            'name': normalized_name,
            'birth_date': birth_date_str
        }
        session.modified = True
        
        # Prepare context for template
        # Lookup descriptions for Hari, Pasaran, Wuku from database tables
        try:
            hari_name_cap = weton_info.get('hari', '')
            pasaran_name_cap = weton_info.get('pasaran', '')
            wuku_name_cap = weton_info.get('wuku', '')

            # Prefer combined pair mapping for Hari+Pasaran
            ket_hari_pair, ket_pas_pair = get_weton_pair_desc(hari_name_cap, pasaran_name_cap)

            hari_desc = ket_hari_pair or (get_weton_generic_desc('Hari', hari_name_cap) or '')
            pasaran_desc = ket_pas_pair or (get_weton_generic_desc('Pasaran', pasaran_name_cap) or '')
            wuku_desc = get_weton_generic_desc('Wuku', wuku_name_cap) or ''
        except Exception:
            hari_desc = ''
            pasaran_desc = ''
            wuku_desc = ''
        context = {
            'name': display_name,
            'birth_date': birth_date_disp,
            'hari': weton_info.get('hari', '').capitalize(),
            'pasaran': weton_info.get('pasaran', '').capitalize(),
            'neptu': weton_info.get('neptu', 0),
            'wuku': weton_info.get('wuku', '').capitalize(),
            'keterangan': weton_meaning,
            'lintang_name': lintang_name,
            'lintang_desc': lintang_desc,
            'lintang_traits': lintang_traits,
            'wewaran_list': wewaran_list,
            'hari_desc': hari_desc,
            'pasaran_desc': pasaran_desc,
            'wuku_desc': wuku_desc,
            'page_title': 'Hasil Perhitungan Weton'
        }
        
        return render_template('weton_result.html', **context)
        
    except Exception as e:
        app.logger.error(f"Error in weton_result: {str(e)}", exc_info=True)
        flash('Terjadi kesalahan saat memproses permintaan Anda. Silakan coba lagi.', 'error')
        return redirect(url_for('weton_form'))

@app.route('/karma_result_legacy', methods=['GET', 'POST'])
def karma_result_legacy():
    if request.method == 'GET':
        return redirect(url_for('karma_form'))
    
    # Kode untuk menangani POST request karma
    name = request.form.get('name', '').strip()
    birth_date = request.form.get('birth_date', '').strip()
    
    # Validasi input
    if not all([name, birth_date]):
        flash('Mohon isi semua field yang diperlukan', 'error')
        return redirect(url_for('karma_form'))
    
    try:
        # Proses perhitungan karma di sini
        # ...
        
        # Contoh response sementara
        flash('Fitur perhitungan karma sedang dalam pengembangan', 'info')
        return redirect(url_for('karma_form'))
        
    except Exception as e:
        print(f"Error in karma_result: {str(e)}")
        flash('Terjadi kesalahan saat memproses permintaan Anda', 'error')
        return redirect(url_for('karma_form'))

@app.route('/rejeki_result_legacy', methods=['GET', 'POST'])
def rejeki_result_legacy():
    if request.method == 'GET':
        return redirect(url_for('rejeki_form'))
    
    # Kode untuk menangani POST request rejeki
    name = request.form.get('name', '').strip()
    birth_date = request.form.get('birth_date', '').strip()
    
    # Validasi input
    if not all([name, birth_date]):
        flash('Mohon isi semua field yang diperlukan', 'error')
        return redirect(url_for('rejeki_form'))
    
    try:
        # Proses perhitungan rejeki di sini
        # ...
        
        # Contoh response sementara
        flash('Fitur perhitungan rejeki sedang dalam pengembangan', 'info')
        return redirect(url_for('rejeki_form'))
        
    except Exception as e:
        print(f"Error in rejeki_result: {str(e)}")
        flash('Terjadi kesalahan saat memproses permintaan Anda', 'error')
        return redirect(url_for('rejeki_form'))

@app.route('/api/search_birthdates', methods=['POST'])
def api_search_birthdates():
    """Search dates within a given year that match selected Hari, Pasaran, and Wuku.
    Input JSON: { 'year': 2023, 'hari': 'Minggu', 'pasaran': 'Umanis'|'Legi'|'Pahing'|'Pon'|'Wage'|'Kliwon', 'wuku': 'Sinta'..'Watugunung' }
    Output JSON: { 'success': True, 'count': N, 'dates': [ {'iso': 'YYYY-MM-DD', 'display': 'DD - MMM - YYYY'} ] }
    Uses weton_calculation() which already adheres to the epoch 1633-07-08 and wuku_awal.xlsx calibration.
    """
    try:
        data = request.get_json(silent=True) or {}
        year = int(data.get('year', 0))
        hari_sel = str(data.get('hari', '')).strip()
        pasaran_sel = str(data.get('pasaran', '')).strip()
        wuku_sel = str(data.get('wuku', '')).strip()
        if year <= 0 or not hari_sel or not pasaran_sel or not wuku_sel:
            return jsonify({'success': False, 'error': 'Param year, hari, pasaran, dan wuku wajib diisi'}), 400

        # Iterate all days in the year
        start = datetime(year, 1, 1)
        end = datetime(year + 1, 1, 1)
        delta = (end - start).days
        results = []
        for i in range(delta):
            dt = start + pd.Timedelta(days=i)
            date_iso = dt.strftime('%Y-%m-%d')
            info = weton_calculation(date_iso)
            if not info:
                continue
            # Pasaran in our function may return 'Umanis' as alias for Legi; accept both user inputs
            hari_ok = str(info.get('hari', '')).strip() == hari_sel
            pasaran_ok = str(info.get('pasaran', '')).strip() == pasaran_sel or (
                pasaran_sel == 'Legi' and str(info.get('pasaran', '')).strip() == 'Umanis')
            wuku_ok = str(info.get('wuku', '')).strip() == wuku_sel
            if hari_ok and pasaran_ok and wuku_ok:
                results.append({
                    'iso': date_iso,
                    'display': dt.strftime('%d - %b - %Y') if hasattr(dt, 'strftime') else date_iso
                })
        return jsonify({'success': True, 'count': len(results), 'dates': results[:200]})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/wuku_names', methods=['GET'])
def api_wuku_names():
    try:
        names = get_wuku_names()
        return jsonify({'success': True, 'names': names})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'names': []}), 500

@app.route('/panggilan', methods=['GET', 'POST'])
def panggilan_form():
    # Simple form without FlaskForm; include CSRF token in template
    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        if not first_name or not last_name:
            flash('Mohon isi First name dan Last name', 'error')
            return redirect(url_for('panggilan_form'))
        # Persist to session for convenience
        session['panggilan_data'] = {'first_name': first_name, 'last_name': last_name}
        session.modified = True
        return redirect(url_for('panggilan_result'))
    # Always render empty inputs on GET (no prefill)
    return render_template('panggilan_form.html', first_name='', last_name='')

@app.route('/panggilan_result', methods=['GET'])
def panggilan_result():
    # Get names from session
    data = session.get('panggilan_data', {})
    first_name = data.get('first_name', '').strip()
    last_name = data.get('last_name', '').strip()
    if not first_name or not last_name:
        flash('Mohon isi data Nama Panggilan terlebih dahulu', 'error')
        return redirect(url_for('panggilan_form'))

    # Compute reduced numbers using existing harani_calculation
    try:
        f_num = int(harani_calculation(first_name).get('number', 0))
    except Exception:
        f_num = 0
    try:
        l_num = int(harani_calculation(last_name).get('number', 0))
    except Exception:
        l_num = 0

    # Compute combined number: sum then reduce, preserve master numbers 11,22
    def reduce_with_master(n: int) -> int:
        if n in (11, 22):
            return n
        # keep reducing until 1 digit or master 11/22
        while n > 9 and n not in (11, 22):
            n = sum(int(d) for d in str(n))
        return n
    combined_number = reduce_with_master(f_num + l_num)

    # Load explanations from DB (panggilan table)
    try:
        from db_access import get_panggilan
        row_c = get_panggilan(int(combined_number)) if combined_number else None
    except Exception:
        row_c = None
    desc_combined = (row_c or {}).get('deskripsi', '').strip()
    # Build paragraphs for combined description (split by blank line, fallback to newline, then sentences)
    desc_combined_paragraphs = []
    if desc_combined:
        try:
            text = str(desc_combined).replace('\r\n', '\n')
            parts = [p.strip() for p in text.split('\n\n') if p.strip()]
            if len(parts) <= 1:
                parts = [p.strip() for p in text.split('\n') if p.strip()]
            if len(parts) <= 1:
                import re as _re
                sentences = [_s.strip() for _s in _re.findall(r'[^.!?\n]+[.!?]?', text) if _s.strip()]
                if sentences:
                    parts = sentences
            desc_combined_paragraphs = parts
        except Exception:
            desc_combined_paragraphs = []
    
    return render_template('panggilan_result.html',
                           first_name=first_name,
                           last_name=last_name,
                           combined_number=combined_number,
                           desc_combined=desc_combined,
                           desc_combined_paragraphs=desc_combined_paragraphs)

@app.route('/results')
def show_results():
    # Pastikan data user ada di session
    if 'form_data' not in session:
        flash('Silakan isi data terlebih dahulu', 'error')
        return redirect(url_for('input_data'))
    
    user_data = session['form_data']
    
    try:
        # Format tanggal lahir
        formatted_date = datetime.strptime(user_data['birth_date'], '%Y-%m-%d').strftime('%d/%m/%Y')
        
        # Hitung semua jenis numerologi
        results = {}
        
        # 1. Hitung Life Path
        life_path_info = calculate_life_path(formatted_date)
        if life_path_info:
            life_path_number = life_path_info.get('life_path')
            life_path_data = get_life_path_details(life_path_number)
            if life_path_data:
                results['life_path'] = {
                    'number': life_path_number,
                    'meaning': life_path_data.get('deskripsi', ''),
                    'strengths': life_path_data.get('kekuatan', []),
                    'challenges': life_path_data.get('tantangan', []),
                    'additional_info': life_path_data.get('detail', '')
                }
        
        # 2. Hitung Weton
        # TODO: Implementasi perhitungan weton
        
        # 3. Hitung Harani
        # TODO: Implementasi perhitungan harani
        
        # 4. Hitung Karma
        # TODO: Implementasi perhitungan karma
        
        # 5. Hitung Rejeki
        # TODO: Implementasi perhitungan rejeki
        
        # 6. Hitung Arah
        # TODO: Implementasi perhitungan arah
        
        return render_template('results.html', 
                             name=user_data['name'],
                             birth_date=formatted_date,
                             results=results)
        
    except Exception as e:
        print(f"Error in show_results: {str(e)}")
        flash('Terjadi kesalahan saat memproses data Anda', 'error')
        return redirect(url_for('input_data'))

@app.route('/input', methods=['GET', 'POST'])
@login_required
@csrf.exempt  # Temporarily disable CSRF for this route
@csrf.exempt  # Temporarily disable CSRF for this route
def input_data():
    guard = _enforce_role('admin')
    if guard:
        return guard
    if request.method == 'POST':
        try:
            # Get and validate form data
            name = request.form.get('name', '').strip()
            birth_date = request.form.get('birth_date', '').strip()
            
            if not name or not birth_date:
                flash('Mohon isi semua field yang diperlukan', 'error')
                return render_template('input_form.html')
            
            # Clear existing session data first
            session.clear()
            
            # Store new data in session
            session['form_data'] = {
                'name': name,
                'birth_date': birth_date
            }
            
            # Ensure session is saved
            session.permanent = True
            session.modified = True
            
            # Generate a new CSRF token for the next request
            csrf_token = generate_csrf()
            
            # Debug: Print session data
            logger.info(f"Session data saved: {session['form_data']}")
            
            # Redirect to calculation options page with a success message
            flash('Data berhasil disimpan', 'success')
            return redirect(url_for('calculation_options'))
            
        except Exception as e:
            logger.error(f"Error in input_data: {str(e)}\n{traceback.format_exc()}")
            flash('Terjadi kesalahan saat memproses data Anda', 'error')
            return render_template('input_form.html'), 400
    
    # For GET requests, show the form
    # CSRF token is automatically available in the template via csrf_token()
    return render_template('input_form.html')

@app.route('/calculation-options', methods=['GET'])
def calculation_options():
    """Display all available calculation options."""
    # Check if we have valid form data
    if 'form_data' not in session or not session['form_data']:
        flash('Silakan isi data terlebih dahulu', 'error')
        return redirect(url_for('input_data'))
    
    form_data = session['form_data']
    name = form_data.get('name', '')
    birth_date = form_data.get('birth_date', '')
    
    # Validate the data
    if not name or not birth_date:
        flash('Data tidak valid, silakan isi ulang', 'error')
        return redirect(url_for('input_data'))
    
    # Debug: Print current session data
    print("Current session data in calculation_options:", form_data)
    
    return render_template('calculation_options.html', 
                         name=name,
                         birth_date=birth_date)

@app.route('/life_path_result', methods=['GET'])
@login_required
def life_path_result():
    """Render Life Path result page using session form data and Excel-backed details."""
    try:
        # Ensure form data exists
        if 'form_data' not in session or not session['form_data']:
            flash('Silakan isi data terlebih dahulu', 'error')
            return redirect(url_for('input_data'))
        
        name = session['form_data'].get('name', '').strip()
        birth_date = session['form_data'].get('birth_date', '').strip()
        if not name or not birth_date:
            flash('Data tidak valid, silakan isi ulang', 'error')
            return redirect(url_for('input_data'))
        
        # Normalize birth date for display and ISO for calc
        from datetime import datetime
        birth_date_disp = birth_date
        birth_date_iso = birth_date
        try:
            dt = datetime.strptime(birth_date, '%Y-%m-%d')
            birth_date_disp = dt.strftime('%d/%m/%Y')
        except ValueError:
            try:
                dt = datetime.strptime(birth_date, '%d/%m/%Y')
                birth_date_iso = dt.strftime('%Y-%m-%d')
            except ValueError:
                flash('Format tanggal tidak valid. Gunakan DD/MM/YYYY atau YYYY-MM-DD', 'error')
                return redirect(url_for('input_data'))
        
        # Calculate life path
        lp_info = life_path_calculation(birth_date_iso)
        lp_number = lp_info.get('life_path')
        details = get_life_path_details(lp_number)
        
        # Load Excel-based meanings for Life Path (if available)
        lp_deskripsi = ''
        lp_detail = ''
        lp_kekuatan = []
        lp_tantangan = []
        lp_penjelasan = ''
        lp_detail_paragraphs = []
        c4_value = None
        c4_explanation = ''
        c4_paragraphs = []
        import re
        try:
            excel_path = os.path.join(os.path.dirname(__file__), 'life_path.xlsx')
            if os.path.exists(excel_path):
                df_lp = pd.read_excel(excel_path)
                # Normalize column names
                cols = {str(c).strip().lower(): c for c in df_lp.columns}
                col_no = cols.get('no')
                col_desc = cols.get('deskripsi')
                col_detail = cols.get('detail')
                col_kekuatan = cols.get('kekuatan')
                col_tantangan = cols.get('tantangan')
                col_penjelasan = (
                    cols.get('penjelasan') or cols.get('penjelasa') or cols.get('penjelasan (html)') or cols.get('penjelasan_html') or cols.get('penjelasanhtml')
                )
                if col_no:
                    try:
                        df_lp[col_no] = pd.to_numeric(df_lp[col_no], errors='coerce').astype('Int64')
                    except Exception:
                        pass
                    row = df_lp.loc[df_lp[col_no] == lp_number]
                    if not row.empty:
                        r0 = row.iloc[0]
                        def clean(v):
                            try:
                                return '' if v is None or (isinstance(v, float) and pd.isna(v)) else str(v).strip()
                            except Exception:
                                return str(v).strip() if v is not None else ''
                        lp_deskripsi = clean(r0.get(col_desc)) if col_desc else ''
                        lp_detail = clean(r0.get(col_detail)) if col_detail else ''
                        raw_kekuatan = clean(r0.get(col_kekuatan)) if col_kekuatan else ''
                        raw_tantangan = clean(r0.get(col_tantangan)) if col_tantangan else ''
                        lp_penjelasan = clean(r0.get(col_penjelasan)) if col_penjelasan else ''
                        def to_sentences(text: str):
                            if not text:
                                return []
                            t = text.replace('\r\n', '\n').strip()
                            parts = [seg.strip() for seg in re.findall(r'[^.!?\n]+[.!?]?', t) if seg and seg.strip()]
                            if len(parts) <= 1 and ('\n' in t):
                                parts = [seg.strip() for seg in t.split('\n') if seg.strip()]
                            return parts
                        if raw_kekuatan:
                            lp_kekuatan = to_sentences(raw_kekuatan)
                        if raw_tantangan:
                            lp_tantangan = to_sentences(raw_tantangan)
        
        except Exception as e:
            app.logger.warning(f"Failed to load life_path.xlsx: {e}")
        
        # Optional: C4 challenge integration if available
        try:
            challenges = compute_challenges(birth_date_iso)
            challenge_numbers = challenges.get('numbers', [])
            if len(challenge_numbers) >= 4:
                c4_value = challenge_numbers[3]
                # Fetch Tantangan explanation from DB
                try:
                    c4_explanation = get_tantangan_by_kode(int(c4_value)) or ''
                    if c4_explanation:
                        text = c4_explanation.replace('\r\n', '\n')
                        parts = [p.strip() for p in text.split('\n\n') if p.strip()]
                        if len(parts) <= 1:
                            parts = [p.strip() for p in text.split('\n') if p.strip()]
                        c4_paragraphs = parts
                except Exception:
                    pass
        except Exception:
            pass
        
        # Load Hari Lahir explanation from DB based on day (DD)
        birth_day = dt.day
        try:
            hari_lahir_text = get_hari_lahir(int(birth_day)) or ''
            # Temporary debug log to verify DB value flows to template
            try:
                _prev = hari_lahir_text.replace('\n', ' ')[:120]
            except Exception:
                _prev = ''
            app.logger.info(f"Hari Lahir DB fetch: day={birth_day}, len={len(hari_lahir_text)} preview='{_prev}'")
        except Exception as _e:
            app.logger.warning(f"Failed to load Hari Lahir from DB: {_e}")
            hari_lahir_text = ''

        context = {
            'name': name,
            'birth_date': birth_date_disp,
            'life_path': lp_info,
            'life_path_number': lp_number,
            'details': details,
            'lp_deskripsi': lp_deskripsi,
            'lp_detail': lp_detail,
            'lp_detail_paragraphs': lp_detail_paragraphs,
            'lp_kekuatan': lp_kekuatan,
            'lp_tantangan': lp_tantangan,
            'lp_penjelasan': lp_penjelasan,
            'c4_value': c4_value,
            'c4_explanation': c4_explanation,
            'c4_paragraphs': c4_paragraphs,
            'birth_day': birth_day,
            'hari_lahir': hari_lahir_text,
        }
        
        return render_template('result_life_path.html', **context)
        
    except Exception as e:
        app.logger.error(f"Error in life_path_result: {str(e)}")
        traceback.print_exc()
        flash('Terjadi kesalahan saat menampilkan Life Path', 'error')
        return redirect(url_for('calculation_options'))

@app.route('/hutang-karma')
@login_required
def hutang_karma_result():
    guard = _enforce_role('gold')
    if guard:
        return guard
    """Handle Hutang Karma calculation and display results."""
    try:
        if 'form_data' not in session or not session['form_data']:
            flash('Silakan isi data terlebih dahulu', 'error')
            return redirect(url_for('input_data'))
        
        # Dapatkan data dari session
        name = session['form_data'].get('name', '')
        birth_date = session['form_data'].get('birth_date', '')
        
        # Hitung Hutang Karma
        from numerology_utils import calculate_hutang_karma
        result = calculate_hutang_karma(birth_date, name)
        
        # Debug: Print result untuk memeriksa struktur data
        print("Hutang Karma Result:", result)
        
        # Pastikan tidak ada error
        if 'error' in result:
            flash(f'Error: {result["error"]}', 'error')
            return redirect(url_for('calculation_options'))
        
        # Render template dengan hasil
        return render_template('hutang_karma_result.html', 
                             name=name,
                             birth_date=birth_date,
                             karma_number=result.get('karma_number', 0),
                             karma_description=result.get('karma_description', ''),
                             karma_meaning=result.get('karma_meaning', ''),
                             karma_lesson=result.get('karma_lesson', ''),
                             karma_advice=result.get('karma_advice', ''),
                             life_path=result.get('life_path', 0),
                             name_number=result.get('name_number', 0),
                             life_path_karmic_debt=result.get('life_path_karmic_debt', {}),
                             karmic_debt_description=result.get('karmic_debt_description', ''),
                             name_number_karmic_debt=result.get('name_number_karmic_debt', {}),
                             name_karmic_debt_description=result.get('name_karmic_debt_description', ''),
                             calculation=result.get('calculation', {}))
        
    except Exception as e:
        print(f"Error in hutang_karma_result: {str(e)}")
        traceback.print_exc()
        flash('Terjadi kesalahan saat menghitung Hutang Karma', 'error')
        return redirect(url_for('calculation_options'))

@app.route('/bridge')
@login_required
def bridge_result():
    guard = _enforce_role('gold')
    if guard:
        return guard
    """Handle Bridge calculation and display results.

    Aturan:
    - Bridge = selisih absolut antara Life Path dan Harani/Name Number.
    - Jika 5 <= Bridge < 8, tampilkan kombinasi (life_path-name_number) sebagai bridge_number.
    - Deskripsi, makna, tantangan, saran diambil dari bridge_number.xlsx.
    """
    try:
        if 'form_data' not in session or not session['form_data']:
            flash('Silakan isi data terlebih dahulu', 'error')
            return redirect(url_for('input_data'))

        # Dapatkan data dari session
        name = session['form_data'].get('name', '')
        birth_date = session['form_data'].get('birth_date', '')

        # Hitung Life Path Number
        from numerology_utils import life_path_calculation, calculate_bridge
        life_path_info = life_path_calculation(birth_date)
        life_path_number = life_path_info.get('life_path')

        # Hitung Name Number menggunakan Harani calculation (konsisten dengan harani_result)
        from numerology_utils import harani_calculation
        harani_info = harani_calculation(name)
        name_number = harani_info.get('number', 0)

        # Hitung Bridge (dan ambil deskripsi dari Excel)
        bres = calculate_bridge(life_path_number, name_number)

        bridge_number = bres.get('bridge_number', '')
        # Try mapping to user-friendly label via DB table bridge_name (bgride -> deskripsi)
        try:
            bridge_label = get_bridge_name(str(bridge_number)) or ''
        except Exception:
            bridge_label = ''
        bridge_description = bres.get('bridge_description', '')
        bridge_meaning = bres.get('bridge_meaning', '')
        bridge_challenge = bres.get('bridge_challenge', '')
        bridge_advice = bres.get('bridge_advice', '')

        # Opsional: meaning untuk Life Path dan Name (biarkan kosong jika tidak ada sumber)
        life_path_meaning = ''
        name_meaning = ''

        # Render template dengan hasil
        return render_template(
            'bridge_result.html',
            name=name,
            birth_date=birth_date,
            life_path_number=life_path_number,
            name_number=name_number,
            bridge_number=bridge_number,
            bridge_label=bridge_label,
            bridge_description=bridge_description,
            bridge_meaning=bridge_meaning,
            bridge_challenge=bridge_challenge,
            bridge_advice=bridge_advice,
            life_path_meaning=life_path_meaning,
            name_meaning=name_meaning,
        )

    except Exception as e:
        print(f"Error in bridge_result: {str(e)}")
        traceback.print_exc()
        flash('Terjadi kesalahan saat menghitung Bridge', 'error')
        return redirect(url_for('calculation_options'))

@app.route('/tenung')
@login_required
def tenung_result():
    guard = _enforce_role('gold')
    if guard:
        return guard
    """Handle Tenung calculation (berdasarkan nama) dan tampilkan hasil.

    Aturan: menggunakan perhitungan Harani dari nama, kemudian memetakan hasilnya ke tenung_nama database.
    """
    try:
        if 'form_data' not in session or not session['form_data']:
            flash('Silakan isi data terlebih dahulu', 'error')
            return redirect(url_for('input_data'))

        # Dapatkan data dari session
        name = session['form_data'].get('name', '')
        birth_date = session['form_data'].get('birth_date', '')

        # Hitung Tenung menggunakan perhitungan Harani dari nama
        from numerology_utils import harani_calculation, karakter_calculation, prediksi_calculation, tenung_karma_calculation
        from db_access import get_tenung_deskripsi, get_tenung_lahir, get_prediksi_by_kondisi, get_tenung_karma
        
        harani_result = harani_calculation(name)
        tenung_number = harani_result.get('number', 0)
        
        # Ambil deskripsi dari DB berdasarkan angka Harani
        try:
            tenung_desc = get_tenung_deskripsi(int(tenung_number)) or ''
        except Exception:
            tenung_desc = ''
        
        # Fallback jika tidak ada deskripsi di DB
        if not tenung_desc:
            tenung_desc = f'Tenung angka {tenung_number} - deskripsi belum tersedia di database.'
        
        # Calculate Karakter from birth date
        karakter_info = karakter_calculation(birth_date)
        karakter_o_desc = None
        karakter_mn_desc = None
        
        if 'error' not in karakter_info:
            # Get descriptions from database
            try:
                o_key = karakter_info['mapping_keys']['O_key']
                mn_key = karakter_info['mapping_keys']['MN_key']
                
                karakter_o_desc = get_tenung_lahir(o_key)
                karakter_mn_desc = get_tenung_lahir(mn_key)
            except Exception as e:
                print(f'Karakter DB error: {e}')
            
            # Provide fallback descriptions
            if not karakter_o_desc:
                karakter_o_desc = f'Deskripsi untuk Root Number {karakter_info["core"]["O_reduced"]} belum tersedia.'
            if not karakter_mn_desc:
                karakter_mn_desc = f'Deskripsi untuk kombinasi M&N {karakter_info["mapping_keys"]["MN_key"]} belum tersedia.'
        
        # Calculate Predictions from birth date
        prediksi_info = prediksi_calculation(birth_date)
        prediksi_results = []
        
        if 'error' not in prediksi_info and prediksi_info.get('matched_conditions'):
            # Get descriptions for each matched condition
            for condition in prediksi_info['matched_conditions']:
                try:
                    makna = get_prediksi_by_kondisi(condition)
                    if makna:
                        prediksi_results.append({
                            'kondisi': condition,
                            'makna': makna
                        })
                except Exception as e:
                    print(f'Prediksi condition {condition} error: {e}')

        # Calculate Tenung Karma from birth date
        tenung_karma_info = tenung_karma_calculation(birth_date)
        tenung_karma_data = None
        
        if 'error' not in tenung_karma_info:
            # Get description from database
            try:
                karma_id = tenung_karma_info['mapping_key']
                tenung_karma_data = get_tenung_karma(karma_id)
                
                # Add calculation details to karma data
                if tenung_karma_data:
                    tenung_karma_data.update({
                        'N': tenung_karma_info['N'],
                        'DL': tenung_karma_info['DL'],
                        'D': tenung_karma_info['D'],
                        'combination': tenung_karma_info['karma_combination']
                    })
            except Exception as e:
                print(f'Tenung Karma DB error: {e}')
        
        # Provide fallback if no karma data found
        if not tenung_karma_data:
            tenung_karma_data = {
                'N': tenung_karma_info.get('N', 0),
                'DL': tenung_karma_info.get('DL', 0), 
                'D': tenung_karma_info.get('D', 0),
                'combination': tenung_karma_info.get('karma_combination', '0-0-0'),
                'arti': 'Tidak Ada Hutang Karma',
                'deskripsi': 'Anda terlihat tidak memiliki Hutang Karma Masa Lalu'
            }

        # Nilai lain untuk template (fallback aman)
        life_path_number = tenung_number
        life_path_meaning = tenung_desc
        current_year = datetime.now().year

        # Opsional: struktur tambahan untuk bagian lain template agar tidak error
        year_theme = ''
        year_positive = []
        year_challenges = []
        life_purpose = ''
        life_lesson = ''
        life_advice = []
        
        # Render Tenung result page
        return render_template(
            'tenung_result.html',
            name=name,
            birth_date=birth_date,
            tenung_number=tenung_number,
            tenung_description=tenung_desc,
            current_year=current_year,
            year_theme=year_theme,
            year_positive=year_positive,
            year_challenges=year_challenges,
            life_purpose=life_purpose,
            life_lesson=life_lesson,
            life_advice=life_advice,
            karakter_info=karakter_info,
            karakter_o_desc=karakter_o_desc,
            karakter_mn_desc=karakter_mn_desc,
            prediksi_info=prediksi_info,
            prediksi_results=prediksi_results,
            tenung_karma_data=tenung_karma_data,
        )

    except Exception as e:
        print(f"Error in tenung_result: {str(e)}")
        traceback.print_exc()
        flash('Terjadi kesalahan saat menghitung Tenung', 'error')
        return redirect(url_for('calculation_options'))

@app.route('/weton', methods=['GET'])
def weton_form():
    """Display the Weton input form page."""
    try:
        form = WetonForm()
        return render_template('weton_form.html', form=form)
    except Exception:
        form = None
        return render_template('weton_form.html', form=form)

@app.route('/chaldean_result')
@login_required
def chaldean_result():
    guard = _enforce_role('gold')
    if guard:
        return guard
    """Display Chaldean numerology calculation results"""
    logger.info("Chaldean result accessed")
    
    # Check if we have form data in session
    if 'form_data' not in session or not session['form_data']:
        q_name = request.args.get('name', '').strip()
        q_birth = request.args.get('birth_date', '').strip()
        if q_name and q_birth:
            session['form_data'] = {'name': q_name, 'birth_date': q_birth}
            session.modified = True
            logger.info("Rebuilt session form_data from query params for chaldean_result")
        else:
            logger.warning("No form data in session and no query params provided; redirecting to calculation_options")
            flash('Data sesi tidak ditemukan. Silakan kembali ke menu utama dan klik Harani lagi.', 'info')
            return redirect(url_for('calculation_options'))
    
    try:
        form_data = session['form_data']
        name = form_data.get('name', '').strip()
        birth_date = form_data.get('birth_date', '').strip()
        
        if not name:
            logger.warning("No name in form data")
            flash('Nama tidak ditemukan di sesi. Silakan isi form lagi.', 'warning')
            return redirect(url_for('calculation_options'))
        
        # Normalize name for display
        try:
            decoded_name = urllib.parse.unquote_plus(name) if name else ''
            normalized_name = ' '.join(decoded_name.replace('+', ' ').split()) if decoded_name else ''
        except Exception as e:
            logger.warning(f"Error decoding name: {str(e)}")
            normalized_name = name
        
        # Parse birth date for display
        try:
            dt = None
            for fmt in ('%d/%m/%Y', '%m/%d/%Y', '%Y-%m-%d', '%d-%m-%Y', '%m-%d-%Y'):
                try:
                    dt = datetime.strptime(birth_date, fmt)
                    break
                except ValueError:
                    continue
            
            if not dt:
                dt = datetime.now()
                logger.warning("Could not parse birth date, using current date")
            
            formatted_birth_date = dt.strftime('%d/%m/%Y')
        except Exception as e:
            logger.warning(f"Error parsing birth date: {str(e)}")
            formatted_birth_date = birth_date
        
        # Calculate Chaldean numerology
        logger.info(f"Calculating Chaldean for name: {normalized_name}")
        chaldean_data = chaldean_calculation(normalized_name)
        
        logger.info(f"Rendering chaldean.html for {normalized_name}")
        return render_template('chaldean.html',
                             name=normalized_name,
                             birth_date=formatted_birth_date,
                             chaldean_data=chaldean_data)
        
    except Exception as e:
        error_msg = f"Terjadi kesalahan tak terduga: {str(e)}"
        logger.error(f"Error in chaldean_result: {error_msg}\n{traceback.format_exc()}")
        flash(error_msg, 'error')
        
        # Create a default result with error information
        chaldean_data = {
            'number': 0,
            'description': 'Terjadi kesalahan saat menghitung Chaldean. Silakan coba lagi atau hubungi dukungan.',
            'steps': [],
            'letter_values': {}
        }
        
        return render_template('chaldean.html',
                             name=normalized_name if 'normalized_name' in locals() else '',
                             birth_date=formatted_birth_date if 'formatted_birth_date' in locals() else '',
                             chaldean_data=chaldean_data)

@app.route('/birth_chart')
@login_required
def birth_chart_result():
    try:
        # Ensure session form data exists, allow admin/url prefill
        if 'form_data' not in session or not session['form_data']:
            q_name = request.args.get('name', '').strip()
            q_birth = request.args.get('birth_date', '').strip()
            if q_name and q_birth:
                session['form_data'] = {'name': q_name, 'birth_date': q_birth}
                session.modified = True
            else:
                flash('Silakan isi data terlebih dahulu', 'error')
                return redirect(url_for('input_data'))
        name = session['form_data'].get('name', '')
        birth_date = session['form_data'].get('birth_date', '')
        # Calculate birth chart from birth date
        from numerology_utils import birth_chart_calculation
        bc = birth_chart_calculation(birth_date)
        # Build descriptions by digit string (e.g., '111','66','9','2')
        birth_chart_digit_desc = {}
        try:
            from db_access import get_birth_chart_desc as _get_bc_desc
            strings = bc.get('strings') or {}
            present = [
                strings.get('mind_self_str',''), strings.get('mind_community_str',''), strings.get('mind_world_str',''),
                strings.get('soul_self_str',''), strings.get('soul_community_str',''), strings.get('soul_world_str',''),
                strings.get('body_self_str',''), strings.get('body_community_str',''), strings.get('body_world_str',''),
            ]
            for s in set(filter(None, present)):
                birth_chart_digit_desc[s] = _get_bc_desc(s)
        except Exception:
            pass
        # Compute empty box combinations and fetch descriptions from DB
        empty_keys = []
        try:
            s = bc.get('strings') or {}
            mapping = {
                'mind_self': s.get('mind_self_str') or '',
                'mind_community': s.get('mind_community_str') or '',
                'mind_world': s.get('mind_world_str') or '',
                'soul_self': s.get('soul_self_str') or '',
                'soul_community': s.get('soul_community_str') or '',
                'soul_world': s.get('soul_world_str') or '',
                'body_self': s.get('body_self_str') or '',
                'body_community': s.get('body_community_str') or '',
                'body_world': s.get('body_world_str') or '',
            }
            empty_keys = [k for k, v in mapping.items() if not (v or '').strip()]
        except Exception:
            empty_keys = []
        birth_chart_empty_info = {}
        try:
            from db_access import get_birth_chart_empty_combo_desc
            birth_chart_empty_info = get_birth_chart_empty_combo_desc(empty_keys)
        except Exception:
            birth_chart_empty_info = {'combined': None, 'entries': []}

        return render_template(
            'birth_chart.html',
            name=name,
            birth_date=birth_date,
            birth_chart=bc.get('chart'),
            birth_chart_strings=bc.get('strings'),
            birth_chart_totals=bc.get('totals'),
            birth_chart_desc=bc.get('descriptions'),
            birth_chart_digit_desc=birth_chart_digit_desc,
            birth_chart_error=bc.get('error'),
            birth_chart_empty_info=birth_chart_empty_info,
        )
    except Exception as e:
        app.logger.error(f"Error in birth_chart_result: {e}")
        flash('Terjadi kesalahan saat membuka Birth Chart', 'error')
        return redirect(url_for('calculation_options'))

@app.route('/arrow_sukses')
@login_required
def arrow_sukses_result():
    try:
        if 'form_data' not in session or not session['form_data']:
            q_name = request.args.get('name', '').strip()
            q_birth = request.args.get('birth_date', '').strip()
            if q_name and q_birth:
                session['form_data'] = {'name': q_name, 'birth_date': q_birth}
                session.modified = True
            else:
                flash('Silakan isi data terlebih dahulu', 'error')
                return redirect(url_for('input_data'))
        name = session['form_data'].get('name', '')
        birth_date = session['form_data'].get('birth_date', '')
        # Calculate birth chart grid and detect arrows
        from numerology_utils import detect_arrows_from_birth_date
        arrows = detect_arrows_from_birth_date(birth_date)
        grid_strings = arrows.get('strings')
        grid_totals = arrows.get('totals')
        arrows_present_ids = arrows.get('arrows_present', [])
        arrows_absent_ids = arrows.get('arrows_absent', [])

        # Fetch descriptions for arrows
        from db_access import get_arrow_individual
        present_desc = []
        for aid in arrows_present_ids:
            row = get_arrow_individual(aid)
            if row:
                present_desc.append({**row, 'id': aid})
        absent_desc = []
        for aid in arrows_absent_ids:
            row = get_arrow_individual(aid)
            if row:
                absent_desc.append({**row, 'id': aid})

        return render_template(
            'arrow_sukses.html',
            name=name,
            birth_date=birth_date,
            birth_chart_strings=grid_strings,
            birth_chart_totals=grid_totals,
            arrows_present=present_desc,
            arrows_absent=absent_desc,
        )
    except Exception as e:
        app.logger.error(f"Error in arrow_sukses_result: {e}")
        flash('Terjadi kesalahan saat membuka Arrow Sukses', 'error')
        return redirect(url_for('calculation_options'))

@app.route('/name_number', methods=['GET', 'POST'])
@login_required
def name_number_result():
    try:
        if 'form_data' not in session or not session['form_data']:
            q_name = request.args.get('name', '').strip()
            q_birth = request.args.get('birth_date', '').strip()
            if q_name and q_birth:
                session['form_data'] = {'name': q_name, 'birth_date': q_birth}
                session.modified = True
            else:
                flash('Silakan isi data terlebih dahulu', 'error')
                return redirect(url_for('input_data'))

        base_name = session['form_data'].get('name', '')
        birth_date = session['form_data'].get('birth_date', '')

        nickname = session.get('nickname', '')
        soul_urge_number = None
        soul_urge_desc = None
        outer_expression_number = None
        outer_expression_desc = None

        if request.method == 'POST':
            nickname = (request.form.get('nickname') or '').strip()
            if nickname:
                try:
                    session['nickname'] = nickname
                    session.modified = True
                except Exception:
                    pass
                try:
                    su_info = heart_desire_calculation(nickname)
                    su_num = int(su_info.get('number') or 0)
                    while su_num > 9:
                        su_num = sum(int(d) for d in str(su_num))
                    soul_urge_number = su_num if su_num >= 1 else None
                    if soul_urge_number:
                        soul_urge_desc = get_soul_urge(soul_urge_number)
                except Exception as e:
                    app.logger.warning(f"Soul Urge calc error: {e}")

                try:
                    pe_info = personality_calculation(nickname)
                    pe_num = int(pe_info.get('number') or 0)
                    while pe_num > 9:
                        pe_num = sum(int(d) for d in str(pe_num))
                    outer_expression_number = pe_num if pe_num >= 1 else None
                    if outer_expression_number:
                        outer_expression_desc = get_outer_expression(outer_expression_number)
                except Exception as e:
                    app.logger.warning(f"Outer Expression calc error: {e}")
            else:
                flash('Masukkan satu nama panggilan yang Anda gunakan sehari-hari', 'info')

        return render_template(
            'name_number.html',
            name=base_name,
            birth_date=birth_date,
            nickname=nickname,
            soul_urge_number=soul_urge_number,
            soul_urge_desc=soul_urge_desc,
            outer_expression_number=outer_expression_number,
            outer_expression_desc=outer_expression_desc,
        )
    except Exception as e:
        app.logger.error(f"Error in name_number_result: {e}")
        flash('Terjadi kesalahan saat membuka Name Number', 'error')
        return redirect(url_for('calculation_options'))

@app.route('/debug/wewaran')
def debug_wewaran():
    """Debug endpoint to check wewaran calculations"""
    return render_template('debug_wewaran.html')

if __name__ == '__main__':
    app.secret_key = os.environ.get('SECRET_KEY') or 'your-secure-secret-key-here'
    port = int(os.environ.get('PORT', 5003))  # Default to 5003 if PORT not set
    print(f"Starting server on port {port}...")
    app.run(host='127.0.0.1', port=port, debug=True, use_reloader=True)
