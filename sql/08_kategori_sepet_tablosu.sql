
-- KATEGORİ BAZLI SEPET ANALİZİ TABLOSU

CREATE TABLE kategori_sepet_kurallari (
    kural_id        SERIAL PRIMARY KEY,
    kategori_a      VARCHAR(100) NOT NULL,
    kategori_b      VARCHAR(100) NOT NULL,
    support         NUMERIC(6,4) NOT NULL,
    confidence      NUMERIC(6,4) NOT NULL,
    lift            NUMERIC(6,2) NOT NULL,
    analiz_tarihi   TIMESTAMP DEFAULT NOW()
);
