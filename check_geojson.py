import pandas as pd
import json

def deteksi_inkonsistensi_wilayah(csv_path, geojson_path):
    print("="*60)
    print(" Memulai Deteksi Inkonsistensi Nama Wilayah ")
    print("="*60)
    
    # 1. Muat data dari CSV
    try:
        df = pd.read_csv(csv_path)
        # Menyesuaikan nama kolom jika ada variasi penulisan
        kolom_wilayah = 'Kab/Kota' if 'Kab/Kota' in df.columns else ('Kab_Kota' if 'Kab_Kota' in df.columns else None)
        
        if not kolom_wilayah:
            print("[ERROR] Kolom nama daerah tidak ditemukan di CSV. Pastikan ada kolom 'Kab/Kota'.")
            return
            
        # Ambil daftar unik nama daerah dari CSV
        csv_regions = set(df[kolom_wilayah].dropna().unique())
    except Exception as e:
        print(f"[ERROR] Gagal membaca file CSV: {e}")
        return

    # 2. Muat data dari GeoJSON
    try:
        with open(geojson_path, "r", encoding="utf-8") as f:
            geojson_data = json.load(f)
            
        # Ambil daftar nama daerah dari properti WADMKK di GeoJSON
        geojson_regions = set()
        for feature in geojson_data.get('features', []):
            nama_geojson = feature.get('properties', {}).get('WADMKK')
            if nama_geojson:
                geojson_regions.add(str(nama_geojson).strip())
    except Exception as e:
        print(f"[ERROR] Gagal membaca file GeoJSON: {e}")
        return

    # 3. Fungsi pembersihan dasar untuk simulasi pencocokan awal
    def clean_text(text):
        t = str(text).upper().strip()
        t = t.replace("KOTA ", "").replace("KABUPATEN ", "").replace("KAB. ", "")
        return t

    csv_clean = {clean_text(r): r for r in csv_regions}
    geojson_clean = {clean_text(r): r for r in geojson_regions}

    # 4. Deteksi daerah di CSV yang TIDAK ADA di GeoJSON (Penyebab daerah abu-abu)
    tidak_ada_di_geojson = []
    for clean_csv_name, original_csv_name in csv_clean.items():
        if clean_csv_name not in geojson_clean:
            tidak_ada_di_geojson.append(original_csv_name)

    # 5. Tampilkan Hasil Analisis
    print(f" Total wilayah unik di CSV     : {len(csv_regions)}")
    print(f" Total wilayah unik di GeoJSON : {len(geojson_regions)}")
    print("-" * 60)
    
    if tidak_ada_di_geojson:
        print(f"⚠️  Ditemukan {len(tidak_ada_di_geojson)} daerah di CSV yang GA MAU KEWARNAIN (Tidak cocok dengan GeoJSON):")
        print("-" * 60)
        for i, daerah in enumerate(sorted(tidak_ada_di_geojson), 1):
            # Cari rekomendasi nama yang mirip di GeoJSON (jika ada kemiripan kata)
            clean_daerah = clean_text(daerah)
            rekomendasi = [geojson_clean[g] for g in geojson_clean if clean_daerah in g or g in clean_daerah]
            
            info_rekomendasi = f" -> Rekomendasi di GeoJSON: {rekomendasi}" if rekomendasi else ""
            print(f"{i}. \"{daerah}\"{info_rekomendasi}")
            
        print("-" * 60)
        print("💡 TIPS PERBAIKAN:")
        print("Masukkan nama-nama di atas ke dalam kamus `corrections` pada file app.py kamu.")
        print("Contoh formatnya:")
        print("  \"NAMA_DI_LIST_ATAS\": \"NAMA_YANG_BENAR_DI_GEOJSON\"")
    else:
        print("✅ LUAR BIASA! Semua nama daerah di CSV sudah 100% cocok dengan GeoJSON.")
        print("Peta kamu seharusnya terwarnai semua tanpa ada yang abu-abu.")
        
    print("="*60)

# === KONFIGURASI PATH ===
# Silakan sesuaikan path file kamu di bawah ini sebelum menjalankan
PATH_CSV = "C:/Users/arielva/Downloads/GovReady-DSS/Dataset_Hasil_Imputasi  - Dataset_Hasil_Imputasi (1).csv"
PATH_GEOJSON = "C:/Users/arielva/Downloads/GovReady-DSS/indonesia_kabupaten.geojson"

if __name__ == "__main__":
    deteksi_inkonsistensi_wilayah(PATH_CSV, PATH_GEOJSON)