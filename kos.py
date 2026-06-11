import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import folium
from streamlit_folium import st_folium
import plotly.express as px
from PIL import Image
import io

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="Dashboard Kos Mahasiswa", layout="wide")

# ------------------ CSS CUSTOM ------------------
st.markdown("""
<style>
    /* Warna filter sidebar */
    [data-testid="stSidebar"] {
        background-color: #0051A8;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    [data-testid="stSidebar"] .stSlider label,
    [data-testid="stSidebar"] .stMultiSelect label,
    [data-testid="stSidebar"] .stSelectbox label {
        color: white !important;
    }
    /* Kotak border untuk setiap section */
    .box {
        border: 2px solid #4A90E2;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        background-color: #f9f9ff;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }
    .box-title {
        font-size: 1.3rem;
        font-weight: bold;
        color: #004B87;
        margin-bottom: 15px;
        border-left: 5px solid #5B9BD5;
        padding-left: 12px;
    }
    .kpi-card {
        background-color: #4A90E2;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        color: white;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
    }
    .kpi-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .kpi-value {
        font-size: 1.8rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ------------------ DATA DUMMY ------------------
lokasi_available = ["Keputih", "Mulyosari", "Gebang"]
tipe_kos_available = ["Putri", "Putra", "Umum"]

data_kos = {
    "nama_kos": ["Kos Mawar Indah", "Kos Melati Asri", "Kos Anggrek Permai", "Kos Flamboyan", "Kos Sakura"],
    "lokasi": ["Keputih", "Keputih", "Mulyosari", "Gebang", "Mulyosari"],
    "tipe_kos": ["Putri", "Putri", "Umum", "Putra", "Putri"],
    "harga": [1200000, 1300000, 1100000, 1450000, 1250000],
    "kapasitas_kamar": [50, 30, 40, 25, 35],
    "jarak_ke_its_m": [300, 450, 800, 1200, 600],
    "indeks_kepuasan": [4.2, 4.5, 3.9, 4.0, 4.3],
    "kontak": ["081234567890", "081298765432", "081355667788", "081277889900", "081344556677"],
    "lat": [-7.279, -7.278, -7.280, -7.275, -7.281],
    "lon": [112.795, 112.796, 112.794, 112.798, 112.793],
}
df_kos = pd.DataFrame(data_kos)

# Rating aspek (skala 1-10)
aspek_rating = {
    "Kos Mawar Indah": {"Kebersihan": 5.3, "Kenyamanan": 6.5, "Keamanan": 6.7, "Fasilitas": 5.3},
    "Kos Melati Asri": {"Kebersihan": 6.8, "Kenyamanan": 7.0, "Keamanan": 6.5, "Fasilitas": 6.2},
    "Kos Anggrek Permai": {"Kebersihan": 5.0, "Kenyamanan": 5.5, "Keamanan": 6.0, "Fasilitas": 5.2},
    "Kos Flamboyan": {"Kebersihan": 6.0, "Kenyamanan": 6.3, "Keamanan": 6.8, "Fasilitas": 5.9},
    "Kos Sakura": {"Kebersihan": 6.5, "Kenyamanan": 6.9, "Keamanan": 6.4, "Fasilitas": 6.1},
}

# Harga sebagai aspek (dinormalisasi: semakin murah semakin baik)
harga_rating = {
    "Kos Mawar Indah": 8.5,
    "Kos Melati Asri": 7.8,
    "Kos Anggrek Permai": 9.0,
    "Kos Flamboyan": 6.5,
    "Kos Sakura": 8.0,
}

# Indikator per aspek
indikator_aspek = {
    "Kos Mawar Indah": {
        "Kebersihan": {"Kamar mandi": 5.0, "Kamar tidur": 5.5},
        "Kenyamanan": {"Sirkulasi udara": 6.0, "Pencahayaan": 7.0},
    },
    "Kos Melati Asri": {
        "Kebersihan": {"Kamar mandi": 7.0, "Kamar tidur": 6.8},
        "Kenyamanan": {"Sirkulasi udara": 7.2, "Pencahayaan": 7.5},
    }
}
for kos in df_kos["nama_kos"]:
    if kos not in indikator_aspek:
        indikator_aspek[kos] = {
            "Kebersihan": {"Kamar mandi": 5.5, "Kamar tidur": 5.5},
            "Kenyamanan": {"Sirkulasi udara": 6.0, "Pencahayaan": 6.5},
            "Keamanan": {"Keamanan lingkungan": 6.5},
            "Fasilitas": {"AC": 6.0, "WiFi": 5.0},
        }

keluhan_data = {
    "Kos Mawar Indah": ["WiFi Lemot", "Air mandi kecil", "Suara berisik"],
    "Kos Melati Asri": ["Air mandi kecil", "Tempat jemur sempit", "WiFi lemot"],
    "Kos Anggrek Permai": ["Listrik padam", "Banyak nyamuk", "Kamar bau"],
    "Kos Flamboyan": ["Parkir sempit", "Suara berisik", "Air keruh"],
    "Kos Sakura": ["WiFi lemot", "Kamar mandi kotor", "Lokasi jauh"],
}

asal_penghuni = {
    "Kos Mawar Indah": {"Jawa Timur": 45, "Jawa Tengah": 25, "Jawa Barat": 15, "Lainnya": 15},
    "Kos Melati Asri": {"Jawa Timur": 50, "Jawa Tengah": 20, "Jawa Barat": 15, "Lainnya": 15},
    "Kos Anggrek Permai": {"Jawa Timur": 40, "Jawa Tengah": 30, "Jawa Barat": 20, "Lainnya": 10},
    "Kos Flamboyan": {"Jawa Timur": 55, "Jawa Tengah": 20, "Jawa Barat": 10, "Lainnya": 15},
    "Kos Sakura": {"Jawa Timur": 48, "Jawa Tengah": 22, "Jawa Barat": 12, "Lainnya": 18},
}

peraturan = {
    "Kos Mawar Indah": ["Bayar DP 3 bulan di muka", "Jam malam 22:00 WIB", "Dilarang membawa tamu laki-laki"],
    "Kos Melati Asri": ["Tamu hanya sampai jam 20:00", "Dilarang memasak di kamar", "Parkir wajib di area"],
    "Kos Anggrek Permai": ["Listrik token", "Jam malam 23:00", "Cuci di tempat laundry"],
    "Kos Flamboyan": ["Kunjungan terbatas", "Deposit 1 bulan", "Tidak boleh bawa hewan"],
    "Kos Sakura": ["Jam malam 21:00", "Dilarang merokok di dalam", "Buang sampah terjadwal"],
}

fasilitas = {
    "Kos Mawar Indah": ["AC", "Wi-Fi", "Kamar Mandi Dalam", "Cuci Setrika"],
    "Kos Melati Asri": ["AC", "Wi-Fi", "Kamar Mandi Luar", "Dapur Umum", "TV"],
    "Kos Anggrek Permai": ["Kipas Angin", "Wi-Fi", "Kamar Mandi Dalam", "Air Panas"],
    "Kos Flamboyan": ["AC", "Wi-Fi", "Kamar Mandi Dalam", "Laundry"],
    "Kos Sakura": ["AC", "Wi-Fi", "Kamar Mandi Dalam", "Parkir Luas", "CCTV"],
}

wordcloud_text = {
    "Kos Mawar Indah": "Wifi lemot air kecil berisik asri nyaman bersih aman murah strategis",
    "Kos Melati Asri": "nyaman bersih AC strategis wifi bagus luas parkir",
    "Kos Anggrek Permai": "listrik padam nyamuk bau gelap sempit",
    "Kos Flamboyan": "berisik parkir sempit keruh ramah bersih",
    "Kos Sakura": "wifi lemot kamar mandi kotor jauh tenang bersih",
}

# ------------------ SIDEBAR FILTER ------------------
st.sidebar.header("🔍 Filter Kos")
lokasi_filter = st.sidebar.multiselect("Lokasi", lokasi_available, default=lokasi_available)
tipe_filter = st.sidebar.multiselect("Tipe Kos", tipe_kos_available, default=tipe_kos_available)
range_harga = st.sidebar.slider("Range Harga (Rp)", 1000000, 2000000, (1000000, 1500000))
filter_kos_nama = st.sidebar.selectbox("Pilih Kos (opsional)", ["Semua"] + list(df_kos["nama_kos"]))

df_filtered = df_kos[
    (df_kos["lokasi"].isin(lokasi_filter)) &
    (df_kos["tipe_kos"].isin(tipe_filter)) &
    (df_kos["harga"] >= range_harga[0]) & (df_kos["harga"] <= range_harga[1])
]

if filter_kos_nama != "Semua":
    df_filtered = df_filtered[df_filtered["nama_kos"] == filter_kos_nama]
    selected_kos = filter_kos_nama
else:
    selected_kos = None

# ------------------ KPI SECTION ------------------
# ------------------ KPI SECTION (Ukuran Seragam) ------------------
st.markdown("## Dashboard Kos Mahasiswa")
st.markdown("---")

# CSS untuk menyamakan ukuran KPI
st.markdown("""
<style>
    /* Container KPI grid */
    .kpi-container {
        display: flex;
        gap: 20px;
        margin-bottom: 20px;
        flex-wrap: wrap;
    }
    /* Setiap KPI card ukuran tetap */
    .kpi-card-uniform {
        background-color: #4A90E2;
        border-radius: 12px;
        padding: 20px 10px;
        text-align: center;
        color: white;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
        flex: 1;
        min-width: 180px;
        height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .kpi-label-uniform {
        font-size: 0.9rem;
        opacity: 0.9;
        margin-bottom: 8px;
    }
    .kpi-value-uniform {
        font-size: 1.5rem;
        font-weight: bold;
        word-wrap: break-word;
        line-height: 1.3;
    }
    @media (max-width: 768px) {
        .kpi-card-uniform {
            min-width: 150px;
            height: 110px;
        }
        .kpi-value-uniform {
            font-size: 1.2rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Membuat KPI dengan ukuran seragam menggunakan HTML
if selected_kos:
    kos_data = df_filtered.iloc[0]
    kpi_nama = kos_data["nama_kos"]
    kpi_aspek_terbaik = max(aspek_rating[kpi_nama], key=aspek_rating[kpi_nama].get)
    kpi_kapasitas = kos_data["kapasitas_kamar"]
    kpi_jarak = kos_data["jarak_ke_its_m"]
    
    kpi_html = f"""
    <div class="kpi-container">
        <div class="kpi-card-uniform">
            <div class="kpi-label-uniform"> Kos Terpilih</div>
            <div class="kpi-value-uniform">{kpi_nama}</div>
        </div>
        <div class="kpi-card-uniform">
            <div class="kpi-label-uniform"> Aspek Terbaik</div>
            <div class="kpi-value-uniform">{kpi_aspek_terbaik}</div>
        </div>
        <div class="kpi-card-uniform">
            <div class="kpi-label-uniform"> Kapasitas</div>
            <div class="kpi-value-uniform">{kpi_kapasitas} kamar</div>
        </div>
        <div class="kpi-card-uniform">
            <div class="kpi-label-uniform"> Jarak ke ITS</div>
            <div class="kpi-value-uniform">{kpi_jarak} m</div>
        </div>
    </div>
    """
    st.markdown(kpi_html, unsafe_allow_html=True)
    
else:
    if not df_filtered.empty:
        top_kos = df_filtered.loc[df_filtered["indeks_kepuasan"].idxmax()]
        top_aspek = max(aspek_rating[top_kos["nama_kos"]], key=aspek_rating[top_kos["nama_kos"]].get)
        
        kpi_html = f"""
        <div class="kpi-container">
            <div class="kpi-card-uniform">
                <div class="kpi-label-uniform"> Kos Top 1</div>
                <div class="kpi-value-uniform">{top_kos["nama_kos"]}</div>
            </div>
            <div class="kpi-card-uniform">
                <div class="kpi-label-uniform"> Aspek Tertinggi</div>
                <div class="kpi-value-uniform">{top_aspek}</div>
            </div>
            <div class="kpi-card-uniform">
                <div class="kpi-label-uniform"> Kapasitas</div>
                <div class="kpi-value-uniform">{top_kos["kapasitas_kamar"]} kamar</div>
            </div>
            <div class="kpi-card-uniform">
                <div class="kpi-label-uniform"> Jarak ke ITS</div>
                <div class="kpi-value-uniform">{top_kos["jarak_ke_its_m"]} m</div>
            </div>
        </div>
        """
        st.markdown(kpi_html, unsafe_allow_html=True)
    else:
        kpi_html = """
        <div class="kpi-container">
            <div class="kpi-card-uniform">
                <div class="kpi-label-uniform"> Kos Terpilih</div>
                <div class="kpi-value-uniform">-</div>
            </div>
            <div class="kpi-card-uniform">
                <div class="kpi-label-uniform"> Aspek Terbaik</div>
                <div class="kpi-value-uniform">-</div>
            </div>
            <div class="kpi-card-uniform">
                <div class="kpi-label-uniform"> Kapasitas</div>
                <div class="kpi-value-uniform">-</div>
            </div>
            <div class="kpi-card-uniform">
                <div class="kpi-label-uniform"> Jarak ke ITS</div>
                <div class="kpi-value-uniform">-</div>
            </div>
        </div>
        """
        st.markdown(kpi_html, unsafe_allow_html=True)
# ------------------ MAIN CONTENT PER KOS ------------------
if not df_filtered.empty:
    for _, kos in df_filtered.iterrows():
        nama = kos["nama_kos"]
        
        # BOX 1: Keluhan + Bar Chart Aspek + Indikator
        with st.container():
            st.markdown(f'<div class="box"><div class="box-title"> {nama}</div>', unsafe_allow_html=True)
            
            # Keluhan (Pareto)
            st.markdown("####  Keluhan Penghuni (Pareto)")
            keluhan_series = pd.Series(keluhan_data[nama]).value_counts().reset_index()
            keluhan_series.columns = ["Keluhan", "Frekuensi"]
            fig = px.bar(keluhan_series, x="Keluhan", y="Frekuensi", title="Keluhan Terbanyak", color_discrete_sequence=["#4A90E2"])
            st.plotly_chart(fig, use_container_width=True)
            
            # Bar chart aspek
            st.markdown("####  Rating Aspek Kos")
            df_aspek = pd.DataFrame(aspek_rating[nama].items(), columns=["Aspek", "Skor"])
            fig_aspek = px.bar(df_aspek, x="Aspek", y="Skor", color="Aspek", color_discrete_sequence=["#5B9BD5", "#4A90E2", "#0051A8", "#004B87"])
            st.plotly_chart(fig_aspek, use_container_width=True)
            
            # Indikator per aspek
            st.markdown("####  Indikator Setiap Aspek")
            for aspek, indikator_dict in indikator_aspek[nama].items():
                with st.expander(f"Detail {aspek}"):
                    st.dataframe(pd.DataFrame(indikator_dict.items(), columns=["Indikator", "Skor"]), use_container_width=True)
            
            # Pie Chart & Wordcloud (bersebelahan)
            col_kiri, col_kanan = st.columns(2)
            with col_kiri:
                st.markdown("####  Asal Penghuni")
                df_asal = pd.DataFrame(asal_penghuni[nama].items(), columns=["Daerah", "Persentase"])
                fig_pie = px.pie(df_asal, values="Persentase", names="Daerah", title="Asal Penghuni", color_discrete_sequence=["#0051A8", "#004B87", "#4A90E2", "#5B9BD5"])
                st.plotly_chart(fig_pie, use_container_width=True)
            with col_kanan:
                st.markdown("####  Wordcloud Ulasan")
                wc = WordCloud(width=800, height=400, background_color="white", colormap="Blues").generate(wordcloud_text[nama])
                fig_wc, ax = plt.subplots(figsize=(5, 3))
                ax.imshow(wc, interpolation="bilinear")
                ax.axis("off")
                st.pyplot(fig_wc)
            
            # Fasilitas & Peraturan (bersebelahan)
            col_fas, col_per = st.columns(2)
            with col_fas:
                st.markdown("####  Fasilitas Kos")
                for fas in fasilitas[nama]:
                    st.write(f" {fas}")
            with col_per:
                st.markdown("####  Peraturan Kos")
                for rule in peraturan[nama]:
                    st.write(f" {rule}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # BOX 2: Peta, Kontak, Harga, Foto
        with st.container():
            st.markdown('<div class="box">', unsafe_allow_html=True)
            col_peta, col_info = st.columns([1, 1])
            with col_peta:
                st.markdown("####  Peta Lokasi Kos")
                m = folium.Map(location=[kos["lat"], kos["lon"]], zoom_start=15)
                folium.Marker([kos["lat"], kos["lon"]], popup=nama, tooltip=nama, icon=folium.Icon(color="blue", icon="home")).add_to(m)
                st_folium(m, width=400, height=300)
            with col_info:
                st.markdown("#### 📞 Kontak & Info")
                st.write(f"💰 **Harga:** Rp {kos['harga']:,} / bulan")
                st.write(f"📱 **Kontak Bapak/Ibu Kos:** {kos['kontak']}")
                st.write(f"🏠 **Kapasitas:** {kos['kapasitas_kamar']} kamar")
                st.write(f"📏 **Jarak ke ITS:** {kos['jarak_ke_its_m']} meter")
                st.write(f"🚻 **Tipe Kos:** {kos['tipe_kos']}")
            st.markdown("####  Foto Dokumentasi")
            col_foto1, col_foto2, col_foto3 = st.columns(3)
            with col_foto1:
                st.image("assets/Screenshot 2026-06-11 075029.png", caption="Suasana Kamar", use_container_width=True)
            with col_foto2:
                st.image("assets/Screenshot 2026-06-11 075051.png", caption="Fasilitas Kamar Mandi", use_container_width=True)
            with col_foto3:
                st.image("assets/Screenshot 2026-06-11 075127.png", caption="Area Umum & Fasilitas", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

else:
    st.warning(" Tidak ada kos yang sesuai dengan filter yang dipilih.")

# ------------------ MCDM AHP SECTION ------------------
st.markdown("---")
st.markdown("##  Analisis MCDM (AHP) - Rekomendasi Kos")

with st.container():
    st.markdown('<div class="box">', unsafe_allow_html=True)
    st.markdown("### Tentukan Bobot Prioritas (Skala Saaty 1-9)")
    st.caption("1 = Sama penting, 9 = Aspek kiri sangat lebih penting dari aspek kanan")
    
    aspek_list = ["Kenyamanan", "Kebersihan", "Keamanan", "Fasilitas", "Harga"]
    
    def get_pairwise_input(aspek1, aspek2):
        return st.slider(f"**{aspek1}** vs **{aspek2}**", 1.0, 9.0, 1.0, step=0.5, key=f"{aspek1}_{aspek2}")
    
    pair_values = {}
    for i in range(len(aspek_list)):
        for j in range(i+1, len(aspek_list)):
            val = get_pairwise_input(aspek_list[i], aspek_list[j])
            pair_values[(aspek_list[i], aspek_list[j])] = val
            pair_values[(aspek_list[j], aspek_list[i])] = 1/val
    for a in aspek_list:
        pair_values[(a, a)] = 1.0
    
    if st.button(" Hitung Bobot & Tampilkan Rekomendasi Kos", use_container_width=True):
        matriks = np.array([[pair_values[(i,j)] for j in aspek_list] for i in aspek_list])
        eig_vals, eig_vecs = np.linalg.eig(matriks)
        max_eig_index = np.argmax(eig_vals)
        bobot = np.abs(eig_vecs[:, max_eig_index])
        bobot = bobot / bobot.sum()
        bobot_dict = {aspek_list[i]: bobot[i] for i in range(len(aspek_list))}
        
        # Hitung skor akhir tiap kos
        df_skor = df_kos.copy()
        skor_total = []
        for _, kos in df_kos.iterrows():
            nama_k = kos["nama_kos"]
            rating_aspek = aspek_rating[nama_k]
            total = 0
            for asp in ["Kenyamanan", "Kebersihan", "Keamanan", "Fasilitas"]:
                total += bobot_dict[asp] * (rating_aspek[asp] / 10)
            total += bobot_dict["Harga"] * (harga_rating[nama_k] / 10)
            skor_total.append(total)
        df_skor["Skor_AHP"] = skor_total
        df_skor = df_skor.sort_values("Skor_AHP", ascending=False)
        
        st.success(" Bobot berhasil dihitung! Berikut rekomendasi kos untuk Anda:")
        st.dataframe(df_skor[["nama_kos", "lokasi", "harga", "Skor_AHP"]], use_container_width=True)
        
        best = df_skor.iloc[0]
        st.balloons()
        st.markdown(f"""
        <div style="background-color:#004B87; padding:20px; border-radius:15px; color:white; text-align:center">
            <h2> KOS REKOMENDASI UNTUK ANDA </h2>
            <h1>{best['nama_kos']}</h1>
            <h3> {best['lokasi']} |  Rp {best['harga']:,}/bulan</h3>
            <h4> Skor AHP: {best['Skor_AHP']:.3f}</h4>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
