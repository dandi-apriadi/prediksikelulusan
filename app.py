from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_pymongo import PyMongo
import pandas as pd
import joblib
from shap import plots
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps  # decorator login_required
from dotenv import load_dotenv
from datetime import datetime
import numpy as np
import shap
from bson.objectid import ObjectId
import os

SHAP = shap
import base64
from io import BytesIO

load_dotenv()

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/tugasakhir"
app.config["SECRET_KEY"] = (
    "eaf344f54e07d439eb3cd5ecb132fe15254a6d7b340940cc6a6257ef1fecabef"
)
mongo = PyMongo(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# klm
ss = joblib.load("models/feature_names.joblib")

target = "KELULUSAN"

app.jinja_env.globals["shap"] = shap
app.jinja_env.globals["SHAP"] = shap


# Muat model dan preprocessor
try:
    model = joblib.load("models/random_forest_model.joblib")
    scaler = joblib.load("models/scaler.joblib")
    kelulusan = joblib.load("models/kelulusan.joblib")
    shap_explainer = joblib.load("models/shap.joblib")
    print("Model dan preprocessor berhasil dimuat.")
except Exception as e:
    print(f"Error loading model or preprocessors: {e}")
    # exit()


@app.context_processor
def inject_now():
    return {"now": datetime.now()}


def role_required(*roles):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if "username" not in session:
                flash("Anda harus login untuk mengakses halaman ini.", "warning")
                return redirect(url_for("login"))

            user_role = session.get("role")
            if user_role not in roles:
                flash("Anda tidak memiliki izin untuk mengakses halaman ini.", "danger")
                return redirect(
                    url_for("login")
                ) 
            return fn(*args, **kwargs)

        return decorated_view

    return wrapper


# Decorator untuk memerlukan login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session:
            flash("Anda harus login untuk mengakses halaman ini.", "warning")
            return redirect(
                url_for("login")
            )
        return f(*args, **kwargs)

    return decorated_function


# LOGIN
@app.route("/")
@app.route("/login", methods=["GET", "POST"])
def login():
    if "username" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        role = request.form.get("role", "")

        # Validasi input kosong
        if not username or not password or not role:
            flash("Username, password, dan role wajib diisi.", "danger")
            return render_template("login.html")
        
        # Validasi format username berdasarkan role
        if role == "mahasiswa":
            if not (username.isdigit() and len(username) <= 8):
                flash("NIM mahasiswa harus berupa angka maksimal 8 digit.", "danger")
                return render_template("login.html")
        elif role in ["dosen", "kaprodi"]:
            if not (username.isdigit() and len(username) == 18):
                flash("NIP dosen/kaprodi harus berupa angka 18 digit.", "danger")
                return render_template("login.html")
        # Role admin tidak perlu validasi format khusus

        # Cari user sesuai role & username
        user = mongo.db.users.find_one({"username": username, "role": role})
        
        # Debug logging (bisa dihapus setelah masalah teratasi)
        print(f"[DEBUG] Login attempt - Username: {username}, Role: {role}")
        print(f"[DEBUG] User found in DB: {user is not None}")

        if user and check_password_hash(user["password"], password):
            session.clear()
            session["user_id"] = str(user["_id"])
            session["username"] = user["username"]
            session["role"] = user["role"]

            flash("Login berhasil", "success")
            return redirect(url_for("dashboard"))
        
        # Debug: kenapa login gagal?
        if not user:
            print(f"[DEBUG] User not found with username={username}, role={role}")
        elif user:
            print(f"[DEBUG] Password mismatch for user {username}")
        
        flash("Username, password, atau role salah", "danger")

    return render_template("login.html")



#  Registrasi
@app.route("/register", methods=["GET", "POST"])
def register():
    if "username" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        role = request.form.get("role")
        error = None

        if not username:
            error = "Username diperlukan."
        elif not password:
            error = "Password diperlukan."
        elif password != confirm_password:
            error = "Password tidak cocok."
        elif mongo.db.users.find_one({"username": username}):
            error = f"Username '{username}' sudah digunakan."
        else:
            if role == "mahasiswa" and not username.isdigit():
                error = "NIM harus berupa angka."
            elif role == "mahasiswa" and len(username) > 8:
                error = "NIM maksimal 8 digit."
            elif role in ["dosen", "kaprodi"] and (not username.isdigit() or len(username) != 18):
                error = "NIP dosen/kaprodi harus 18 digit angka."

        if error is None:
            hashed_password = generate_password_hash(password)
            mongo.db.users.insert_one(
                {
                    "username": username,
                    "password": hashed_password,
                    "role": role,  # simpan role sesuai pilihan
                }
            )
            flash("Registrasi berhasil! Silakan login.", "success")
            return redirect(url_for("login"))

        flash(error, "danger")

    return render_template("register.html")



#  Logout
@app.route("/logout")
@login_required
def logout():
    session.clear()
    flash("Anda telah berhasil logout.", "info")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    role = session.get("role")
    username = session.get("username")

    unique_nims = mongo.db.prediksi.distinct("NIM")
    jumlah_mahasiswa = len(unique_nims)
    total_pengguna = mongo.db.users.count_documents({})

    if role in ("admin", "kaprodi"):
        jumlah_prediksi = mongo.db.prediksi.count_documents({})
        lulus = mongo.db.prediksi.count_documents({"Prediksi": "Lulus"})
        tidak_lulus = mongo.db.prediksi.count_documents({"Prediksi": "Tidak Lulus"})
        aktivitas_terbaru = list(mongo.db.prediksi.find().sort("DateTime", -1).limit(5))
    else:
        jumlah_prediksi = mongo.db.prediksi.count_documents({"Submitted_by": username})
        lulus = mongo.db.prediksi.count_documents({"Submitted_by": username, "Prediksi": "Lulus"})
        tidak_lulus = mongo.db.prediksi.count_documents({"Submitted_by": username, "Prediksi": "Tidak Lulus"})
        aktivitas_terbaru = list(
            mongo.db.prediksi.find({"Submitted_by": username})
            .sort("DateTime", -1)
            .limit(5)
        )

    return render_template(
        "dashboard.html",
        active_page="dashboard",
        username=username,
        jumlah_mahasiswa=jumlah_mahasiswa,
        jumlah_prediksi=jumlah_prediksi,
        total_pengguna=total_pengguna,
        lulus=lulus,
        tidak_lulus=tidak_lulus,
        aktivitas_terbaru=aktivitas_terbaru,
    )



# Predict
@app.route("/prediction", methods=["GET", "POST"])
@login_required
def prediction():
    mk = list(mongo.db.mata_kuliah.find({}, {"_id": 0}))

    if request.method == "POST":
        form_data = request.form.to_dict()
        try:
            pertemuan = int(form_data.get("total_pertemuan", 16))
            kehadiran_per_mk = [
                int(v) for k, v in form_data.items() if k.startswith("kehadiran_")
            ]

            if not kehadiran_per_mk:
                presentase_kehadiran = 0
            else:
                total_hadir = sum(kehadiran_per_mk)
                jumlah_mk = len(kehadiran_per_mk)
                total_pertemuan_mungkin = pertemuan * jumlah_mk
                presentase_kehadiran = (total_hadir / total_pertemuan_mungkin) * 100

            input_dict = {col: 0.0 for col in ss}
            for col in ss:
                if col not in ["KEHADIRAN", "ORGANISASI_Ya"]:
                    input_dict[col] = float(form_data.get(col, 0))

            input_dict["KEHADIRAN"] = presentase_kehadiran

            organisasi_pilih = form_data.get("ORGANISASI_Ya", "Tidak")
            input_dict["ORGANISASI_Ya"] = 1 if organisasi_pilih == "Ya" else 0

            # DataFrame
            input_df = pd.DataFrame([input_dict], columns=ss)

            input_scaled_np = scaler.transform(input_df)
            input_scaled = pd.DataFrame(input_scaled_np, columns=ss)

            prediction_encoded = model.predict(input_scaled)
            prediction_label = kelulusan.inverse_transform(prediction_encoded)[0]

            # SHAP
            try:
                lulus_idx = np.where(kelulusan.classes_ == 'Lulus')[0][0]
            except (IndexError, ValueError):
                print("Peringatan: Label 'Lulus' tidak ditemukan di LabelEncoder. Menggunakan indeks 1.")
                lulus_idx = 1
            
            
            try:
                exp = shap_explainer(input_scaled)
                values = exp.values
                base_vals = getattr(exp, "base_values", None)

                if isinstance(values, np.ndarray) and values.ndim == 3:
                    # Bentuk (n_samples, n_features, n_classes)
                    sv = values[0, :, lulus_idx] 
                    if base_vals is not None:
                        base_value = (
                            base_vals[0, lulus_idx] 
                            if np.ndim(base_vals) == 2
                            else base_vals[lulus_idx] 
                        )
                    else:
                        base_value = 0.0
                else:
                    sv = values[0]
                    if base_vals is not None:
                        base_value = base_vals[0] if np.ndim(base_vals) >= 1 else float(base_vals)
                    else:
                        base_value = 0.0

            except Exception:
                
                shap_values_list = shap_explainer.shap_values(input_scaled)
                expected = getattr(shap_explainer, "expected_value", 0.0)

                if isinstance(shap_values_list, list):
                    # Jika list per kelas, pilih berdasarkan lulus_idx
                    sv = shap_values_list[lulus_idx][0]
                    if isinstance(expected, (list, np.ndarray)):
                        base_value = expected[lulus_idx]
                    else:
                        base_value = float(expected)
                else:
                    sv = shap_values_list[0]
                    if isinstance(expected, (list, np.ndarray)):
                        base_value = expected[0]
                    else:
                        base_value = float(expected)

            # Force Plot
            force_plot = shap.force_plot(
                base_value, 
                sv, 
                features=input_df.iloc[0], 
                matplotlib=False, 
                show=False,
                plot_cmap=["#008bfb", "#ff0052"]
            )

            
            shap_html = shap.getjs() + force_plot.html()

            # DF kontribusi fitur
            shap_df = pd.DataFrame(
                {
                    "Faktor": input_df.columns,
                    "Kontribusi": sv,
                }
            )

            # top 5 faktor absolut
            shap_df["Abs_Kontribusi"] = shap_df["Kontribusi"].abs()
            top_factors = shap_df.sort_values(
                by="Abs_Kontribusi", ascending=False
            ).head(5)

            analisis_hasil = top_factors[["Faktor", "Kontribusi"]].to_dict("records")

            prediction_record = {
                "NIM": form_data.get("NIM", "unknown"),
                "Nama": form_data.get("nama", "unknown"),
                "Semester": form_data.get("semester"),
                "Prediksi": prediction_label,
                "input_data": input_dict,
                "Analisis": analisis_hasil,
                "Submitted_by": session.get("username"),
                "DateTime": datetime.now(),
            }

            mongo.db.prediksi.insert_one(prediction_record)

            flash(f"Hasil Prediksi: {prediction_label}", "success")
            return render_template(
                "hasil_prediksi.html",
                prediction=prediction_label,
                nama_mahasiswa=form_data.get("nama", "Mahasiswa"),
                nim=form_data.get("NIM", "N/A"),
                semester=form_data.get("semester", "N/A"),
                analisis=analisis_hasil,
                shap_plot_html=shap_html,
                active_page="prediction",
            )

        except Exception as e:
            print(f"Error during prediction or preprocessing: {e}")
            flash(f"Terjadi kesalahan saat melakukan prediksi: {e}", "danger")
            return redirect(url_for("prediction"))

    selected_semester = request.args.get("semester", default=1, type=int)
    mk = list(mongo.db.mata_kuliah.find({"semester": selected_semester}, {"_id": 0}))

    semesters = range(1, 9)

    return render_template(
        "predict.html",
        mata_kuliah=mk,
        semesters=semesters,
        selected_semester=selected_semester,
        active_page="prediction",
    )


#riwayat
@app.route("/history")
@login_required
def history():
    role = session.get("role")
    username = session.get("username")
    
    nim_filter = request.args.get('nim', None)
    
    query = {}


    if role not in ["admin", "kaprodi"]:
        query["Submitted_by"] = username

    if nim_filter:
        query["NIM"] = nim_filter

    history_data = list(mongo.db.prediksi.find(query).sort("DateTime", -1))


    all_history = list(mongo.db.prediksi.find({}, {"Semester": 1, "Prediksi": 1, "_id": 0}))
    semesters = sorted(list(set(h.get('Semester') for h in all_history if h.get('Semester'))))
    statuses = sorted(list(set(h.get('Prediksi') for h in all_history if h.get('Prediksi'))))

    for h in history_data:
        h["DateTime_str"] = (
            h["DateTime"].strftime("%d-%m-%Y %H:%M")
            if "DateTime" in h and h["DateTime"]
            else "-"
        )

    return render_template(
        "history.html", 
        riwayat=history_data, 
        active_page="history",
        nim_filter=nim_filter,
        semesters=semesters,
        statuses=statuses
    )



@app.route("/history/detail/<id>")
@login_required
def view_prediction_detail(id):
    prediction = mongo.db.prediksi.find_one({"_id": ObjectId(id)})
    if not prediction:
        flash("Data prediksi tidak ditemukan.", "danger")
        return redirect(url_for("history"))


    role = session.get("role")
    if role not in ["admin", "kaprodi"] and prediction.get("Submitted_by") != session.get("username"):
        flash("Anda tidak memiliki izin untuk melihat detail ini.", "danger")
        return redirect(url_for("history"))

    return render_template("detail.html", prediction=prediction, active_page="detail")




# users
@app.route('/admin/users') 
@login_required
@role_required("admin")
def manage_users():
    users = list(mongo.db.users.find())
    return render_template("manage_users.html", users=users, active_page="users")


@app.route("/admin/users/add", methods=["POST"])
@login_required
@role_required("admin")
def add_user():
    try:
        username = request.form.get("username")
        nama = request.form.get("nama")
        role = request.form.get("role")
        password = request.form.get("password")

        if not username or not nama or not role or not password:
            flash("Semua field wajib diisi", "danger")
            return redirect(url_for("manage_users"))

        if mongo.db.users.find_one({"username": username}):
            flash("Username sudah digunakan", "danger")
            return redirect(url_for("manage_users"))

        hashed_password = generate_password_hash(password)
        user = {
            "username": username.strip(),
            "nama": nama.strip(),
            "role": role,
            "password": hashed_password,
        }
        mongo.db.users.insert_one(user)
        flash("User berhasil ditambahkan", "success")
    except Exception as e:
        flash(f"Gagal menambah user: {e}", "danger")

    return redirect(url_for("manage_users"))


@app.route("/admin/users/edit/<id>", methods=["POST"])
@login_required
@role_required("admin")
def edit_user(id):
    try:
        nama = request.form.get("nama")
        role = request.form.get("role")
        password = request.form.get("password")

        update_data = {"nama": nama, "role": role}
        if password:
            update_data["password"] = generate_password_hash(password)

        mongo.db.users.update_one({"_id": ObjectId(id)}, {"$set": update_data})
        flash("User berhasil diperbarui", "success")
    except Exception as e:
        flash(f"Gagal mengubah user: {e}", "danger")

    return redirect(url_for("manage_users"))


@app.route("/admin/users/delete/<id>")
@login_required
@role_required("admin")
def delete_user(id):
    try:
        mongo.db.users.delete_one({"_id": ObjectId(id)})
        flash("User berhasil dihapus", "success")
    except Exception as e:
        flash(f"Gagal menghapus user: {e}", "danger")

    return redirect(url_for("manage_users"))





# # manage mhs
# @app.route("/mahasiswa")
# @login_required
# @role_required("kaprodi", "admin")
# def manage_mahasiswa():
#     # Pipeline untuk mengambil data mahasiswa unik dari koleksi prediksi
#     pipeline = [
#         {
#             "$group": {
#                 "_id": "$NIM",
#                 "nama": {"$first": "$Nama"}
#             }
#         },
#         {
#             "$project": {
#                 "_id": 0,
#                 "username": "$_id",
#                 "nama": "$nama"
#             }
#         },
#         {
#             "$sort": {"username": 1}
#         }
#     ]
#     mahasiswa = list(mongo.db.prediksi.aggregate(pipeline))
 
#     angkatan_list = sorted(list(set(m['username'][:2] for m in mahasiswa if m.get('username'))))
#     return render_template("manage_mahasiswa.html",
#                            mahasiswa=mahasiswa, angkatan_list=angkatan_list, active_page="mahasiswa")


# @app.route("/mahasiswa/import", methods=["POST"])
# @login_required
# @role_required("kaprodi", "admin")
# def import_mahasiswa():
#     file = request.files.get("file")
#     if not file:
#         flash("Tidak ada file diunggah", "danger")
#         return redirect(url_for("manage_mahasiswa"))

#     filename = secure_filename(file.filename)
#     filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
#     file.save(filepath)

#     try:
#         if filename.endswith(".csv"):
#             df = pd.read_csv(filepath)
#         else:
#             df = pd.read_excel(filepath)

#         required_cols = {"username", "nama"}
#         if not required_cols.issubset(df.columns):
#             flash("File harus memiliki kolom: username, nama", "danger")
#             return redirect(url_for("manage_mahasiswa"))

#         for _, row in df.iterrows():
#             mhs = {
#                 "username": str(row["username"]).strip(),
#                 "nama": str(row["nama"]).strip(),
#                 "role": "mahasiswa",
#             }
#             mongo.db.users.update_one({"username": mhs["username"]}, {"$set": mhs}, upsert=True)

#         flash("Data mahasiswa berhasil diimport", "success")
#     except Exception as e:
#         flash(f"Error import: {e}", "danger")

#     return redirect(url_for("manage_mahasiswa"))




# # Tambah Mahasiswa
# @app.route("/mahasiswa/add", methods=["POST"])
# @login_required
# @role_required("kaprodi", "admin")
# def add_mahasiswa():
#     try:
#         username = request.form.get("username").strip()
#         nama = request.form.get("nama").strip()

#         if not username or not nama:
#             flash("NIM dan Nama wajib diisi", "danger")
#             return redirect(url_for("manage_mahasiswa"))

#         # Default password = NIM (atau bisa kamu atur lain)
#         password = generate_password_hash(username)

#         mahasiswa = {
#             "username": username,
#             "nama": nama,
#             "role": "mahasiswa",
#             "password": password
#         }

#         mongo.db.users.insert_one(mahasiswa)
#         flash("Mahasiswa berhasil ditambahkan", "success")

#     except Exception as e:
#         flash(f"Gagal menambah mahasiswa: {e}", "danger")

#     return redirect(url_for("manage_mahasiswa"))

    
# @app.route("/mahasiswa/edit/<id>", methods=["POST"])
# @login_required
# @role_required("kaprodi", "admin")
# def edit_mahasiswa(id):
#     try:
#         nama = request.form.get("nama")
#         if not nama:
#             flash("Nama tidak boleh kosong", "danger")
#             return redirect(url_for("manage_mahasiswa"))

#         mongo.db.users.update_one(
#             {"_id": ObjectId(id)},
#             {"$set": {"nama": nama}}
#         )
#         flash("Data mahasiswa berhasil diperbarui", "success")
#     except Exception as e:
#         flash(f"Gagal mengubah data: {e}", "danger")

#     return redirect(url_for("manage_mahasiswa"))


# @app.route("/mahasiswa/delete/<id>")
# @login_required
# @role_required("kaprodi", "admin")
# def delete_mahasiswa(id):
#     try:
#         mongo.db.users.delete_one({"_id": ObjectId(id)})
#         flash("Data mahasiswa berhasil dihapus", "success")
#     except Exception as e:
#         flash(f"Gagal menghapus data: {e}", "danger")
#     return redirect(url_for("manage_mahasiswa"))



# mk
@app.route("/mata_kuliah")
@login_required
@role_required("kaprodi", "admin")
def manage_mk():
    mk = list(mongo.db.mata_kuliah.find())
    return render_template("mata_kuliah.html",
                           mata_kuliah=mk, active_page="mata_kuliah")


@app.route("/mata_kuliah/add", methods=["POST"])
@login_required
@role_required("kaprodi", "admin")
def add_mk():
    kode = request.form.get("kode")
    nama = request.form.get("nama")
    semester = request.form.get("semester")

    if not kode or not nama or not semester:
        flash("Semua field wajib diisi", "danger")
        return redirect(url_for("manage_mk"))

    try:
        mk = {
            "kode": kode.strip(),
            "nama": nama.strip(),
            "semester": int(semester),
        }
        mongo.db.mata_kuliah.update_one({"kode": mk["kode"]}, {"$set": mk}, upsert=True)
        flash("Mata kuliah berhasil ditambahkan", "success")
    except Exception as e:
        flash(f"Gagal menambah data: {e}", "danger")

    return redirect(url_for("manage_mk"))


@app.route("/mata_kuliah/edit/<id>", methods=["POST"])
@login_required
@role_required("kaprodi", "admin")
def edit_mk(id):
    try:
        nama = request.form.get("nama")
        semester = request.form.get("semester")

        mongo.db.mata_kuliah.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"nama": nama, "semester": int(semester)}}
        )
        flash("Mata kuliah berhasil diperbarui", "success")
    except Exception as e:
        flash(f"Gagal mengubah data: {e}", "danger")

    return redirect(url_for("manage_mk"))


@app.route("/mata_kuliah/delete/<id>")
@login_required
@role_required("kaprodi", "admin")
def delete_mk(id):
    try:
        mongo.db.mata_kuliah.delete_one({"_id": ObjectId(id)})
        flash("Mata kuliah berhasil dihapus", "success")
    except Exception as e:
        flash(f"Gagal menghapus data: {e}", "danger")

    return redirect(url_for("manage_mk"))


@app.route("/mata_kuliah/import", methods=["POST"])
@login_required
@role_required("kaprodi", "admin")
def import_mk():
    file = request.files.get("file")
    if not file:
        flash("Tidak ada file diunggah", "danger")
        return redirect(url_for("manage_mk"))

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    try:
        if filename.endswith(".csv"):
            df = pd.read_csv(filepath)
        else:
            df = pd.read_excel(filepath)

        required_cols = {"kode", "nama", "semester"}
        if not required_cols.issubset(df.columns):
            flash("File harus memiliki kolom: kode, nama, semester", "danger")
            return redirect(url_for("manage_mk"))

        for _, row in df.iterrows():
            mk = {
                "kode": str(row["kode"]).strip(),
                "nama": str(row["nama"]).strip(),
                "semester": int(row["semester"]),
            }
            mongo.db.mata_kuliah.update_one({"kode": mk["kode"]}, {"$set": mk}, upsert=True)

        flash("Data mata kuliah berhasil diimport", "success")
    except Exception as e:
        flash(f"Error import: {e}", "danger")

    return redirect(url_for("manage_mk"))


# @app.route("/mata_kuliah/export")
# @login_required
# @role_required("kaprodi", "admin")
# def export_mk():
#     mk_list = list(mongo.db.mata_kuliah.find({}, {"_id": 0}))
#     if not mk_list:
#         flash("Tidak ada data mata kuliah untuk diekspor", "warning")
#         return redirect(url_for("manage_mk"))

#     df = pd.DataFrame(mk_list)
#     export_path = os.path.join(app.config["UPLOAD_FOLDER"], "mata_kuliah_export.xlsx")
#     df.to_excel(export_path, index=False)

#     return redirect(f"/{export_path}")




# profil
@app.route("/profile", methods=["GET", "POST"])
@login_required
@role_required("admin", "dosen", "kaprodi", "mahasiswa")
def profil():
    user = mongo.db.users.find_one({"username": session.get("username")})

    if request.method == "POST":
        nama = request.form.get("nama")
        password = request.form.get("password")

        update_data = {"nama": nama}

        if password:  # jika password diisi, hash lalu update
            hashed_password = generate_password_hash(password)
            update_data["password"] = hashed_password

        mongo.db.users.update_one({"username": session.get("username")}, {"$set": update_data})
        flash("Profil berhasil diperbarui!", "success")
        return redirect(url_for("profil"))

    return render_template("profil.html", user=user, active_page="profil")



if __name__ == "__main__":
    app.run(debug=True)
