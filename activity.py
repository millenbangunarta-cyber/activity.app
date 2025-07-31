import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image
from io import BytesIO
from pathlib import Path
import zipfile

# Konfigurasi file & folder
CSV_FILE = "activity_log.csv"
IMAGE_FOLDER = "images"
os.makedirs(IMAGE_FOLDER, exist_ok=True)

# Konfigurasi URL lokal agar gambar bisa diakses via <a> link
st.markdown(
    f"""<base href="{Path().absolute().as_uri()}/">""",
    unsafe_allow_html=True
)

# Fungsi bantu
def format_jam_manual(input_str):
    input_str = input_str.strip().replace(".", ":")
    try:
        datetime.strptime(input_str, "%H:%M")
        return input_str
    except ValueError:
        return None

def hitung_durasi(mulai, selesai):
    mulai_dt = datetime.strptime(mulai, "%H:%M")
    selesai_dt = datetime.strptime(selesai, "%H:%M")
    if selesai_dt < mulai_dt:
        selesai_dt += pd.Timedelta(days=1)
    durasi = selesai_dt - mulai_dt
    return round(durasi.total_seconds() / 3600, 2)

def buat_zip_gambar(folder_path):
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for filename in os.listdir(folder_path):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                filepath = os.path.join(folder_path, filename)
                zip_file.write(filepath, arcname=filename)
    buffer.seek(0)
    return buffer

# Judul
st.title("📋 Aplikasi Pencatatan Aktivitas Harian")

# Form Input
with st.form("activity_form"):
    aktivitas = st.text_input("📝 Aktivitas")
    posisi = st.text_input("📍 Posisi Aktivitas")
    jam_mulai_input = st.text_input("⏱️ Jam Mulai (misal: 08.30)")
    jam_selesai_input = st.text_input("⏲️ Jam Selesai (misal: 10.15)")
    foto = st.camera_input("📷 Foto Dokumentasi")

    submitted = st.form_submit_button("✅ Simpan Aktivitas")

if submitted:
    jam_mulai = format_jam_manual(jam_mulai_input)
    jam_selesai = format_jam_manual(jam_selesai_input)

    if not all([aktivitas, posisi, jam_mulai, jam_selesai, foto]):
        st.error("⚠️ Semua data harus diisi dan format jam harus benar.")
    else:
        tanggal = datetime.now().strftime("%Y-%m-%d")
        durasi = hitung_durasi(jam_mulai, jam_selesai)

        # Simpan foto
        waktu_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        nama_file = f"{aktivitas.strip().lower().replace(' ', '_')}_{waktu_str}.jpg"
        path_gambar = os.path.join(IMAGE_FOLDER, nama_file)
        image = Image.open(foto)
        image.save(path_gambar)

        # Simpan ke CSV
        row = {
            "Tanggal": tanggal,
            "Aktivitas": aktivitas,
            "Posisi": posisi,
            "Jam Mulai": jam_mulai,
            "Jam Selesai": jam_selesai,
            "Durasi (Jam)": durasi,
            "Foto": nama_file
        }
        df = pd.DataFrame([row])
        if os.path.exists(CSV_FILE):
            df.to_csv(CSV_FILE, mode='a', index=False, header=False)
        else:
            df.to_csv(CSV_FILE, index=False)

        st.success("✅ Data berhasil disimpan!")

# Tampilkan Data Aktivitas
st.markdown("---")
st.subheader("📑 Riwayat Aktivitas")

if os.path.exists(CSV_FILE):
    data = pd.read_csv(CSV_FILE)
    st.dataframe(data, use_container_width=True)

    # Preview Gambar
    st.markdown("### 🖼️ Dokumentasi Gambar")
    for i, row in data.iterrows():
        st.markdown(f"**{row['Tanggal']} - {row['Aktivitas']}**")
        st.markdown(f"🕒 {row['Jam Mulai']} - {row['Jam Selesai']} | ⏱️ {row['Durasi (Jam)']} jam")
        st.markdown(f"📍 {row['Posisi']}")

        image_path = os.path.join(IMAGE_FOLDER, row['Foto'])
        if os.path.exists(image_path):
            st.image(image_path, width=250, caption=row['Foto'])
            st.markdown(f"[🔗 Buka Gambar di Tab Baru](images/{row['Foto']})", unsafe_allow_html=True)
        else:
            st.warning("⚠️ Gambar tidak ditemukan.")
        st.markdown("---")

    # Download CSV
    with open(CSV_FILE, "rb") as f:
        st.download_button("⬇️ Download CSV", data=f, file_name="activity_log.csv", mime="text/csv")

    # Download Semua Gambar
    zip_data = buat_zip_gambar(IMAGE_FOLDER)
    st.download_button("📦 Download Semua Gambar (.zip)", data=zip_data, file_name="dokumentasi_gambar.zip", mime="application/zip")
else:
    st.info("Belum ada data aktivitas tersimpan.")
