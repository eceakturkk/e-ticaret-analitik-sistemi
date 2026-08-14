
-- SEPET ANALİZİ (MARKET BASKET ANALYSIS) TABLOSU

CREATE TABLE sepet_analiz_kurallari (
    kural_id        SERIAL PRIMARY KEY,
    urun_a          VARCHAR(200) NOT NULL,
    urun_b          VARCHAR(200) NOT NULL,
    support         NUMERIC(6,4) NOT NULL,
    confidence      NUMERIC(6,4) NOT NULL,
    lift            NUMERIC(6,2) NOT NULL,
    analiz_tarihi   TIMESTAMP DEFAULT NOW()
);
