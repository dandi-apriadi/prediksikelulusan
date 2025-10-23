from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash

# Koneksi ke MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client.tugasakhir

# Data akun dari akun.txt yang akan di-update
accounts = [
    {"username": "123456789012345678", "password": "0000", "role": "kaprodi"},
    {"username": "Admin", "password": "0101", "role": "admin"},
    {"username": "098765432112345678", "password": "srh", "role": "dosen"}
]

print("=" * 70)
print("RESET PASSWORD SESUAI akun.txt")
print("=" * 70)

for account in accounts:
    username = account["username"]
    password = account["password"]
    role = account["role"]
    
    # Hash password baru
    hashed_password = generate_password_hash(password)
    
    # Update password di database
    result = db.users.update_one(
        {"username": username, "role": role},
        {"$set": {"password": hashed_password}}
    )
    
    if result.matched_count > 0:
        print(f"✅ {role.upper()}: {username}")
        print(f"   Password baru: {password}")
        print(f"   Hash: {hashed_password[:50]}...")
        
        # Verifikasi password berhasil di-update
        user = db.users.find_one({"username": username, "role": role})
        if user and check_password_hash(user["password"], password):
            print(f"   ✅ Verifikasi: Password berhasil di-update dan cocok!")
        else:
            print(f"   ❌ Verifikasi: Masih ada masalah dengan password")
    else:
        print(f"❌ {role.upper()}: {username} - Tidak ditemukan di database")
    
    print()

print("=" * 70)
print("VERIFIKASI AKHIR - TEST SEMUA AKUN")
print("=" * 70)

success_count = 0
for account in accounts:
    user = db.users.find_one({"username": account["username"], "role": account["role"]})
    if user and check_password_hash(user["password"], account["password"]):
        success_count += 1
        print(f"✅ {account['role'].upper()}: {account['username']} - SIAP LOGIN")
    else:
        print(f"❌ {account['role'].upper()}: {account['username']} - MASIH GAGAL")

print(f"\nTotal: {success_count}/{len(accounts)} akun siap digunakan")
print("=" * 70)
