-- ============================================
-- KATEGORİ BAZLI SEPET ANALİZİ TABLOSU
-- (eticaret_dw veritabanında çalıştırılmalı)
-- Ürün bazlı sepet analizinin daha güvenilir/istatistiksel olarak
-- anlamlı hali - az kategori sayısı sayesinde daha yoğun veri
-- ============================================

CREATE TABLE kategori_sepet_kurallari (
    kural_id        SERIAL PRIMARY KEY,
    kategori_a      VARCHAR(100) NOT NULL,
    kategori_b      VARCHAR(100) NOT NULL,
    support         NUMERIC(6,4) NOT NULL,
    confidence      NUMERIC(6,4) NOT NULL,
    lift            NUMERIC(6,2) NOT NULL,
    analiz_tarihi   TIMESTAMP DEFAULT NOW()
);
