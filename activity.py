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

# Fungsi konversi dan validasi waktu
def parse_jam(input_str):
    input_str = input_str.strip().replace(".", ":")
    try:
        waktu = datetime.strptime(input_str, "%H:%M")
        return waktu.strftime("%H:%M")
    except ValueError:
        return None

# Fungsi hitung durasi dalam jam desimal
def hitung_durasi(mulai, selesai):
    mulai_dt = datetime.strptime(mulai, "%H:%M")
    selesai_dt = datetime.strptime(selesai, "%H:%M")
    if selesai_dt < mulai_dt:
        selesai_dt += pd.Timedelta(days=1)
    durasi = selesai_dt - mulai_dt
    return round(durasi.total_seconds() / 3600, 2)

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

# Judul aplikasi
st.markdown("<h2 style='text-align: center;'>📋 Daily Activity Recorder</h2>", unsafe_allow_html=True)

# Form input
with st.form("form_aktivitas", clear_on_submit=True):
    st.markdown("### ✏️ Input Aktivitas")

    aktivitas = st.text_input("Aktivitas", placeholder="Contoh: Pemeriksaan panel listrik", label_visibility="collapsed")
    posisi = st.text_input("Posisi Aktivitas", placeholder="Contoh: Area Genset", label_visibility="collapsed")

    jam_mulai_input = st.text_input("Jam Mulai", placeholder="Contoh: 08.30 atau 08:30", label_visibility="collapsed")
    jam_selesai_input = st.text_input("Jam Selesai", placeholder="Contoh: 10.15 atau 10:15", label_visibility="collapsed")

    gambar = st.camera_input("📷 Dokumentasi Gambar")

    submit = st.form_submit_button("✅ Simpan Data")

    if submit:
        jam_mulai = parse_jam(jam_mulai_input)
        jam_selesai = parse_jam(jam_selesai_input)

        if not aktivitas or not posisi or not jam_mulai or not jam_selesai or not gambar:
            st.warning("⚠️ Mohon isi semua data dan pastikan format jam benar.")
        else:
            tanggal = datetime.now().strftime("%Y-%m-%d")
            durasi = hitung_durasi(jam_mulai, jam_selesai)

            # Buat nama file dari aktivitas
            nama_aktivitas_bersih = aktivitas.strip().lower().replace(" ", "_").replace("/", "_")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{nama_aktivitas_bersih}_{timestamp}.jpg"
            path_gambar = os.path.join(IMAGE_FOLDER, filename)
            with open(path_gambar, "wb") as f:
                f.write(gambar.getbuffer())

            # Simpan ke CSV
            simpan_data(tanggal, aktivitas, posisi, jam_mulai, jam_selesai, durasi, filename)
            st.success("✅ Data berhasil disimpan.")

# Tampilkan data
st.markdown("### 📑 Riwayat Aktivitas")
data = pd.read_csv(CSV_FILE)
st.dataframe(data, use_container_width=True)

# Tombol download
def convert_df(df):
    return df.to_csv(index=False).encode("utf-8")

csv_data = convert_df(data)
st.download_button("⬇️ Download CSV", data=csv_data, file_name="daily_activity.csv", mime="text/csv")
