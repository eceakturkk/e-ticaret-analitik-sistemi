
-- SEPET ANALİZİ SORGULARI
-- Analiz scriptinin (scripts/sepet_analizi.py) ürettiği

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
