import streamlit as st
import pandas as pd
from datetime import datetime

# ==========================================
# BAGIAN 1: LOGIKA & OOP
# ==========================================

class Transaksi:
    def __init__(self, nama, jenis, kategori, nominal, metode):
        self.nama = nama
        self.jenis = jenis
        self.kategori = kategori
        self.nominal = nominal
        self.metode = metode 
        self.waktu = datetime.now().strftime("%Y-%m-%d %H:%M")

class KeuanganManager:
    def __init__(self):
        if 'database' not in st.session_state:
            st.session_state['database'] = []

    def tambah_data(self, nama, jenis, kategori, nominal, metode):
        nama_bersih = nama.strip().title()
        transaksi_baru = Transaksi(nama_bersih, jenis, kategori, nominal, metode)
        st.session_state['database'].append(transaksi_baru)

    def ambil_semua_data(self):
        data_list = []
        for item in st.session_state['database']:
            data_list.append({
                "Waktu": item.waktu,
                "Nama": item.nama,
                "Jenis": item.jenis,
                "Kategori": item.kategori,
                "Nominal": item.nominal,
                "Metode": item.metode 
            })
        return data_list

    def hitung_ringkasan(self):
        total_masuk = 0
        total_keluar = 0
        for item in st.session_state['database']:
            if item.jenis == "Pemasukan":
                total_masuk += item.nominal
            elif item.jenis == "Pengeluaran":
                total_keluar += item.nominal
        return total_masuk, total_keluar, total_masuk - total_keluar

    def hapus_semua(self):
        st.session_state['database'] = []

# --- FUNGSI HELPER ---
def format_ribuan(nilai):
    return f"{nilai:,.0f}".replace(",", ".")

def proses_input_uang(teks):
    if not teks: return 0
    teks = teks.lower().replace("rp", "").replace(" ", "")
    faktor = 1
    if "jt" in teks:
        faktor = 1000000
        teks = teks.replace("jt", "")
    elif "k" in teks or "rb" in teks:
        faktor = 1000
        teks = teks.replace("k", "").replace("rb", "")
    teks = teks.replace(".", "").replace(",", ".")
    try:
        angka = float(teks) * faktor
        return int(angka)
    except ValueError:
        return 0

# ==========================================
# BAGIAN 2: TAMPILAN (UI)
# ==========================================

st.set_page_config(page_title="Dompet Pintar", page_icon="💸", layout="wide")
manager = KeuanganManager()

st.title("💸 Dompet Pintar: Pencatat Keuangan")
st.write("Tips: Ketik '20k' untuk 20.000")
st.markdown("---")

col1, col2 = st.columns([1, 2])

# --- INPUT DATA ---
with col1:
    st.header("📝 Input Data")
    
    # 1. Pilih Jenis (Di luar Form agar interaktif)
    jenis = st.radio("Jenis Transaksi", ["Pengeluaran", "Pemasukan"], horizontal=True)
    
    # 2. Logika Form Dinamis (Kategori & Placeholder)
    if jenis == "Pemasukan":
        opsi_kategori = ["Cash", "Cashless"]
        tampil_opsi_metode = False 
        # REVISI DISINI: Placeholder khusus Pemasukan
        placeholder_nama = "Contoh: Gaji Bulanan / Transfer dari Ortu / Bonus"
    else:
        opsi_kategori = ["Makan", "Transport", "Pulsa", "Jajan", "Tabungan", "Lainnya"]
        tampil_opsi_metode = True 
        # REVISI DISINI: Placeholder khusus Pengeluaran
        placeholder_nama = "Contoh: Beli Nasi Padang / Bayar Kos"
    
    with st.form("form_transaksi", clear_on_submit=True):
        # Teks placeholder berubah sesuai variabel di atas
        nama = st.text_input("Keterangan", placeholder=placeholder_nama)
        
        kategori = st.selectbox("Kategori", opsi_kategori)
        
        # Logika Metode Pembayaran
        metode_pilih = "Cash" 
        if tampil_opsi_metode:
            st.write("Metode Pembayaran:")
            metode_pilih = st.radio("Pilih Metode", ["Cash", "Cashless"], horizontal=True, label_visibility="collapsed")
        else:
            metode_pilih = kategori 
            
        input_nominal = st.text_input("Nominal (Rp)", placeholder="Cth: 15k, 50rb")
        
        submitted = st.form_submit_button("Simpan Transaksi")
        
        if submitted:
            nominal_fix = proses_input_uang(input_nominal)
            
            if nama and nominal_fix > 0:
                manager.tambah_data(nama, jenis, kategori, nominal_fix, metode_pilih)
                st.success(f"Berhasil: {kategori} ({metode_pilih}) - Rp {format_ribuan(nominal_fix)}")
            else:
                st.error("Nama wajib diisi dan nominal harus benar.")

    if st.button("Hapus Semua Data"):
        manager.hapus_semua()
        st.rerun()

# --- DASHBOARD ---
with col2:
    st.header("📊 Ringkasan")
    masuk, keluar, saldo = manager.hitung_ringkasan()
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Pemasukan", f"Rp {format_ribuan(masuk)}")
    m2.metric("Pengeluaran", f"Rp {format_ribuan(keluar)}")
    m3.metric("Saldo", f"Rp {format_ribuan(saldo)}")
    
    st.divider()
    
    data = manager.ambil_semua_data()
    if data:
        df = pd.DataFrame(data)
        df_tampil = df.copy()
        
        # Format Nominal
        df_tampil['Nominal'] = df_tampil['Nominal'].apply(lambda x: f"Rp {format_ribuan(x)}")
        
        # Urutan Kolom
        kolom_urut = ["Waktu", "Nama", "Jenis", "Kategori", "Metode", "Nominal"]
        df_tampil = df_tampil[kolom_urut]
        
        def warna_jenis(val):
            return f'background-color: {"#ffcccb" if val == "Pengeluaran" else "#90ee90"}'
            
        st.dataframe(df_tampil.style.map(warna_jenis, subset=['Jenis']), use_container_width=True, hide_index=True)
    else:
        st.info("Belum ada data.")