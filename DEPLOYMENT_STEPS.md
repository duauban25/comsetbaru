# Panduan Deployment Numerology ke VPS (Ubuntu 24.04 LTS)

## Status Saat Ini
- ✅ Project sudah di-upload ke GitHub: `https://github.com/duauban25/numerologi`
- ✅ File konfigurasi deployment sudah siap
- ⏳ Menunggu deployment ke VPS

---

## LANGKAH 1: Persiapan VPS

### 1.1 Login ke VPS
```bash
ssh username@IP_VPS
```

### 1.2 Update sistem
```bash
sudo apt update
sudo apt upgrade -y
```

### 1.3 Install paket yang dibutuhkan
```bash
sudo apt install -y python3 python3-venv python3-pip build-essential python3-dev nginx git ufw curl sqlite3
```

---

## LANGKAH 2: Konfigurasi Firewall

### 2.1 Izinkan SSH dan Nginx
```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw --force enable
sudo ufw status
```

---

## LANGKAH 3: Clone Repository

### 3.1 Buat folder aplikasi
```bash
sudo mkdir -p /var/www/numerology
sudo chown -R $USER:$USER /var/www/numerology
```

### 3.2 Clone dari GitHub
```bash
cd /var/www/numerology
git clone https://github.com/duauban25/numerologi.git .
```

---

## LANGKAH 4: Setup Python Environment

### 4.1 Buat virtual environment
```bash
python3 -m venv venv
```

### 4.2 Install dependencies
```bash
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### 4.3 Test import aplikasi
```bash
venv/bin/python -c "from app import app; print('Import berhasil')"
```

---

## LANGKAH 5: Setup Folder dan Permission

### 5.1 Buat folder uploads
```bash
mkdir -p /var/www/numerology/uploads
```

### 5.2 Set permission uploads
```bash
sudo chown -R www-data:www-data /var/www/numerology/uploads
```

### 5.3 Set permission database (jika ada)
```bash
sudo chown www-data:www-data /var/www/numerology/app.db || true
```

---

## LANGKAH 6: Setup Environment Variables

### 6.1 Buat file .env
```bash
sudo nano /var/www/numerology/.env
```

### 6.2 Generate SECRET_KEY
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 6.3 Isi file .env
```bash
SECRET_KEY=paste_hasil_generate_di_sini
```

### 6.4 Set permission .env
```bash
sudo chown www-data:www-data /var/www/numerology/.env
sudo chmod 600 /var/www/numerology/.env
```

---

## LANGKAH 7: Setup Systemd Service (Gunicorn)

### 7.1 Copy file service
```bash
sudo cp /var/www/numerology/numerology.service /etc/systemd/system/numerology.service
```

### 7.2 Reload dan enable service
```bash
sudo systemctl daemon-reload
sudo systemctl enable numerology
sudo systemctl start numerology
```

### 7.3 Cek status service
```bash
sudo systemctl status numerology
```

### 7.4 Cek log (jika ada error)
```bash
sudo journalctl -u numerology -n 50 --no-pager
```

---

## LANGKAH 8: Setup Nginx

### 8.1 Copy file konfigurasi Nginx
```bash
sudo cp /var/www/numerology/numerology-nginx.conf /etc/nginx/sites-available/numerology
```

### 8.2 Enable site
```bash
sudo ln -sf /etc/nginx/sites-available/numerology /etc/nginx/sites-enabled/numerology
```

### 8.3 Test konfigurasi Nginx
```bash
sudo nginx -t
```

### 8.4 Reload Nginx
```bash
sudo systemctl reload nginx
```

### 8.5 Cek status Nginx
```bash
sudo systemctl status nginx
```

---

## LANGKAH 9: Test Deployment

### 9.1 Test dari dalam VPS
```bash
# Test Gunicorn internal
curl -I http://127.0.0.1:8000/

# Test Nginx
curl -I http://localhost/
```

### 9.2 Test dari laptop
```bash
curl -I http://IP_VPS/
```

### 9.3 Buka di browser
```
http://IP_VPS/
```

---

## LANGKAH 10: Troubleshooting

### Jika service tidak jalan
```bash
sudo systemctl restart numerology
sudo journalctl -u numerology -f
```

### Jika Nginx error
```bash
sudo nginx -t
sudo tail -n 50 /var/log/nginx/error.log
```

### Update aplikasi
```bash
cd /var/www/numerology
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart numerology
```

---

## Ringkasan File Lokasi

| Item | Lokasi |
|-----|--------|
| Aplikasi | `/var/www/numerology/` |
| Virtual Environment | `/var/www/numerology/venv/` |
| Database | `/var/www/numerology/app.db` |
| Uploads | `/var/www/numerology/uploads/` |
| Environment | `/var/www/numerology/.env` |
| Systemd Service | `/etc/systemd/system/numerology.service` |
| Nginx Config | `/etc/nginx/sites-available/numerology` |

---

## Catatan Penting

- Pastikan VPS punya minimal 1GB RAM
- File `app.db` dan folder `uploads/` harus writable oleh user `www-data`
- SECRET_KEY harus di-generate random, jangan pakai default
- Untuk produksi dengan domain, tambahkan SSL dengan Let's Encrypt
