# VPS Deployment Guide - Numerology App

## Prerequisites
- Ubuntu 24.04 LTS VPS
- SSH access to VPS
- GitHub repository: https://github.com/duauban25/comsetbaru

## Quick Deployment (Automated)

### 1. Upload deployment files to VPS
From your local machine:
```bash
scp /Users/baktanarta/Documents/numerology/deploy.sh username@IP_VPS:/tmp/
scp /Users/baktanarta/Documents/numerology/numerology.service username@IP_VPS:/tmp/
scp /Users/baktanarta/Documents/numerology/numerology-nginx.conf username@IP_VPS:/tmp/
```

### 2. Run deployment script on VPS
```bash
ssh username@IP_VPS
sudo mv /tmp/deploy.sh /var/www/numerology/
sudo mv /tmp/numerology.service /var/www/numerology/
sudo mv /tmp/numerology-nginx.conf /var/www/numerology/
cd /var/www/numerology
sudo bash deploy.sh
```

The script will automatically:
- Update system and install required packages
- Configure firewall (UFW)
- Clone repository from GitHub
- Setup Python virtual environment
- Install dependencies
- Configure permissions
- Setup systemd service
- Configure Nginx
- Start all services

## Manual Deployment (Step by Step)

### 1. Update system and install packages
```bash
sudo apt update
sudo apt upgrade -y

sudo apt install -y \
    python3 python3-venv python3-pip \
    build-essential python3-dev \
    nginx git ufw curl sqlite3
```

### 2. Configure firewall
```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw --force enable
sudo ufw status
```

### 3. Create deployment directory
```bash
sudo mkdir -p /var/www/numerology
sudo chown -R $USER:$USER /var/www/numerology
```

### 4. Clone repository
```bash
cd /var/www/numerology
git clone https://github.com/duauban25/comsetbaru.git .
```

### 5. Setup virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### 6. Setup uploads directory
```bash
mkdir -p uploads
sudo chown -R www-data:www-data /var/www/numerology/uploads
```

### 7. Setup database permissions
```bash
sudo chown www-data:www-data /var/www/numerology/app.db || true
```

### 8. Create environment file
```bash
sudo nano /var/www/numerology/.env
```

Add:
```bash
SECRET_KEY=your-random-secret-key-here
```

Generate random key:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 9. Install systemd service
```bash
sudo cp numerology.service /etc/systemd/system/numerology.service
sudo systemctl daemon-reload
sudo systemctl enable numerology
sudo systemctl start numerology
sudo systemctl status numerology
```

### 10. Install Nginx configuration
```bash
sudo cp numerology-nginx.conf /etc/nginx/sites-available/numerology
sudo ln -sf /etc/nginx/sites-available/numerology /etc/nginx/sites-enabled/numerology
sudo nginx -t
sudo systemctl reload nginx
```

### 11. Test deployment
```bash
# Check service status
sudo systemctl status numerology

# Check Nginx status
sudo systemctl status nginx

# Test from VPS
curl -I http://127.0.0.1:8000/
curl -I http://IP_VPS/
```

## Access Your Application

After deployment, access your app at:
- `http://IP_VPS/`

## Troubleshooting

### Check application logs
```bash
sudo journalctl -u numerology -n 200 --no-pager
```

### Check Nginx logs
```bash
sudo tail -n 200 /var/log/nginx/error.log
```

### Restart services
```bash
sudo systemctl restart numerology
sudo systemctl restart nginx
```

### Update application
```bash
cd /var/www/numerology
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart numerology
```

## File Locations

- Application: `/var/www/numerology/`
- Virtual environment: `/var/www/numerology/venv/`
- Database: `/var/www/numerology/app.db`
- Uploads: `/var/www/numerology/uploads/`
- Systemd service: `/etc/systemd/system/numerology.service`
- Nginx config: `/etc/nginx/sites-available/numerology`

## Security Notes

- Change the default SECRET_KEY in `.env` file
- Consider setting up SSL/HTTPS with Let's Encrypt when using a domain
- Regularly update system packages
- Backup `app.db` regularly (SQLite database)
