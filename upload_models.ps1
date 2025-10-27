# Upload Models to Server Script
# Gunakan script ini untuk upload file models ke server

# WINDOWS (PowerShell)
# ====================

# 1. Compress models folder
Write-Host "Compressing models folder..." -ForegroundColor Green
Compress-Archive -Path models -DestinationPath models.zip -Force

# 2. Upload to server
# Ganti dengan IP server dan user Anda
$SERVER_IP = "YOUR_SERVER_IP"
$SERVER_USER = "flaskapp"
$SERVER_PATH = "/home/flaskapp/prediksikelulusan/"

Write-Host "Uploading to server..." -ForegroundColor Green
Write-Host "Run this command:" -ForegroundColor Yellow
Write-Host "scp models.zip ${SERVER_USER}@${SERVER_IP}:${SERVER_PATH}" -ForegroundColor Cyan

# 3. Unzip di server
Write-Host "`nAfter upload, run on server:" -ForegroundColor Yellow
Write-Host "cd /home/flaskapp/prediksikelulusan" -ForegroundColor Cyan
Write-Host "unzip -o models.zip" -ForegroundColor Cyan
Write-Host "rm models.zip" -ForegroundColor Cyan
Write-Host "ls -lh models/" -ForegroundColor Cyan

# ATAU gunakan ini untuk upload langsung semua file (lebih lambat):
# scp -r models ${SERVER_USER}@${SERVER_IP}:${SERVER_PATH}


# LINUX/MAC (Bash)
# =================

# #!/bin/bash
# SERVER_IP="YOUR_SERVER_IP"
# SERVER_USER="flaskapp"
# SERVER_PATH="/home/flaskapp/prediksikelulusan/"
#
# echo "Compressing models folder..."
# zip -r models.zip models/
#
# echo "Uploading to server..."
# scp models.zip ${SERVER_USER}@${SERVER_IP}:${SERVER_PATH}
#
# echo "SSH to server and run:"
# echo "  cd ${SERVER_PATH}"
# echo "  unzip -o models.zip"
# echo "  rm models.zip"
# echo "  ls -lh models/"
#
# # Cleanup local
# rm models.zip


# ALTERNATIVE: Training ulang model di server
# ============================================
# Jika tidak ingin upload, training ulang di server:
#
# ssh flaskapp@YOUR_SERVER_IP
# cd /home/flaskapp/prediksikelulusan
# source env/bin/activate
# bash generate_models.sh
# # ATAU: python src/training.py
