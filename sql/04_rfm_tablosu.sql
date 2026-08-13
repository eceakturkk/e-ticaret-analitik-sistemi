-- ============================================
-- RFM ANALİZ TABLOSU (eticaret_dw veritabanında çalıştırılmalı)
-- ============================================

CREATE TABLE rfm_analiz (
    rfm_id          SERIAL PRIMARY KEY,
    musteri_id      INTEGER NOT NULL REFERENCES dim_musteri(musteri_id),
    son_siparis_tarihi   DATE NOT NULL,
    recency_gun     INTEGER NOT NULL,
    frequency       INTEGER NOT NULL,
    monetary        NUMERIC(10,2) NOT NULL,
    r_skor          INTEGER NOT NULL,
    f_skor          INTEGER NOT NULL,
    m_skor          INTEGER NOT NULL,
    rfm_skor        VARCHAR(3) NOT NULL,
    segment         VARCHAR(50) NOT NULL,
    analiz_tarihi   TIMESTAMP DEFAULT NOW()
);
