from pymongo import MongoClient
from werkzeug.security import check_password_hash

# Koneksi ke MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client.tugasakhir

# Data akun dari akun.txt
test_accounts = [
    {"username": "123456789012345678", "password": "0000", "role": "kaprodi"},
    {"username": "Admin", "password": "0101", "role": "admin"},
    {"username": "098765432112345678", "password": "srh", "role": "dosen"}
]

print("=" * 70)
print("PENGUJIAN LOGIN - VERIFIKASI DATA USER DI DATABASE")
print("=" * 70)

# Cek semua user di database
all_users = list(db.users.find())
print(f"\nTotal user di database: {len(all_users)}")
print("\nDaftar user di database:")
for user in all_users:
    print(f"  - Username: {user['username']}, Role: {user['role']}")

print("\n" + "=" * 70)
print("TEST LOGIN UNTUK SETIAP AKUN")
print("=" * 70)

for account in test_accounts:
    username = account["username"]
    password = account["password"]
    role = account["role"]
    
    print(f"\n{'='*70}")
    print(f"Testing {role.upper()}: username='{username}'")
    print(f"{'='*70}")
    
    # Cari user di database
    user = db.users.find_one({"username": username, "role": role})
    
    if not user:
        print(f"❌ GAGAL - User tidak ditemukan di database")
        print(f"   Query: username='{username}', role='{role}'")
        # Coba cari tanpa role
        user_any = db.users.find_one({"username": username})
        if user_any:
            print(f"   ⚠️  User ditemukan tapi dengan role berbeda: {user_any['role']}")
        continue
    
    print(f"✅ User ditemukan di database")
    print(f"   Username: {user['username']}")
    print(f"   Role: {user['role']}")
    
    # Cek password
    password_match = check_password_hash(user["password"], password)
    
    if password_match:
        print(f"✅ Password COCOK - Login akan BERHASIL")
    else:
        print(f"❌ Password TIDAK COCOK - Login akan GAGAL")
        print(f"   Password yang diuji: '{password}'")

print("\n" + "=" * 70)
print("RINGKASAN PENGUJIAN")
print("=" * 70)

success_count = 0
for account in test_accounts:
    user = db.users.find_one({"username": account["username"], "role": account["role"]})
    if user and check_password_hash(user["password"], account["password"]):
        success_count += 1
        print(f"✅ {account['role'].upper()}: {account['username']} - SIAP LOGIN")
    else:
        print(f"❌ {account['role'].upper()}: {account['username']} - GAGAL")

print(f"\nTotal: {success_count}/{len(test_accounts)} akun siap digunakan")
print("=" * 70)
