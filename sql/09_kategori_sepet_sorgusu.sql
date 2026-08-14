-- ============================================
-- KATEGORİ BAZLI SEPET ANALİZİ SORGUSU (eticaret_dw veritabanında çalıştırılır)
-- Analiz scriptinin (scripts/kategori_sepet_analizi.py) ürettiği
-- kategori_sepet_kurallari tablosu üzerinden çalışır
--
-- NOT: Bu analiz, ürün bazlı sepet analizinin (sepet_analizi.py) yaşadığı
-- düşük-support/güvenilmezlik problemini çözmek için kategori seviyesinde
-- yapılmıştır. Lift değerlerinin 1'e yakın çıkması (gerçek bir ilişki
-- olmadığını göstermesi) veri setinin sentetik/rastgele üretilmiş olmasından
-- kaynaklanan beklenen ve doğru bir sonuçtur.
-- ============================================

SELECT 
    kategori_a,
    kategori_b,
    support,
    confidence,
    lift
FROM kategori_sepet_kurallari
ORDER BY lift DESC;
