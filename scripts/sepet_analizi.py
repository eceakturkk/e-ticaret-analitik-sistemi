"""
E-Ticaret Analitik Sistemi
Sepet Analizi (Market Basket Analysis) Scripti

Bu script:
- Her siparişi bir "sepet" olarak ele alır
- Apriori algoritmasıyla sık birlikte satılan ürün kombinasyonlarını bulur
- Association rules (birliktelik kuralları) çıkarır: support, confidence, lift
- Sonuçları sepet_analiz_kurallari tablosuna yazar
"""

import pandas as pd
from sqlalchemy import create_engine
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder

# 1. VERİTABANI BAĞLANTISI
# ---------------------------------------------------------
DB_USER = "eticaret"
DB_PASS = "eticaret123"
DB_HOST = "localhost"
DB_PORT = "5432"

engine_dw = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/eticaret_dw")

# Eşik değerler - bunları değiştirerek daha fazla/az kural bulabilirsin
MIN_SUPPORT = 0.004     # ürün kombinasyonu, siparişlerin en az %0.4'ünde görülmeli (yaklaşık 2 sepet)
MIN_CONFIDENCE = 0.02   # A alındığında B'nin alınma olasılığı en az %2 olmalı

print("Sepet analizi başlıyor...\n")

# 2. VERİYİ ÇEK (sadece tamamlanan siparişler)
# ---------------------------------------------------------
df = pd.read_sql("""
    SELECT 
        f.siparis_id,
        u.urun_adi
    FROM fact_siparis f
    JOIN dim_urun u ON f.urun_id = u.urun_id
    WHERE f.durum = 'Tamamlandı'
""", engine_dw)

print(f"{len(df)} sipariş kalemi okundu.")
print(f"{df['siparis_id'].nunique()} tekil sipariş (sepet) bulundu.")

# 3. SEPET FORMATINA DÖNÜŞTÜR
# ---------------------------------------------------------
# Her sipariş_id için, o siparişte geçen ürünlerin listesini oluşturuyoruz
sepetler = df.groupby("siparis_id")["urun_adi"].apply(list).tolist()

# TransactionEncoder: sepet listelerini True/False matrisine çevirir
# (her satır bir sipariş, her sütun bir ürün, True = o ürün o siparişte var)
te = TransactionEncoder()
te_array = te.fit(sepetler).transform(sepetler)
df_encoded = pd.DataFrame(te_array, columns=te.columns_)

print(f"Sepet matrisi oluşturuldu: {df_encoded.shape[0]} sepet x {df_encoded.shape[1]} ürün.")


# 4. APRIORI ALGORİTMASI - SIK GÖRÜLEN ÜRÜN KOMBİNASYONLARI
# ---------------------------------------------------------
frequent_itemsets = apriori(df_encoded, min_support=MIN_SUPPORT, use_colnames=True)

print(f"{len(frequent_itemsets)} sık görülen ürün kombinasyonu bulundu.")

# Tanı amaçlı: kombinasyon büyüklüklerinin dağılımı
frequent_itemsets["boyut"] = frequent_itemsets["itemsets"].apply(len)
print("Kombinasyon büyüklüğü dağılımı:")
print(frequent_itemsets["boyut"].value_counts().sort_index().to_string())

if len(frequent_itemsets) == 0:
    print("\n Hiç kombinasyon bulunamadı. MIN_SUPPORT değerini düşürüp tekrar dene.")
else:
    # ---------------------------------------------------------
    # 5. ASSOCIATION RULES (BİRLİKTELİK KURALLARI) ÇIKAR
    # ---------------------------------------------------------
    rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=MIN_CONFIDENCE)

    # Sadece 1 ürün -> 1 ürün ilişkilerini alıyoruz (basitlik için)
    rules = rules[
        (rules["antecedents"].apply(len) == 1) &
        (rules["consequents"].apply(len) == 1)
    ].copy()

    rules["urun_a"] = rules["antecedents"].apply(lambda x: list(x)[0])
    rules["urun_b"] = rules["consequents"].apply(lambda x: list(x)[0])

    rules_final = rules[["urun_a", "urun_b", "support", "confidence", "lift"]].copy()
    rules_final = rules_final.sort_values("lift", ascending=False).round(4)

    print(f"{len(rules_final)} birliktelik kuralı bulundu.")

    
    # 6. YÜKLE — sepet_analiz_kurallari tablosuna yaz
    # ---------------------------------------------------------
    if len(rules_final) > 0:
        rules_final.to_sql("sepet_analiz_kurallari", engine_dw, if_exists="append", index=False)
        print(f"\n {len(rules_final)} kural 'sepet_analiz_kurallari' tablosuna yazıldı.")

        print("\n--- En güçlü 5 ilişki (lift'e göre) ---")
        print(rules_final.head(5).to_string(index=False))
    else:
        print("\n Eşik değerlerini karşılayan kural bulunamadı. MIN_CONFIDENCE değerini düşürüp tekrar dene.")
