-- ============================================
-- SEPET ANALİZİ SORGULARI (eticaret_dw veritabanında çalıştırılır)
-- Analiz scriptinin (scripts/sepet_analizi.py) ürettiği
-- sepet_analiz_kurallari tablosu üzerinden çalışır
-- ============================================

-- En güçlü birliktelik kuralları (lift'e göre)
SELECT 
    urun_a,
    urun_b,
    support,
    confidence,
    lift
FROM sepet_analiz_kurallari
ORDER BY lift DESC
LIMIT 20;
