"""
E-Ticaret Analitik Sistemi
Kategori Bazlı Sepet Analizi

Bu script, ürün bazlı sepet analizinin (sepet_analizi.py) yaşadığı
"az veri, çok ürün -> güvenilmez sonuç" problemini çözmek için
aynı Apriori mantığını ÜRÜN yerine KATEGORİ seviyesinde uygular.

8 kategori olduğu için (120 ürüne kıyasla), her kombinasyon için
çok daha fazla veri birikir -> sonuçlar istatistiksel olarak daha güvenilir olur.
"""

import pandas as pd
from sqlalchemy import create_engine
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder

DB_USER = "eticaret"
DB_PASS = "eticaret123"
DB_HOST = "localhost"
DB_PORT = "5432"

engine_dw = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/eticaret_dw")

# Kategori seviyesinde olduğumuz için eşikleri makul seviyede tutabiliriz
MIN_SUPPORT = 0.05
MIN_CONFIDENCE = 0.3

print("Kategori bazlı sepet analizi başlıyor...\n")

# ---------------------------------------------------------
# 1. VERİYİ ÇEK — bu sefer urun_adi değil, kategori_adi
# ---------------------------------------------------------
df = pd.read_sql("""
    SELECT DISTINCT
        f.siparis_id,
        u.kategori_adi
    FROM fact_siparis f
    JOIN dim_urun u ON f.urun_id = u.urun_id
    WHERE f.durum = 'Tamamlandı'
""", engine_dw)

# DISTINCT kullandık çünkü bir siparişte aynı kategoriden 2 ürün olabilir,
# biz sadece "bu siparişte bu kategori var mı yok mu" bilgisini istiyoruz

print(f"{len(df)} sipariş-kategori satırı okundu.")
print(f"{df['siparis_id'].nunique()} tekil sipariş (sepet) bulundu.")
print(f"{df['kategori_adi'].nunique()} farklı kategori var.")

# ---------------------------------------------------------
# 2. SEPET FORMATINA DÖNÜŞTÜR
# ---------------------------------------------------------
sepetler = df.groupby("siparis_id")["kategori_adi"].apply(list).tolist()

te = TransactionEncoder()
te_array = te.fit(sepetler).transform(sepetler)
df_encoded = pd.DataFrame(te_array, columns=te.columns_)

print(f"Sepet matrisi oluşturuldu: {df_encoded.shape[0]} sepet x {df_encoded.shape[1]} kategori.")

# ---------------------------------------------------------
# 3. APRIORI + ASSOCIATION RULES
# ---------------------------------------------------------
frequent_itemsets = apriori(df_encoded, min_support=MIN_SUPPORT, use_colnames=True)
print(f"{len(frequent_itemsets)} sık görülen kategori kombinasyonu bulundu.")

rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=MIN_CONFIDENCE)

rules = rules[
    (rules["antecedents"].apply(len) == 1) &
    (rules["consequents"].apply(len) == 1)
].copy()

rules["kategori_a"] = rules["antecedents"].apply(lambda x: list(x)[0])
rules["kategori_b"] = rules["consequents"].apply(lambda x: list(x)[0])

rules_final = rules[["kategori_a", "kategori_b", "support", "confidence", "lift"]].copy()
rules_final = rules_final.sort_values("lift", ascending=False).round(4)

print(f"{len(rules_final)} kategori birlikteliği kuralı bulundu.\n")

if len(rules_final) > 0:
    rules_final.to_sql("kategori_sepet_kurallari", engine_dw, if_exists="append", index=False)
    print(f"✅ {len(rules_final)} kural 'kategori_sepet_kurallari' tablosuna yazıldı.\n")

    print("--- Tüm kategori birliktelik kuralları (lift'e göre) ---")
    print(rules_final.to_string(index=False))
else:
    print("⚠️  Eşikleri karşılayan kural bulunamadı, MIN_SUPPORT/MIN_CONFIDENCE düşürülebilir.")
