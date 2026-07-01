import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import pickle
import json
import re

# ==========================================
# 1. MANAGEMENT LAYOUT & THEME CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="GovReady - SPK Transformasi Digital Daerah",
    layout="wide"
)

# Custom Corporate Dashboard CSS
st.markdown("""
    <style>
    .reportview-container { background: #FFFFFF; }
    html, body, [data-testid="stSidebar"] { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }
    .govready-title { font-size: 36px !important; font-weight: 800; color: #0F172A; margin-bottom: 25px; letter-spacing: -0.5px; line-height: 1.2; }
    .section-title { font-size: 24px !important; font-weight: 700; color: #1E293B; margin-top: 45px; margin-bottom: 20px; padding-bottom: 12px; border-bottom: 2px solid #F1F5F9; }
    .sub-section-title { font-size: 18px !important; font-weight: 600; color: #334155; margin-bottom: 15px; }
    div[data-testid="stMetricValue"] { font-size: 42px !important; font-weight: 700 !important; color: #0F172A !important; }
    div[data-testid="stMetricLabel"] { font-size: 16px !important; font-weight: 600 !important; color: #64748B !important; text-transform: uppercase; letter-spacing: 0.5px; }
    div[data-testid="metric-container"] { background-color: #F8FAFC; padding: 25px; border-radius: 8px; border: 1px solid #E2E8F0; }
    .stSlider label, .stSelectbox label, .stTextInput label { font-size: 16px !important; font-weight: 600 !important; color: #334155 !important; }
    .cluster-box { padding: 20px; border-radius: 6px; margin-bottom: 25px; border-left: 5px solid #CBD5E1; }
    .cluster-a { background-color: #FAF5FF; border-left-color: #5B21B6; } 
    .cluster-b { background-color: #FEFCBF; border-left-color: #EAB308; } 
    .cluster-c { background-color: #F0FDF4; border-left-color: #16A34A; } 
    .cluster-box-title { font-size: 18px !important; font-weight: 700; color: #0F172A; margin-bottom: 8px; }
    .cluster-box-desc { font-size: 15px !important; color: #334155; line-height: 1.6; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATA INTEGRATION & PRE-PROCESSED GEOJSON
# ==========================================
@st.cache_resource
def load_ml_pipeline():
    try:
        with open("D:/GOVREADY\govready_pipeline.pkl", "rb") as f:
            return pickle.load(f)
    except:
        return None

# Fungsi pembersihan super agresif (Hapus spasi, tanda baca, kata Kab/Kota)
def super_clean_text(text):
    if pd.isna(text):
        return ""
    t = str(text).upper().strip()
    t = t.replace("KOTA", "").replace("KABUPATEN", "").replace("KAB.", "").replace("ADMINISTRASI", "")
    t = re.sub(r'[^A-Z0-9]', '', t)
    return t

@st.cache_data
def load_fast_geojson(geojson_path):
    try:
        with open(geojson_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Terapkan pembersihan seragam ke properti pencocokan GeoJSON
            for feature in data.get('features', []):
                original_name = feature.get('properties', {}).get('WADMKK', '')
                feature['properties']['WADMKK_CLEAN'] = super_clean_text(original_name)
            return data
    except Exception as e:
        st.error(f"Gagal memuat berkas GeoJSON: {e}")
        return None

GEOJSON_MATANG_PATH = "D:/GOVREADY/indonesia_kabupaten.geojson"

def clean_region_name(name):
    cleaned = super_clean_text(name)
    
    # KAMUS OVERRIDE MUTAKHIR: Memetakan nama CSV ke ID Geometri GeoJSON secara presisi
    peta_pemekaran_induk = {
        # --- Wilayah Papua Utama & Pegunungan ---
        "PUNCAK": "PUNCAKJAYA",
        "INTANJAYA": "PANIAI",
        "DEIYAI": "PANIAI",
        "DOGIYAI": "PANIAI",
        "NDUGA": "JAYAWIJAYA",
        "YALIMO": "JAYAWIJAYA",
        "MAMBERAMOTENGAH": "JAYAWIJAYA",
        "LANNYJAYA": "JAYAWIJAYA",
        "MAMBERAMORAYA": "SARMI",
        
        # --- Wilayah Papua Selatan & Merauke Lama ---
        "ASMAT": "MERAUKE",
        "MAPPI": "MERAUKE",
        "BOVENDIGOEL": "MERAUKE",
        "PEGUNUNGANBINTANG": "YAHUKIMO",
        
        # --- Wilayah Maluku, Maluku Utara & Sulawesi ---
        "PULAUMOROTAI": "HALMAHERAUTARA",
        "PULAUYTALIABU": "KEPULAUANSULA",
        "TALIABU": "KEPULAUANSULA",
        "MALUKUTENGGARABARAT": "KEPULAUANTANIMBAR",
        "MALUKUTEGGRABARAT": "KEPULAUANTANIMBAR",
        "MALUKUTEGARABARAT": "KEPULAUANTANIMBAR",
        "MAMUJUUTARA": "PASANGKAYU",
        "SIAUTAGULANDANGBIARO": "KEPULAUANSIAUTAGULANDANGBIARO",
        "PANGKAJENEDANKEPULAUAN": "PANGKAJENEKEPULAUAN",
        "KEPULAUANSANGIHE": "SANGIHE",
        "KEPULAUANTALAUD": "TALAUD",
        "BOLAANGMONGONDOWUTARA": "BOLAANGMONGONDOW",
        "BOLAANGMONGONDOWSELATAN": "BOLAANGMONGONDOW",
        "BOLAANGMONGONDOWTIMUR": "BOLAANGMONGONDOW",
        
        # --- Sumatera & Kepulauan Luar ---
        "KEPULAUANMENTAWAI": "MENTAWAI",
        "NIASUTARA": "NIAS",
        "NIASBARAT": "NIAS",
        "NIASSELATAN": "NIAS",
        "TOBASAMOSIR": "TOBA",
        "BATANGHARI": "BATANGHARI",
        "BANYUASIN": "BANYUASIN",
        "GUNUNGKIDUL": "GUNUNGKIDUL"
    }
    
    if cleaned in peta_pemekaran_induk:
        return peta_pemekaran_induk[cleaned]
    return cleaned

model_pipeline = load_ml_pipeline()
geojson_data = load_fast_geojson(GEOJSON_MATANG_PATH)
fitur_numerik = ['IPM_2024', 'RLS_2024', 'P0_2024', 'D1_SPBE', 'D2_SPBE', 'D3_SPBE', 'D4_SPBE']

CLUSTER_INFO = {
    "Cluster A": {
        "title": "Cluster A – Daerah Berkembang Digital (Ungu)",
        "class": "cluster-a",
        "desc": "Daerah pada cluster ini telah memiliki fondasi transformasi digital yang cukup baik, namun masih memerlukan penguatan pada aspek tata kelola dan integrasi layanan..."
    },
    "Cluster B": {
        "title": "Cluster B – Daerah Siap Digital (Kuning)",
        "class": "cluster-b",
        "desc": "Daerah pada cluster ini memiliki capaian SPBE yang tinggi, didukung kualitas sumber daya manusia yang baik serta tingkat kemiskinan yang relatif rendah..."
    },
    "Cluster C": {
        "title": "Cluster C – Daerah Prioritas Transformasi Digital (Hijau)",
        "class": "cluster-c",
        "desc": "Daerah pada cluster ini memiliki tingkat kesiapan transformasi digital yang relatif lebih rendah..."
    }
}

def map_numeric_to_cluster_label(cluster_val):
    val_str = str(cluster_val).strip()
    if val_str in ['2', '2.0']:
        return "Cluster A"
    elif val_str in ['0', '0.0']:
        return "Cluster B"
    elif val_str in ['1', '1.0']:
        return "Cluster C"
    return "Cluster B"

def process_and_cluster_data(source_input):
    df_raw = pd.read_csv(source_input)
    
    if 'Kab/Kota' in df_raw.columns:
        df_raw['Geo_Key'] = df_raw['Kab/Kota'].apply(clean_region_name)
        
    if 'Cluster' not in df_raw.columns or df_raw['Cluster'].isnull().any():
        if model_pipeline is not None:
            try:
                preds = model_pipeline.predict(df_raw[fitur_numerik])
                df_raw['Cluster'] = [map_numeric_to_cluster_label(p) for p in preds]
            except:
                raw_preds = np.random.choice([0, 1, 2], size=len(df_raw))
                df_raw['Cluster'] = [map_numeric_to_cluster_label(p) for p in raw_preds]
        else:
            np.random.seed(42)
            raw_preds = np.random.choice([0, 1, 2], size=len(df_raw))
            df_raw['Cluster'] = [map_numeric_to_cluster_label(p) for p in raw_preds]
    else:
        df_raw['Cluster'] = df_raw['Cluster'].apply(map_numeric_to_cluster_label)
            
    return df_raw

# ==========================================
# 3. INTERFACE WORKFLOW & LAYOUT
# ==========================================
st.markdown('<div class="govready-title">Sistem Pendukung Keputusan Prioritas Transformasi Digital Daerah</div>', unsafe_allow_html=True)

uploaded_dataset = st.file_uploader("Pembaruan Basis Data Utama (Berkas CSV)", type=["csv"])

if 'active_df' not in st.session_state or uploaded_dataset is not None:
    if uploaded_dataset is not None:
        st.session_state.active_df = process_and_cluster_data(uploaded_dataset)
        st.toast("Dataset Berhasil Diperbarui")
    else:
        try:
            st.session_state.active_df = process_and_cluster_data("D:/GOVREADY/Dataset_Hasil_Imputasi  - Dataset_Hasil_Imputasi (1).csv")
        except:
            st.session_state.active_df = pd.DataFrame(columns=['Kab/Kota'] + fitur_numerik + ['Cluster'])

df_master = st.session_state.active_df

if not df_master.empty:
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Cakupan Wilayah", f"{len(df_master)} Kab/Kota")
    kpi2.metric("Rata-rata IPM", f"{df_master['IPM_2024'].mean():.2f}")
    kpi3.metric("Rata-rata Kebijakan SPBE (D1)", f"{df_master['D1_SPBE'].mean():.2f}")
    kpi4.metric("Rata-rata Layanan SPBE (D4)", f"{df_master['D4_SPBE'].mean():.2f}")

    st.markdown('<div class="section-title">Peta Batas Wilayah Administrasi Berdasarkan Kategori Klaster</div>', unsafe_allow_html=True)
    
    cluster_palette = {
        'Cluster A': '#5B21B6',  # Ungu Tua
        'Cluster B': '#EAB308',  # Kuning Gold
        'Cluster C': '#16A34A'   # Hijau Daun
    }
    
    if geojson_data is not None:
        fig_spatial = px.choropleth_mapbox(
            df_master,
            geojson=geojson_data,
            locations="Geo_Key",
            featureidkey="properties.WADMKK_CLEAN",  # Join menggunakan properti terstandardisasi agresif
            color="Cluster",
            color_discrete_map=cluster_palette,
            category_orders={"Cluster": ["Cluster A", "Cluster B", "Cluster C"]},
            mapbox_style="carto-positron",
            zoom=4.2, 
            center={"lat": -2.5, "lon": 118.0},
            opacity=0.8,
            labels={"Cluster": "Kategori Klaster"},
            hover_name="Kab/Kota",
            hover_data={'IPM_2024': ':.2f', 'P0_2024': ':.2f}%', 'D1_SPBE': ':.2f', 'D4_SPBE': ':.2f'}
        )
        
        fig_spatial.update_layout(
            margin={"r":0,"t":0,"l":0,"b":0},
            height=700,
            legend=dict(
                orientation="h", 
                yanchor="top", 
                y=0.98, 
                xanchor="left", 
                x=0.01,
                font=dict(size=14, color="#0F172A"),
                bgcolor="rgba(255, 255, 255, 0.90)"
            )
        )
        st.plotly_chart(fig_spatial, use_container_width=True)
    else:
        st.warning("Visualisasi peta tidak dapat ditampilkan karena berkas GeoJSON tidak tersedia.")

    st.markdown('<div class="section-title">Data Agregat Hasil Imputasi dan Maturitas Digital</div>', unsafe_allow_html=True)
    col_search, _ = st.columns([2, 2])
    with col_search:
        filter_query = st.text_input("Filter Wilayah Administrasi:", placeholder="Masukkan nama kabupaten atau kota...")

    display_col = 'Kab_Kota' if 'Kab_Kota' in df_master.columns else 'Kab/Kota'
    df_filtered = df_master[df_master[display_col].str.contains(filter_query, case=False)] if filter_query else df_master

    st.dataframe(df_filtered.drop(columns=['Geo_Key'], errors='ignore'), use_container_width=True, height=350)

    st.markdown('<div class="section-title">Panel Simulasi Dampak Skenario Intervensi Kebijakan</div>', unsafe_allow_html=True)
    target_kabkota = sorted(df_master[display_col].unique())
    selected_kab = st.selectbox("Pilih Wilayah Sasaran Intervensi:", target_kabkota)

    current_record = df_master[df_master[display_col] == selected_kab].iloc[0]
    initial_cluster = str(current_record['Cluster'])

    if initial_cluster in CLUSTER_INFO:
        info = CLUSTER_INFO[initial_cluster]
        st.markdown(f'<div class="cluster-box {info["class"]}"><div class="cluster-box-title">{info["title"]}</div><div class="cluster-box-desc">{info["desc"]}</div></div>', unsafe_allow_html=True)

    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.markdown('<div class="sub-section-title">Indikator Makro Sosio-Ekonomi</div>', unsafe_allow_html=True)
        input_ipm = st.slider("Indeks Pembangunan Manusia (IPM)", float(df_master['IPM_2024'].min()), float(df_master['IPM_2024'].max()), float(current_record['IPM_2024']), step=0.01)
        input_rls = st.slider("Rata-rata Lama Sekolah (RLS)", float(df_master['RLS_2024'].min()), float(df_master['RLS_2024'].max()), float(current_record['RLS_2024']), step=0.01)
        input_p0 = st.slider("Tingkat Kemiskinan (P0 %)", float(df_master['P0_2024'].min()), float(df_master['P0_2024'].max()), float(current_record['P0_2024']), step=0.01)
    with col_p2:
        st.markdown('<div class="sub-section-title">Indeks Maturitas SPBE</div>', unsafe_allow_html=True)
        input_d1 = st.slider("Dimensi 1: Kebijakan Tata Kelola", float(df_master['D1_SPBE'].min()), float(df_master['D1_SPBE'].max()), float(current_record['D1_SPBE']), step=0.01)
        input_d2 = st.slider("Dimensi 2: Tata Kelola Instansional", float(df_master['D2_SPBE'].min()), float(df_master['D2_SPBE'].max()), float(current_record['D2_SPBE']), step=0.01)
        input_d3 = st.slider("Dimensi 3: Manajemen Infrastruktur", float(df_master['D3_SPBE'].min()), float(df_master['D3_SPBE'].max()), float(current_record['D3_SPBE']), step=0.01)
        input_d4 = st.slider("Dimensi 4: Layanan Berbasis Elektronik", float(df_master['D4_SPBE'].min()), float(df_master['D4_SPBE'].max()), float(current_record['D4_SPBE']), step=0.01)

    if st.button("Eksekusi Skenario Perubahan", type="primary", use_container_width=True):
        inference_df = pd.DataFrame([{'IPM_2024': input_ipm, 'RLS_2024': input_rls, 'P0_2024': input_p0, 'D1_SPBE': input_d1, 'D2_SPBE': input_d2, 'D3_SPBE': input_d3, 'D4_SPBE': input_d4}])
        if model_pipeline is not None:
            try: raw_pred = model_pipeline.predict(inference_df)[0]
            except: raw_pred = model_pipeline.predict(inference_df.values)[0]
            predicted_cluster = map_numeric_to_cluster_label(raw_pred)
        else:
            if input_p0 > 15 or input_d1 < 2.2: predicted_cluster = "Cluster C"
            elif input_d1 > 3.0 and input_ipm > 73: predicted_cluster = "Cluster B"
            else: predicted_cluster = "Cluster A"
        idx_match = df_master[df_master[display_col] == selected_kab].index[0]
        st.session_state.active_df.loc[idx_match, ['IPM_2024', 'RLS_2024', 'P0_2024', 'D1_SPBE', 'D2_SPBE', 'D3_SPBE', 'D4_SPBE', 'Cluster']] = [input_ipm, input_rls, input_p0, input_d1, input_d2, input_d3, input_d4, predicted_cluster]
        st.rerun()
else:
    st.error("Gagal mendeteksi basis data utama.")