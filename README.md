# Numerulogi - Aplikasi Web Pemroses Excel

Aplikasi web berbasis Python (Flask) untuk mengunggah, melihat, dan menganalisis data dari file Excel dengan antarmuka yang modern dan responsif menggunakan Tailwind CSS.

## 🚀 Fitur Utama

- 🌐 Antarmuka web yang modern dan responsif
- 📤 Unggah file Excel (.xlsx, .xls)
- 📊 Tampilkan data dalam tabel interaktif
- 🔍 Pencarian dan filter data
- 📥 Ekspor data (dalam pengembangan)
- 📱 Responsif di berbagai perangkat

## 🛠️ Teknologi yang Digunakan

- **Backend**: Python 3.7+
- **Web Framework**: Flask
- **Frontend**: HTML5, Tailwind CSS, JavaScript
- **Pengolahan Data**: Pandas, OpenPyXL
- **Development**: Gunicorn (untuk production)

## 🚀 Cara Menjalankan

### 1. Persyaratan Sistem
- Python 3.7 atau lebih baru
- pip (package manager Python)

### 2. Instalasi

1. Clone repository ini:
```bash
git clone [URL_REPOSITORY]
cd numerulogi
```

2. Buat dan aktifkan virtual environment (disarankan):
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# atau
# .\venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Menjalankan Aplikasi

#### Mode Pengembangan
```bash
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```

Atau langsung:
```bash
python app.py
```

#### Mode Produksi (dengan Gunicorn)
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Buka browser dan kunjungi: http://localhost:5000

## 📂 Struktur Proyek

```
numerulogi/
├── app.py                # Aplikasi utama Flask
├── requirements.txt      # Daftar dependensi
├── uploads/              # Folder untuk menyimpan file yang diunggah
│   └── ...
├── static/               # File statis (CSS, JS, gambar)
│   ├── css/
│   │   └── style.css    # File CSS kustom
│   └── js/
│       └── main.js      # JavaScript kustom
├── templates/            # Template HTML
│   ├── base.html        # Template dasar
│   └── index.html       # Halaman utama
└── README.md            # Dokumentasi ini
```

## 🎨 Tampilan

### Halaman Utama
- Area drag & drop untuk mengunggah file Excel
- Tampilan data dalam tabel yang dapat diurutkan
- Pencarian instan
- Tampilan responsif

## 🛠️ Pengembangan

### Menambahkan Fitur Baru
1. Buat branch baru: `git checkout -b fitur-baru`
2. Lakukan perubahan yang diperlukan
3. Commit perubahan: `git commit -am 'Menambahkan fitur baru'`
4. Push ke branch: `git push origin fitur-baru`
5. Buat Pull Request

### Variabel Lingkungan
Buat file `.env` di direktori root dengan konten:
```
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=10485760  # 10MB
```

## 📝 Lisensi

Proyek ini dilisensikan di bawah MIT License - lihat file [LICENSE](LICENSE) untuk detailnya.

## 🙏 Terima Kasih

Terima kasih telah menggunakan Numerulogi! Jika Anda menemukan bug atau memiliki saran, silakan buat issue baru.
# numerologi
