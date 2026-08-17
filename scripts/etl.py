"""
ETL
Bu script:
- eticaret_oltp veritabanından ham veriyi çeker (Extract)
- Star schema formatına dönüştürür (Transform)
- eticaret_dw veritabanına yükler (Load)
"""

import pandas as pd
from sqlalchemy import create_engine

# ---------------------------------------------------------
# 1. VERİTABANI BAĞLANTILARI

DB_USER = "eticaret"
DB_PASS = "eticaret123"
DB_HOST = "localhost"
DB_PORT = "5432"

engine_oltp = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/eticaret_oltp")
engine_dw = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/eticaret_dw")

HAFTA_GUNLERI = {
    0: "Pazartesi", 1: "Salı", 2: "Çarşamba", 3: "Perşembe",
    4: "Cuma", 5: "Cumartesi", 6: "Pazar",
}

AY_ADLARI = {
    1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan", 5: "Mayıs", 6: "Haziran",
    7: "Temmuz", 8: "Ağustos", 9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık",
}

print("ETL süreci başlıyor...\n")

# ---------------------------------------------------------
# 2. EXTRACT — OLTP'den ham veriyi çek

df_kategori_src = pd.read_sql("SELECT * FROM kategori", engine_oltp)
df_urun_src = pd.read_sql("SELECT * FROM urun", engine_oltp)
df_musteri_src = pd.read_sql("SELECT * FROM musteri", engine_oltp)
df_siparis_src = pd.read_sql("SELECT * FROM siparis", engine_oltp)
df_siparis_detay_src = pd.read_sql("SELECT * FROM siparis_detay", engine_oltp)

print("Extract tamamlandı: OLTP'den veriler çekildi.")

# ---------------------------------------------------------
# 3. TRANSFORM + LOAD — dim_musteri

df_dim_musteri = df_musteri_src[["musteri_id", "ad_soyad", "sehir", "yas_grubu"]].copy()
df_dim_musteri["kayit_yili"] = pd.to_datetime(df_musteri_src["kayit_tarihi"]).dt.year
df_dim_musteri.to_sql("dim_musteri", engine_dw, if_exists="append", index=False)
print(f"dim_musteri yüklendi: {len(df_dim_musteri)} kayıt.")

# ---------------------------------------------------------
# 4. TRANSFORM + LOAD — dim_urun

df_urun_merged = df_urun_src.merge(df_kategori_src, on="kategori_id", how="left")
df_dim_urun = df_urun_merged[["urun_id", "urun_adi", "kategori_adi"]].copy()
df_dim_urun.to_sql("dim_urun", engine_dw, if_exists="append", index=False)
print(f"dim_urun yüklendi: {len(df_dim_urun)} kayıt.")

# ---------------------------------------------------------
# 5. TRANSFORM + LOAD — dim_zaman

tarihler = pd.to_datetime(df_siparis_src["siparis_tarihi"]).dt.date
tekil_tarihler = pd.Series(tarihler.unique())
tekil_tarihler = pd.to_datetime(tekil_tarihler).sort_values().reset_index(drop=True)

df_dim_zaman = pd.DataFrame({"tarih": tekil_tarihler})
df_dim_zaman["yil"] = df_dim_zaman["tarih"].dt.year
df_dim_zaman["ay"] = df_dim_zaman["tarih"].dt.month
df_dim_zaman["ay_adi"] = df_dim_zaman["ay"].map(AY_ADLARI)
df_dim_zaman["ceyrek"] = df_dim_zaman["tarih"].dt.quarter
df_dim_zaman["hafta_gunu"] = df_dim_zaman["tarih"].dt.weekday.map(HAFTA_GUNLERI)

df_dim_zaman.to_sql("dim_zaman", engine_dw, if_exists="append", index=False)
print(f"dim_zaman yüklendi: {len(df_dim_zaman)} kayıt.")

# tarih -> tarih_id eşlemesi için geri oku
df_dim_zaman_db = pd.read_sql("SELECT tarih_id, tarih FROM dim_zaman", engine_dw)
df_dim_zaman_db["tarih"] = pd.to_datetime(df_dim_zaman_db["tarih"])
tarih_to_id = dict(zip(df_dim_zaman_db["tarih"], df_dim_zaman_db["tarih_id"]))

# ---------------------------------------------------------
# 6. TRANSFORM + LOAD — fact_siparis

# siparis_detay -> siparis (tarih, musteri, durum bilgisi için) birleştiriliyor
df_fact = df_siparis_detay_src.merge(
    df_siparis_src[["siparis_id", "musteri_id", "siparis_tarihi", "durum"]],
    on="siparis_id", how="left"
)

df_fact["siparis_tarihi"] = pd.to_datetime(df_fact["siparis_tarihi"])
df_fact["tarih_only"] = df_fact["siparis_tarihi"].dt.normalize()
df_fact["tarih_id"] = df_fact["tarih_only"].map(tarih_to_id)

df_fact["toplam_tutar"] = df_fact["adet"] * df_fact["birim_fiyat"]

df_fact_final = df_fact[[
    "siparis_detay_id", "siparis_id", "tarih_id", "musteri_id",
    "urun_id", "adet", "birim_fiyat", "toplam_tutar", "durum"
]].rename(columns={"siparis_detay_id": "siparis_detay_id"})

df_fact_final.to_sql("fact_siparis", engine_dw, if_exists="append", index=False)
print(f"fact_siparis yüklendi: {len(df_fact_final)} kayıt.")

print("\n ETL süreci başarıyla tamamlandı! Veri ambarı dolduruldu.")
