# Panduan Deployment ke VPS (SSH Mode)

## Konfigurasi
- **VPS IP**: 76.13.193.187
- **VPS User**: root
- **GitHub Repo**: git@github.com:duauban25/numerologi.git (SSH)
- **OS**: Ubuntu 24.04 LTS

---

## LANGKAH 1: Login ke VPS

```bash
ssh root@76.13.193.187
```

---

## LANGKAH 2: Update Sistem dan Install Paket

```bash
apt update
apt upgrade -y

apt install -y \
    python3 python3-venv python3-pip \
    build-essential python3-dev \
    nginx git ufw curl sqlite3
```

---

## LANGKAH 3: Setup SSH Key untuk GitHub

### 3.1 Generate SSH Key (jika belum ada)
```bash
ssh-keygen -t ed25519 -C "root@vps"
```
Tekan Enter untuk semua default (bisa tanpa passphrase)

### 3.2 Tampilkan public key
```bash
cat ~/.ssh/id_ed25519.pub
```

### 3.3 Copy public key ke GitHub
- Copy output dari perintah di atas
- Buka GitHub → Settings → SSH and GPG Keys → New SSH key
- Paste key dan save

### 3.4 Test koneksi ke GitHub
```bash
ssh -T git@github.com
```
Harus muncul: `Hi duauban25! You've successfully authenticated...`

---

## LANGKAH 4: Konfigurasi Firewall

```bash
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw --force enable
ufw status
```

---

## LANGKAH 5: Clone Repository via SSH

```bash
mkdir -p /var/www/numerology
cd /var/www/numerology
git clone git@github.com:duauban25/numerologi.git .
```

---

## LANGKAH 6: Setup Python Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### Test import
```bash
venv/bin/python -c "from app import app; print('Import berhasil')"
```

---

## LANGKAH 7: Setup Folder dan Permission

```bash
mkdir -p /var/www/numerology/uploads
chown -R www-data:www-data /var/www/numerology/uploads
chown www-data:www-data /var/www/numerology/app.db || true
```

---

## LANGKAH 8: Setup Environment Variables

### 8.1 Generate SECRET_KEY
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 8.2 Buat file .env
```bash
nano /var/www/numerology/.env
```

### 8.3 Isi dengan SECRET_KEY
```bash
SECRET_KEY=paste_hasil_generate_di_sini
```

### 8.4 Set permission
```bash
chown www-data:www-data /var/www/numerology/.env
chmod 600 /var/www/numerology/.env
```

---

## LANGKAH 9: Setup Systemd Service

### 9.1 Copy file service
```bash
cp /var/www/numerology/numerology.service /etc/systemd/system/numerology.service
```

### 9.2 Reload dan start service
```bash
systemctl daemon-reload
systemctl enable numerology
systemctl start numerology
```

### 9.3 Cek status
```bash
systemctl status numerology
```

---

## LANGKAH 10: Setup Nginx

### 10.1 Copy konfigurasi Nginx
```bash
cp /var/www/numerology/numerology-nginx.conf /etc/nginx/sites-available/numerology
```

### 10.2 Enable site
```bash
ln -sf /etc/nginx/sites-available/numerology /etc/nginx/sites-enabled/numerology
```

### 10.3 Test dan reload
```bash
nginx -t
systemctl reload nginx
```

### 10.4 Cek status
```bash
systemctl status nginx
```

---

## LANGKAH 11: Test Deployment

### 11.1 Test dari VPS
```bash
curl -I http://127.0.0.1:8000/
curl -I http://localhost/
```

### 11.2 Test dari laptop
```bash
curl -I http://76.13.193.187/
```

### 11.3 Buka di browser
```
http://76.13.193.187/
```

---

## LANGKAH 12: Troubleshooting

### Cek log aplikasi
```bash
journalctl -u numerology -n 100 --no-pager
```

### Cek log Nginx
```bash
tail -n 50 /var/log/nginx/error.log
```

### Restart service
```bash
systemctl restart numerology
systemctl restart nginx
```

### Update aplikasi
```bash
cd /var/www/numerology
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
systemctl restart numerology
```

---

## Ringkasan Perintah (Copy-Paste Mode)

Jalankan ini satu per satu di VPS:

```bash
# 1. Update dan install
apt update && apt upgrade -y
apt install -y python3 python3-venv python3-pip build-essential python3-dev nginx git ufw curl sqlite3

# 2. Firewall
ufw allow OpenSSH && ufw allow 'Nginx Full' && ufw --force enable

# 3. Clone repository
mkdir -p /var/www/numerology && cd /var/www/numerology
git clone git@github.com:duauban25/numerologi.git .

# 4. Setup Python
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# 5. Permission
mkdir -p /var/www/numerology/uploads
chown -R www-data:www-data /var/www/numerology/uploads
chown www-data:www-data /var/www/numerology/app.db || true

# 6. Environment
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
echo "SECRET_KEY=$SECRET_KEY" > /var/www/numerology/.env
chown www-data:www-data /var/www/numerology/.env
chmod 600 /var/www/numerology/.env

# 7. Systemd service
cp /var/www/numerology/numerology.service /etc/systemd/system/numerology.service
systemctl daemon-reload
systemctl enable numerology
systemctl start numerology

# 8. Nginx
cp /var/www/numerology/numerology-nginx.conf /etc/nginx/sites-available/numerology
ln -sf /etc/nginx/sites-available/numerology /etc/nginx/sites-enabled/numerology
nginx -t
systemctl reload nginx

# 9. Cek status
systemctl status numerology
systemctl status nginx
```

---

## Catatan Penting

- Pastikan SSH key sudah terdaftar di GitHub sebelum clone
- VPS login sebagai root, jadi tidak perlu sudo
- Aplikasi akan jalan di http://76.13.193.187/
- Untuk HTTPS, tambahkan domain dan setup Let's Encrypt
