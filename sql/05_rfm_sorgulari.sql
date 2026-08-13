-- ============================================
-- RFM ANALİZ SORGULARI (eticaret_dw veritabanında çalıştırılır)
-- Analiz scriptinin (scripts/rfm_analiz.py) ürettiği rfm_analiz tablosu üzerinden çalışır
-- ============================================

-- 1. Müşteri Segment Dağılımı
SELECT 
    segment,
    COUNT(*) AS musteri_sayisi
FROM rfm_analiz
GROUP BY segment
ORDER BY musteri_sayisi DESC;

-- 2. Segment Bazlı Ortalama Harcama
SELECT 
    segment,
    ROUND(AVG(monetary), 2) AS ortalama_harcama,
    COUNT(*) AS musteri_sayisi
FROM rfm_analiz
GROUP BY segment
ORDER BY ortalama_harcama DESC;

-- 3. RFM Detay Raporu
SELECT 
    m.ad_soyad,
    m.sehir,
    r.recency_gun,
    r.frequency,
    r.monetary,
    r.rfm_skor,
    r.segment
FROM rfm_analiz r
JOIN dim_musteri m ON r.musteri_id = m.musteri_id
ORDER BY r.monetary DESC;
