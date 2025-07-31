import streamlit as st
import pandas as pd
from datetime import datetime
import os

# File dan folder
CSV_FILE = "daily_activity.csv"
IMAGE_FOLDER = "images"
os.makedirs(IMAGE_FOLDER, exist_ok=True)

# Inisialisasi CSV jika belum ada
if not os.path.exists(CSV_FILE):
    df_init = pd.DataFrame(columns=[
        "Tanggal", "Aktivitas", "Posisi", "Jam Mulai", "Jam Selesai", "Durasi (Jam)", "Foto"
    ])
    df_init.to_csv(CSV_FILE, index=False)

# Fungsi menghitung durasi dalam jam desimal
def hitung_durasi(mulai, selesai):
    mulai_dt = datetime.strptime(mulai, "%H:%M")
    selesai_dt = datetime.strptime(selesai, "%H:%M")
    if selesai_dt < mulai_dt:
        selesai_dt += pd.Timedelta(days=1)  # untuk aktivitas yang melewati tengah malam
    durasi = selesai_dt - mulai_dt
    durasi_jam = durasi.total_seconds() / 3600
    return round(durasi_jam, 2)

# Fungsi simpan data
def simpan_data(tanggal, aktivitas, posisi, jam_mulai, jam_selesai, durasi, foto_filename):
    data_baru = pd.DataFrame({
        "Tanggal": [tanggal],
        "Aktivitas": [aktivitas],
        "Posisi": [posisi],
        "Jam Mulai": [jam_mulai],
        "Jam Selesai": [jam_selesai],
        "Durasi (Jam)": [durasi],
        "Foto": [foto_filename]
    })
    data_baru.to_csv(CSV_FILE, mode="a", header=False, index=False)

# UI Streamlit
st.title("🗒️ Pencatatan Daily Activity")

aktivitas = st.text_input("📝 Aktivitas", placeholder="Contoh: Pemeriksaan panel listrik")
posisi = st.text_input("📍 Posisi Aktivitas", placeholder="Contoh: Area Genset")

jam_mulai = st.time_input("⏱️ Jam Mulai")
jam_selesai = st.time_input("⏲️ Jam Selesai")

gambar = st.camera_input("📷 Dokumentasi Gambar (bisa pakai kamera atau upload)")

if st.button("✅ Simpan Data"):
    if aktivitas and posisi and gambar:
        tanggal = datetime.now().strftime("%Y-%m-%d")
        mulai_str = jam_mulai.strftime("%H:%M")
        selesai_str = jam_selesai.strftime("%H:%M")
        durasi = hitung_durasi(mulai_str, selesai_str)

        # Simpan gambar
        filename = f"{tanggal}_{datetime.now().strftime('%H%M%S')}.jpg"
        path_gambar = os.path.join(IMAGE_FOLDER, filename)
        with open(path_gambar, "wb") as f:
            f.write(gambar.getbuffer())

        # Simpan data ke CSV
        simpan_data(tanggal, aktivitas, posisi, mulai_str, selesai_str, durasi, filename)

        st.success("✅ Data berhasil disimpan.")
    else:
        st.warning("❗ Semua kolom wajib diisi dan gambar harus diunggah!")

# Tampilkan data CSV
st.subheader("📋 Riwayat Aktivitas")
data = pd.read_csv(CSV_FILE)
st.dataframe(data, use_container_width=True)

# Download tombol CSV
def convert_df(df):
    return df.to_csv(index=False).encode("utf-8")

csv_data = convert_df(data)
st.download_button("⬇️ Download CSV", data=csv_data, file_name="daily_activity.csv", mime="text/csv")
