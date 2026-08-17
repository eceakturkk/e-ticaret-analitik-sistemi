
-- Metabase dashboard'undaki 6 grafiğin kaynağı

-- 1. En çok satan ürünler (adet bazında)
SELECT 
    u.urun_adi,
    u.kategori_adi,
    SUM(f.adet) AS toplam_satis_adet,
    ROUND(SUM(f.toplam_tutar), 2) AS toplam_gelir
FROM fact_siparis f
JOIN dim_urun u ON f.urun_id = u.urun_id
WHERE f.durum = 'Tamamlandı'
GROUP BY u.urun_adi, u.kategori_adi
ORDER BY toplam_satis_adet DESC
LIMIT 10;

-- 2. Kategori bazlı toplam gelir
SELECT 
    u.kategori_adi,
    ROUND(SUM(f.toplam_tutar), 2) AS toplam_gelir
FROM fact_siparis f
JOIN dim_urun u ON f.urun_id = u.urun_id
WHERE f.durum = 'Tamamlandı'
GROUP BY u.kategori_adi
ORDER BY toplam_gelir DESC;

-- 3. Aylık gelir trendi
SELECT 
    z.yil || '-' || LPAD(z.ay::text, 2, '0') AS yil_ay,
    ROUND(SUM(f.toplam_tutar), 2) AS aylik_gelir
FROM fact_siparis f
JOIN dim_zaman z ON f.tarih_id = z.tarih_id
WHERE f.durum = 'Tamamlandı'
GROUP BY z.yil, z.ay
ORDER BY z.yil, z.ay;

-- 4. Yaş grubuna göre ortalama sipariş tutarı (doğal yaş sırasıyla)
SELECT 
    m.yas_grubu,
    ROUND(AVG(f.toplam_tutar), 2) AS ortalama_tutar,
    COUNT(*) AS siparis_kalem_sayisi
FROM fact_siparis f
JOIN dim_musteri m ON f.musteri_id = m.musteri_id
WHERE f.durum = 'Tamamlandı'
GROUP BY m.yas_grubu
ORDER BY 
    CASE m.yas_grubu
        WHEN '18-24' THEN 1
        WHEN '25-34' THEN 2
        WHEN '35-44' THEN 3
        WHEN '45-54' THEN 4
        WHEN '55+' THEN 5
    END;

-- 5. Şehir bazlı toplam gelir
SELECT 
    m.sehir,
    ROUND(SUM(f.toplam_tutar), 2) AS toplam_gelir,
    COUNT(DISTINCT f.siparis_id) AS siparis_sayisi
FROM fact_siparis f
JOIN dim_musteri m ON f.musteri_id = m.musteri_id
WHERE f.durum = 'Tamamlandı'
GROUP BY m.sehir
ORDER BY toplam_gelir DESC;

-- 6. Sipariş durum dağılımı (iptal/iade oranı)
SELECT 
    durum,
    COUNT(*) AS kayit_sayisi,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS yuzde
FROM fact_siparis
GROUP BY durum;
