# Cheatsheet - Command Reference untuk VPS

## Struktur Direktori di VPS
```
/home/flaskapp/prediksikelulusan/
├── app.py
├── data/
├── env/
├── generate_models.sh
├── models/
├── notebooks/
├── requirements-linux.txt
├── reset_passwords.py
├── setup server.txt
├── src/
├── static/
├── templates/
├── test_login.py
└── uploads/
```

## Command Penting

### 1. Navigasi & Status
```bash
# Masuk ke direktori project
cd /home/flaskapp/prediksikelulusan

# Cek isi folder
ls -la

# Aktifkan virtual environment
source env/bin/activate

# Cek Python version
python --version

# Cek pip packages
pip list
```

### 2. Generate/Update Models
```bash
cd /home/flaskapp/prediksikelulusan
source env/bin/activate

# Menggunakan script auto
bash generate_models.sh

# Atau manual
python src/training.py

# Verify models
ls -lh models/
```

### 3. Test Aplikasi
```bash
cd /home/flaskapp/prediksikelulusan
source env/bin/activate
python app.py
# Tekan Ctrl+C untuk stop
```

### 4. Service Management (Gunicorn)
```bash
# Start service
sudo systemctl start prediksi

# Stop service
sudo systemctl stop prediksi

# Restart service
sudo systemctl restart prediksi

# Status service
sudo systemctl status prediksi

# Enable auto-start saat boot
sudo systemctl enable prediksi

# Cek log
sudo journalctl -u prediksi -f
sudo journalctl -u prediksi -n 100
```

### 5. Nginx Management
```bash
# Test config
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx

# Status Nginx
sudo systemctl status nginx

# Cek log
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 6. Update dari GitHub
```bash
cd /home/flaskapp/prediksikelulusan

# Pull update terbaru
git pull origin main

# Jika ada conflict
git status
git stash  # simpan perubahan local
git pull origin main
git stash pop  # restore perubahan local

# Update dependencies
source env/bin/activate
pip install -r requirements-linux.txt

# Restart aplikasi
sudo systemctl restart prediksi
```

### 7. MongoDB Management
```bash
# Masuk ke MongoDB shell
mongosh

# atau dengan authentication
mongosh "mongodb://flaskapp:password@localhost:27017/tugasakhir"

# Di dalam MongoDB shell:
show dbs
use tugasakhir
show collections
db.users.find()
exit

# Backup database
mongodump --uri="mongodb://flaskapp:password@localhost:27017/tugasakhir" --out=/home/flaskapp/backups/backup-$(date +%Y%m%d)

# Restore database
mongorestore --uri="mongodb://flaskapp:password@localhost:27017/tugasakhir" /home/flaskapp/backups/backup-20250101/tugasakhir/

# Cek status MongoDB
sudo systemctl status mongod
```

### 8. File Permissions
```bash
# Set ownership untuk folder uploads
sudo chown -R flaskapp:www-data /home/flaskapp/prediksikelulusan/uploads
sudo chmod -R 775 /home/flaskapp/prediksikelulusan/uploads

# Set permissions untuk static files
sudo chown -R flaskapp:www-data /home/flaskapp/prediksikelulusan/static
sudo chmod -R 755 /home/flaskapp/prediksikelulusan/static

# Cek permission socket
ls -la /home/flaskapp/prediksikelulusan/prediksi.sock
```

### 9. SSL Certificate Management
```bash
# Generate/renew SSL certificate
sudo certbot --nginx -d prediksikelulusanmahasiswa.site -d www.prediksikelulusanmahasiswa.site

# Test auto-renewal
sudo certbot renew --dry-run

# List certificates
sudo certbot certificates

# Force renew
sudo certbot renew --force-renewal
```

### 10. Monitoring & Logs
```bash
# Monitor aplikasi real-time
sudo journalctl -u prediksi -f

# Cek last 50 lines log
sudo journalctl -u prediksi -n 50

# Cek error saja
sudo journalctl -u prediksi -p err

# Monitor Nginx access log
sudo tail -f /var/log/nginx/access.log

# Monitor Nginx error log
sudo tail -f /var/log/nginx/error.log

# Disk usage
df -h

# Memory usage
free -h

# CPU & process
top
htop  # jika sudah install
```

### 11. Firewall (UFW)
```bash
# Status firewall
sudo ufw status

# Allow port
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp

# Enable firewall
sudo ufw enable

# Disable firewall
sudo ufw disable
```

### 12. System Info
```bash
# Ubuntu version
lsb_release -a

# System info
uname -a

# Disk space
df -h

# Memory
free -h

# CPU info
lscpu

# Network info
ip addr show
```

### 13. Process Management
```bash
# Cek process Python yang running
ps aux | grep python

# Kill process by PID
kill PID_NUMBER
kill -9 PID_NUMBER  # force kill

# Cek port yang digunakan
sudo netstat -tulpn | grep :80
sudo netstat -tulpn | grep :443
```

### 14. Troubleshooting Common Issues

**Issue: 502 Bad Gateway**
```bash
sudo systemctl status prediksi
sudo journalctl -u prediksi -n 50
ls -la /home/flaskapp/prediksikelulusan/prediksi.sock
sudo systemctl restart prediksi
sudo systemctl restart nginx
```

**Issue: Models tidak ada**
```bash
cd /home/flaskapp/prediksikelulusan
source env/bin/activate
bash generate_models.sh
ls -lh models/
```

**Issue: Permission denied**
```bash
sudo chown -R flaskapp:www-data /home/flaskapp/prediksikelulusan
sudo chmod -R 755 /home/flaskapp/prediksikelulusan
```

**Issue: MongoDB connection failed**
```bash
sudo systemctl status mongod
sudo systemctl restart mongod
mongosh "mongodb://localhost:27017/tugasakhir"
```

## Quick Commands

### Restart Everything
```bash
cd /home/flaskapp/prediksikelulusan
source env/bin/activate
sudo systemctl restart prediksi
sudo systemctl restart nginx
sudo systemctl restart mongod
```

### Full Update & Restart
```bash
cd /home/flaskapp/prediksikelulusan
git pull origin main
source env/bin/activate
pip install -r requirements-linux.txt
sudo systemctl restart prediksi
```

### Check All Services
```bash
sudo systemctl status prediksi
sudo systemctl status nginx
sudo systemctl status mongod
```

### View All Logs
```bash
# Terminal 1
sudo journalctl -u prediksi -f

# Terminal 2
sudo tail -f /var/log/nginx/access.log

# Terminal 3
sudo tail -f /var/log/nginx/error.log
```

## Maintenance Schedule

### Daily
- Cek log errors: `sudo journalctl -u prediksi -p err`
- Monitor disk space: `df -h`

### Weekly
- Review access logs: `sudo tail -100 /var/log/nginx/access.log`
- Backup database

### Monthly
- Update system: `sudo apt update && sudo apt upgrade -y`
- Review SSL certificate: `sudo certbot certificates`
- Clean old backups
- Review and optimize database
