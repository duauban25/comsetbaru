#!/bin/bash

# Deployment script for Numerology app to VPS (Ubuntu 24.04 LTS)
# Usage: ./deploy.sh

set -e

echo "=== Numerology VPS Deployment Script ==="
echo ""

# Configuration
REPO_URL="https://github.com/duauban25/numerologi.git"
DEPLOY_DIR="/var/www/numerology"
SERVICE_NAME="numerology"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

# Step 1: Update system and install packages
echo "Step 1: Updating system and installing packages..."
apt update
apt upgrade -y

apt install -y \
    python3 python3-venv python3-pip \
    build-essential python3-dev \
    nginx git ufw curl sqlite3

# Step 2: Setup firewall
echo "Step 2: Configuring firewall..."
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw --force enable

# Step 3: Create deployment directory
echo "Step 3: Creating deployment directory..."
mkdir -p $DEPLOY_DIR
chown -R $SUDO_USER:$SUDO_USER $DEPLOY_DIR

# Step 4: Clone repository
echo "Step 4: Cloning repository..."
if [ -d "$DEPLOY_DIR/.git" ]; then
    echo "Repository already exists, pulling latest changes..."
    cd $DEPLOY_DIR
    sudo -u $SUDO_USER git pull origin main
else
    echo "Cloning repository..."
    sudo -u $SUDO_USER git clone $REPO_URL $DEPLOY_DIR
fi

# Step 5: Setup virtual environment
echo "Step 5: Setting up virtual environment..."
cd $DEPLOY_DIR
if [ ! -d "venv" ]; then
    sudo -u $SUDO_USER python3 -m venv venv
fi
sudo -u $SUDO_USER venv/bin/pip install --upgrade pip setuptools wheel
sudo -u $SUDO_USER venv/bin/pip install -r requirements.txt

# Step 6: Setup uploads directory
echo "Step 6: Setting up uploads directory..."
mkdir -p $DEPLOY_DIR/uploads
chown -R www-data:www-data $DEPLOY_DIR/uploads

# Step 7: Setup database permissions
echo "Step 7: Setting up database permissions..."
if [ -f "$DEPLOY_DIR/app.db" ]; then
    chown www-data:www-data $DEPLOY_DIR/app.db
fi

# Step 8: Create environment file
echo "Step 8: Creating environment file..."
if [ ! -f "$DEPLOY_DIR/.env" ]; then
    echo "Creating .env file with random SECRET_KEY..."
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    echo "SECRET_KEY=$SECRET_KEY" > $DEPLOY_DIR/.env
    chown www-data:www-data $DEPLOY_DIR/.env
    chmod 600 $DEPLOY_DIR/.env
fi

# Step 9: Install systemd service
echo "Step 9: Installing systemd service..."
cp numerology.service /etc/systemd/system/$SERVICE_NAME.service
systemctl daemon-reload
systemctl enable $SERVICE_NAME
systemctl restart $SERVICE_NAME

# Step 10: Install Nginx configuration
echo "Step 10: Installing Nginx configuration..."
cp numerology-nginx.conf /etc/nginx/sites-available/$SERVICE_NAME
ln -sf /etc/nginx/sites-available/$SERVICE_NAME /etc/nginx/sites-enabled/$SERVICE_NAME
nginx -t
systemctl reload nginx

# Step 11: Final checks
echo "Step 11: Running final checks..."
echo ""
echo "=== Service Status ==="
systemctl status $SERVICE_NAME --no-pager -l
echo ""
echo "=== Nginx Status ==="
systemctl status nginx --no-pager -l
echo ""
echo "=== Firewall Status ==="
ufw status
echo ""

echo "=== Deployment Complete ==="
echo "Your app should now be accessible at: http://$(curl -s ifconfig.me)/"
echo "Check logs with: sudo journalctl -u $SERVICE_NAME -f"
