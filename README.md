# Sistem Prediksi Kelulusan Mahasiswa

Aplikasi web berbasis Flask untuk memprediksi kelulusan mahasiswa menggunakan Machine Learning (Random Forest).

## 🚀 Fitur

- Prediksi kelulusan mahasiswa berdasarkan data akademik
- Prediksi batch menggunakan file Excel/CSV
- Dashboard analytics dengan visualisasi data
- Manajemen data mahasiswa dan mata kuliah
- Sistem autentikasi multi-level (Admin, Dosen, Mahasiswa)
- History prediksi
- Export hasil prediksi

## 📋 Requirements

### Development (Windows)
```bash
pip install -r requirements.txt
```

### Production (Linux/Ubuntu)
```bash
pip install -r requirements-linux.txt
```

**Catatan:** File `requirements.txt` berisi package `pywin32` yang hanya tersedia di Windows. Untuk deployment di Linux, gunakan `requirements-linux.txt` yang sudah menghilangkan dependency Windows-specific.

## 🛠️ Instalasi

### Development Setup

1. Clone repository
```bash
git clone https://github.com/dandi-apriadi/prediksikelulusan.git
cd prediksikelulusan
```

2. Buat virtual environment
```bash
python -m venv env
```

3. Aktivasi virtual environment
- Windows:
```bash
env\Scripts\activate
```
- Linux/Mac:
```bash
source env/bin/activate
```

4. Install dependencies
- Windows:
```bash
pip install -r requirements.txt
```
- Linux:
```bash
pip install -r requirements-linux.txt
```

5. Setup MongoDB
- Install MongoDB
- Buat database `tugasakhir`
- Import data awal jika ada

6. Konfigurasi environment variables (opsional)
```bash
# Buat file .env
SECRET_KEY=your_secret_key_here
MONGO_URI=mongodb://localhost:27017/tugasakhir
```

7. Jalankan aplikasi
```bash
python app.py
```

Aplikasi akan berjalan di `http://localhost:5000`

## 🚢 Production Deployment

Untuk deployment ke production server (Ubuntu), ikuti panduan lengkap di file `setup server.txt`.

### Quick Start Production:

**1. Upload models ke server** (PENTING!)

File models tidak ada di Git karena ukurannya besar. Ada 2 cara:

**Cara 1: Upload dari komputer lokal**
```powershell
# Windows PowerShell
.\upload_models.ps1
# Atau manual:
# scp -r models flaskapp@YOUR_SERVER_IP:/home/flaskapp/prediksikelulusan/
```

**Cara 2: Training ulang di server**
```bash
# Di server Ubuntu
cd /home/flaskapp/prediksikelulusan
source env/bin/activate
bash generate_models.sh
# ATAU: python src/training.py
```

**2. Install dependencies dan jalankan**
```bash
# Di server Ubuntu
pip install -r requirements-linux.txt
gunicorn --workers 4 --bind 0.0.0.0:8000 app:app
```

Untuk setup lengkap dengan Nginx, SSL, dan domain, lihat: [setup server.txt](setup%20server.txt)

## 📁 Struktur Project

```
prediksi/
├── app.py                  # Main Flask application
├── requirements.txt        # Dependencies untuk Windows
├── requirements-linux.txt  # Dependencies untuk Linux/Production
├── setup server.txt        # Panduan deployment production
├── upload_models.ps1       # Script upload models ke server
├── data/                   # Dataset training
│   ├── dataset.csv
│   ├── train_data.csv
│   └── test_data.csv
├── models/                 # Trained ML models (NOT in Git)
│   ├── random_forest_model.joblib
│   ├── scaler.joblib
│   ├── imputer.joblib
│   ├── feature_names.joblib
│   └── ...
├── src/                    # Source code ML
│   ├── training.py
│   ├── randomforest.py
│   └── eda.py
├── templates/              # HTML templates
├── static/                 # CSS, JS, images
├── uploads/                # User uploads
└── notebooks/              # Jupyter notebooks untuk EDA
```

**⚠️ PENTING:** Folder `models/` tidak ada di Git karena ukuran file besar. 
Anda harus:
1. Upload manual ke server, ATAU
2. Training ulang model di server dengan `python src/training.py`

## 🔑 Default Login

Setelah setup awal, gunakan kredensial berikut:
- **Username:** admin
- **Password:** (sesuai yang dibuat saat setup)

Atau jalankan `reset_passwords.py` untuk reset password.

## 🧪 Testing

```bash
python test_login.py
```

## 📊 Model Machine Learning

- **Algorithm:** Random Forest Classifier
- **Features:** IPK, SKS, kehadiran, nilai mata kuliah, dll
- **Metrics:** Akurasi, Precision, Recall, F1-Score
- **SHAP Values:** Untuk interpretasi model

Training model:
```bash
python src/training.py
```

## 🔧 Maintenance

### Backup Database
```bash
mongodump --uri="mongodb://localhost:27017/tugasakhir" --out=backup/
```

### Restore Database
```bash
mongorestore --uri="mongodb://localhost:27017/tugasakhir" backup/tugasakhir/
```

### Update Model
1. Update dataset di `data/dataset.csv`
2. Jalankan training: `python src/training.py`
3. Model baru akan disimpan di `models/`

## 🌐 Production URL

Website: [https://prediksikelulusanmahasiswa.site](https://prediksikelulusanmahasiswa.site)

## 📝 License

This project is licensed under the MIT License.

## 👨‍💻 Developer

Dandi Apriadi

## 📞 Support

Jika ada pertanyaan atau issue, silakan buat issue di repository ini atau hubungi developer.

---

**Note:** Pastikan untuk mengganti semua password default dan secret keys sebelum deployment ke production!
