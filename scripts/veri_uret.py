"""
E-Ticaret Analitik Sistemi
Örnek Veri Üretme Scripti

Bu script:
- Kategori, ürün, müşteri, sipariş ve sipariş detay verilerini sahte ama gerçekçi şekilde üretir
- Doğrudan PostgreSQL (eticaret_oltp) veritabanına yükler
"""

import random
from datetime import date, datetime, timedelta

import pandas as pd
from faker import Faker
from sqlalchemy import create_engine

# ---------------------------------------------------------
# 1. VERİTABANI BAĞLANTISI
# ---------------------------------------------------------
DB_USER = "eticaret"
DB_PASS = "eticaret123"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "eticaret_oltp"

engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

fake = Faker("tr_TR")
random.seed(42)

# ---------------------------------------------------------
# 2. KATEGORİ VERİSİ
# ---------------------------------------------------------
kategoriler = [
    "Elektronik", "Giyim", "Ev & Yaşam", "Kozmetik",
    "Spor & Outdoor", "Kitap & Hobi", "Anne & Bebek", "Süpermarket"
]

df_kategori = pd.DataFrame({"kategori_adi": kategoriler})
df_kategori.to_sql("kategori", engine, if_exists="append", index=False)
print(f"{len(df_kategori)} kategori eklendi.")

kategori_ids = pd.read_sql("SELECT kategori_id, kategori_adi FROM kategori", engine)

# ---------------------------------------------------------
# 3. ÜRÜN VERİSİ
# ---------------------------------------------------------
# Kategoriye göre gerçekçi fiyat aralıkları
fiyat_araliklari = {
    "Elektronik": (500, 25000),
    "Giyim": (100, 2000),
    "Ev & Yaşam": (50, 5000),
    "Kozmetik": (50, 1500),
    "Spor & Outdoor": (100, 4000),
    "Kitap & Hobi": (30, 500),
    "Anne & Bebek": (50, 2000),
    "Süpermarket": (10, 300),
}

n_urun_per_kategori = 15
urun_kayitlari = []

for _, kat_row in kategori_ids.iterrows():
    kat_id = kat_row["kategori_id"]
    kat_adi = kat_row["kategori_adi"]
    min_fiyat, max_fiyat = fiyat_araliklari[kat_adi]

    for _ in range(n_urun_per_kategori):
        urun_kayitlari.append({
            "urun_adi": fake.catch_phrase(),
            "kategori_id": kat_id,
            "fiyat": round(random.uniform(min_fiyat, max_fiyat), 2),
            "stok_miktari": random.randint(0, 500),
        })

df_urun = pd.DataFrame(urun_kayitlari)
df_urun.to_sql("urun", engine, if_exists="append", index=False)
print(f"{len(df_urun)} ürün eklendi.")

urun_df = pd.read_sql("SELECT urun_id, fiyat FROM urun", engine)

# ---------------------------------------------------------
# 4. MÜŞTERİ VERİSİ
# ---------------------------------------------------------
yas_gruplari = ["18-24", "25-34", "35-44", "45-54", "55+"]
sehirler = ["İstanbul", "Ankara", "İzmir", "Bursa", "Antalya", "Adana", "Konya", "Gaziantep"]

n_musteri = 300
musteri_kayitlari = []

for _ in range(n_musteri):
    musteri_kayitlari.append({
        "ad_soyad": fake.name(),
        "email": fake.unique.email(),
        "sehir": random.choice(sehirler),
        "yas_grubu": random.choices(
            yas_gruplari, weights=[0.15, 0.30, 0.25, 0.18, 0.12]
        )[0],
        "kayit_tarihi": fake.date_between(start_date="-3y", end_date="-1M"),
    })

df_musteri = pd.DataFrame(musteri_kayitlari)
df_musteri.to_sql("musteri", engine, if_exists="append", index=False)
print(f"{len(df_musteri)} müşteri eklendi.")

musteri_ids = pd.read_sql("SELECT musteri_id FROM musteri", engine)["musteri_id"].tolist()
urun_ids = urun_df["urun_id"].tolist()

# ---------------------------------------------------------
# 5. SİPARİŞ VE SİPARİŞ DETAY VERİSİ
# ---------------------------------------------------------
durumlar = ["Tamamlandı", "Tamamlandı", "Tamamlandı", "Tamamlandı", "İptal", "İade"]

n_siparis = 800
siparis_kayitlari = []

for _ in range(n_siparis):
    siparis_kayitlari.append({
        "musteri_id": random.choice(musteri_ids),
        "siparis_tarihi": fake.date_time_between(start_date="-1y", end_date="now"),
        "durum": random.choice(durumlar),
    })

df_siparis = pd.DataFrame(siparis_kayitlari)
df_siparis.to_sql("siparis", engine, if_exists="append", index=False)
print(f"{len(df_siparis)} sipariş eklendi.")

siparis_ids = pd.read_sql("SELECT siparis_id FROM siparis", engine)["siparis_id"].tolist()

# Her sipariş için 1-4 arası ürün kalemi oluştur
urun_fiyat_map = dict(zip(urun_df["urun_id"], urun_df["fiyat"]))

siparis_detay_kayitlari = []
for siparis_id in siparis_ids:
    n_kalem = random.randint(1, 4)
    secilen_urunler = random.sample(urun_ids, min(n_kalem, len(urun_ids)))

    for urun_id in secilen_urunler:
        siparis_detay_kayitlari.append({
            "siparis_id": siparis_id,
            "urun_id": urun_id,
            "adet": random.randint(1, 3),
            "birim_fiyat": urun_fiyat_map[urun_id],
        })

df_siparis_detay = pd.DataFrame(siparis_detay_kayitlari)
df_siparis_detay.to_sql("siparis_detay", engine, if_exists="append", index=False)
print(f"{len(df_siparis_detay)} sipariş detay kaydı eklendi.")

print("\n✅ Tüm örnek veriler başarıyla yüklendi!")
