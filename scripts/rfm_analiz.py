"""
Bu script:
- Her müşteri için Recency (yakınlık), Frequency (sıklık), Monetary (parasal değer) hesaplar
- Her ölçütü 1-5 arası puanlar (NTILE mantığıyla, pandas qcut kullanarak)
- Puanlara göre müşteriyi bir segmente atar (Şampiyon, Sadık Müşteri, Risk Altında vb.)
- Sonuçları rfm_analiz tablosuna yazar
"""

import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine

# 1. VERİTABANI BAĞLANTISI
# ---------------------------------------------------------
DB_USER = "eticaret"
DB_PASS = "eticaret123"
DB_HOST = "localhost"
DB_PORT = "5432"

engine_dw = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/eticaret_dw")

print("RFM analizi başlıyor...\n")

# 2. VERİYİ ÇEK (sadece tamamlanan siparişler)
# ---------------------------------------------------------
df = pd.read_sql("""
    SELECT 
        f.musteri_id,
        f.siparis_id,
        z.tarih,
        f.toplam_tutar
    FROM fact_siparis f
    JOIN dim_zaman z ON f.tarih_id = z.tarih_id
    WHERE f.durum = 'Tamamlandı'
""", engine_dw)

print(f"{len(df)} sipariş kalemi okundu.")

df["tarih"] = pd.to_datetime(df["tarih"])
bugun = pd.Timestamp(datetime.now().date())


# 3. MÜŞTERİ BAZLI RFM DEĞERLERİNİ HESAPLA
# ---------------------------------------------------------
rfm = df.groupby("musteri_id").agg(
    son_siparis_tarihi=("tarih", "max"),
    frequency=("siparis_id", "nunique"),   # tekil sipariş sayısı
    monetary=("toplam_tutar", "sum"),
).reset_index()

rfm["recency_gun"] = (bugun - rfm["son_siparis_tarihi"]).dt.days

print(f"{len(rfm)} müşteri için RFM değerleri hesaplandı.")


# 4. 1-5 ARASI PUANLAMA (qcut ile 5 eşit dilime bölüyoruz)
# ---------------------------------------------------------
# Recency: DÜŞÜK gün sayısı = İYİ (yakın zamanda alışveriş yapmış) -> puanlama TERS çevriliyor
rfm["r_skor"] = pd.qcut(rfm["recency_gun"], 5, labels=[5, 4, 3, 2, 1]).astype(int)

# Frequency: YÜKSEK sipariş sayısı = İYİ -> normal sırayla puanlama
# Not: rank(method="first") kullanıyoruz çünkü frequency'de çok sayıda eşit değer (aynı sipariş sayısı)
# olabilir, qcut bu durumda hata verebilir
rfm["f_skor"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)

# Monetary: YÜKSEK harcama = İYİ -> normal sırayla puanlama
rfm["m_skor"] = pd.qcut(rfm["monetary"], 5, labels=[1, 2, 3, 4, 5]).astype(int)

rfm["rfm_skor"] = (
    rfm["r_skor"].astype(str) + rfm["f_skor"].astype(str) + rfm["m_skor"].astype(str)
)


# 5. SEGMENT ATAMA (basit kural tabanlı mantık)
# ---------------------------------------------------------
def segment_belirle(row):
    r, f, m = row["r_skor"], row["f_skor"], row["m_skor"]

    if r >= 4 and f >= 4 and m >= 4:
        return "Şampiyon"
    elif r >= 3 and f >= 3:
        return "Sadık Müşteri"
    elif r >= 4 and f <= 2:
        return "Yeni Müşteri"
    elif r <= 2 and f >= 4:
        return "Risk Altında"
    elif r <= 2 and f <= 2 and m <= 2:
        return "Kayıp Müşteri"
    else:
        return "Orta Segment"

rfm["segment"] = rfm.apply(segment_belirle, axis=1)


# 6. YÜKLE — rfm_analiz tablosuna yaz
# ---------------------------------------------------------
rfm_final = rfm[[
    "musteri_id", "son_siparis_tarihi", "recency_gun", "frequency", "monetary",
    "r_skor", "f_skor", "m_skor", "rfm_skor", "segment"
]].copy()

rfm_final["monetary"] = rfm_final["monetary"].round(2)

rfm_final.to_sql("rfm_analiz", engine_dw, if_exists="append", index=False)
print(f"\n {len(rfm_final)} müşteri için RFM analizi 'rfm_analiz' tablosuna yazıldı.")

# 7. ÖZET RAPOR
# ---------------------------------------------------------
print("\n--- Segment Dağılımı ---")
print(rfm_final["segment"].value_counts().to_string())
