import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
import joblib
import os

os.makedirs("data", exist_ok=True)
os.makedirs("models", exist_ok=True)

df = pd.read_csv("data/dataset.csv", sep=",")
df.drop(['NAMA', 'SEMESTER'], axis=1, inplace=True)
df.insert(0, "ID", [f"MHS{i+1:03d}" for i in range(len(df))])

columns = [
    "ETIKA", "BERPIKIR_KRITIS", "KEPEMIMPINAN", "KEMAMPUAN_KOMUNIKASI",
    "MANAJEMEN_DIRI", "PENYELESAIAN_MASALAH", "KERJA_SAMA_TIM",
    "MANAJEMEN_WAKTU", "TUGAS_TERLAMBAT", "KEHADIRAN",
]

# Labelling data
print("\nData Sebelum Labelling")
print("Unique values ORGANISASI", df["ORGANISASI"].unique())
print("Unique values KELULUSAN:", df["KELULUSAN"].unique())

kelulusan = LabelEncoder()
df["KELULUSAN"] = kelulusan.fit_transform(df["KELULUSAN"])

print("\nHasil Labelling")
print("\nKELULUSAN:")
kelulusan_df = pd.DataFrame(
    {"Kategori": kelulusan.classes_, "Label": range(len(kelulusan.classes_))}
)
print(kelulusan_df.to_string(index=False))
print("--" * 50)

print("\nORGANISASI:")
original_categories = df['ORGANISASI'].unique()
original_categories.sort()

# One-Hot Encoding
df = pd.get_dummies(df, columns=['ORGANISASI'], prefix='ORGANISASI', drop_first=True, dtype=int)

new_org= [col for col in df.columns if col.startswith('ORGANISASI_')]
kategori= original_categories[1]
kategori_basis = original_categories[0]

organisasi = {
    "Kategori": [kategori, kategori_basis],
    "Label": [f"1", f"0"]
}
organisasi_df = pd.DataFrame(organisasi)
print(organisasi_df.to_string(index=False))
print("--" * 50)

print("\nData Setelah Labelling")
pd.set_option("display.max_rows", 30)
pd.set_option("display.max_columns", 12)
pd.set_option("display.width", None)
print(df.head())
pd.reset_option("display.max_rows")
pd.reset_option("display.max_columns")
pd.reset_option("display.width")

# Split data
X = df.drop(["KELULUSAN"], axis=1)
y = df["KELULUSAN"]

# Simpan kolom ID terpisah untuk tracking
ids = X["ID"]


X = X.drop(["ID"], axis=1)

X_train, X_test, y_train, y_test, id_train, id_test = train_test_split(
    X, y, ids, test_size=0.2, random_state=42
)

feature_names = X_train.columns.tolist()
joblib.dump(feature_names, "models/feature_names.joblib")

# Feature Scaling
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# convert kembali ke df dgn nama kolom yg benar
X_train_scaled_df = pd.DataFrame(X_train_scaled, columns=X_train.columns, index=X_train.index)
X_test_scaled_df = pd.DataFrame(X_test_scaled, columns=X_test.columns, index=X_test.index)

# gabung fitur, target, dan ID
train_data = X_train_scaled_df.copy()
train_data["KELULUSAN"] = y_train
train_data["ID"] = id_train

test_data = X_test_scaled_df.copy()
test_data["KELULUSAN"] = y_test
test_data["ID"] = id_test

# save data
try:
    train_data.to_csv("data/train_data.csv", index=False)
    test_data.to_csv("data/test_data.csv", index=False)
    print("\n Data Split Disimpan ")
    print("File train disimpan di: data/train_data.csv")
    print("File test disimpan di: data/test_data.csv")
    print(f"Jumlah data train: {len(train_data)} ({len(train_data)/len(df)*100:.1f}%)")
    print(f"Jumlah data test: {len(test_data)} ({len(test_data)/len(df)*100:.1f}%)")
except Exception as e:
    print(f"\n Gagal menyimpan file: {str(e)}")
    print("Pastikan:")
    print("- Folder 'data' ada dan dapat dibuka")
    print("- Tidak ada file dengan nama yang sama yang sedang terbuka")

# save preprocessor
joblib.dump(kelulusan, "models/kelulusan.joblib")
joblib.dump(scaler, "models/scaler.joblib")

print("\nDistribusi Label pada Data Train & Test ")

print("\nDistribusi Data Latih (y_train):")
train_counts = y_train.value_counts()
train_percentages = y_train.value_counts(normalize=True) * 100
train_dist_df = pd.DataFrame({
    'Jumlah': train_counts,
    'Persentase (%)': train_percentages.round(2)
})
train_dist_df.index = [kelulusan.classes_[i] for i in train_dist_df.index]
print(train_dist_df.to_string())

print("\nDistribusi Data Uji (y_test):")
test_counts = y_test.value_counts()
test_percentages = y_test.value_counts(normalize=True) * 100
test_dist_df = pd.DataFrame({
    'Jumlah': test_counts,
    'Persentase (%)': test_percentages.round(2)
})
test_dist_df.index = [kelulusan.classes_[i] for i in test_dist_df.index]
print(test_dist_df.to_string())
