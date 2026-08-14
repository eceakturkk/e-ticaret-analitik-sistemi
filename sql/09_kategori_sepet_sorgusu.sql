
-- KATEGORİ BAZLI SEPET ANALİZİ SORGUSU 
-- Analiz scriptinin (scripts/kategori_sepet_analizi.py) ürettiği
-- kategori_sepet_kurallari tablosu üzerinden çalışır

SELECT 
    kategori_a,
    kategori_b,
    support,
    confidence,
    lift
FROM kategori_sepet_kurallari
ORDER BY lift DESC;
