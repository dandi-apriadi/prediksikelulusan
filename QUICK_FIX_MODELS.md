# QUICK FIX: Error FileNotFoundError models/feature_names.joblib

## Problem
```
FileNotFoundError: [Errno 2] No such file or directory: 'models/feature_names.joblib'
```

## Cause
File models tidak ada di Git karena ukurannya besar dan ada di `.gitignore`

## Solution (Pilih salah satu)

### ✅ Solusi 1: Training Model di Server (RECOMMENDED)

Di server, jalankan:
```bash
cd /home/flaskapp/prediksikelulusan  # sesuai nama folder di server
source env/bin/activate
bash generate_models.sh
```

Atau manual:
```bash
cd /home/flaskapp/prediksikelulusan
source env/bin/activate
python src/training.py
ls -lh models/  # verify models created
```

### ✅ Solusi 2: Upload dari Komputer Lokal

**Di komputer lokal (Windows):**
```powershell
# Compress models
Compress-Archive -Path models -DestinationPath models.zip

# Upload ke server (ganti YOUR_SERVER_IP dengan IP server Anda)
scp models.zip flaskapp@YOUR_SERVER_IP:/home/flaskapp/prediksikelulusan/
```

**Di server:**
```bash
cd /home/flaskapp/prediksikelulusan
unzip -o models.zip
rm models.zip
ls -lh models/
```

### ✅ Solusi 3: Upload Individual Files

```powershell
# Di komputer lokal
scp -r models flaskapp@YOUR_SERVER_IP:/home/flaskapp/prediksikelulusan/
```

## Verify

Setelah models ada, cek:
```bash
cd /home/flaskapp/prediksikelulusan
ls -lh models/
```

Harus ada file-file ini:
- feature_names.joblib
- imputer.joblib
- kelulusan.joblib
- model_metadata.joblib
- random_forest_model.joblib
- scaler.joblib
- shap.joblib

## Test Application

```bash
python app.py
```

Jika sukses, aplikasi akan berjalan tanpa error!

## Tips

- **Solusi 1** lebih mudah dan tidak perlu transfer file besar
- **Solusi 2** lebih cepat jika models sudah ada di lokal
- Pastikan `data/dataset.csv` ada sebelum training
