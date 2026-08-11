
-- VERİ AMBARI ŞEMASI - STAR SCHEMA 

-- DIMENSION TABLOLARI

-- 1. dim_zaman
CREATE TABLE dim_zaman (
    tarih_id        SERIAL PRIMARY KEY,
    tarih           DATE NOT NULL UNIQUE,
    yil             INTEGER NOT NULL,
    ay              INTEGER NOT NULL,
    ay_adi          VARCHAR(20) NOT NULL,
    ceyrek          INTEGER NOT NULL,
    hafta_gunu      VARCHAR(20) NOT NULL
);

-- 2. dim_musteri
CREATE TABLE dim_musteri (
    musteri_id      INTEGER PRIMARY KEY,
    ad_soyad        VARCHAR(150),
    sehir           VARCHAR(100),
    yas_grubu       VARCHAR(10),
    kayit_yili      INTEGER
);

-- 3. dim_urun
CREATE TABLE dim_urun (
    urun_id         INTEGER PRIMARY KEY,
    urun_adi        VARCHAR(200),
    kategori_adi    VARCHAR(100)
);

-- ============================================
-- FACT TABLOSU
-- ============================================

-- 4. fact_siparis (her satır = bir sipariş kalemi)
CREATE TABLE fact_siparis (
    fact_id           SERIAL PRIMARY KEY,
    siparis_detay_id  INTEGER NOT NULL,
    siparis_id        INTEGER NOT NULL,
    tarih_id          INTEGER NOT NULL REFERENCES dim_zaman(tarih_id),
    musteri_id        INTEGER NOT NULL REFERENCES dim_musteri(musteri_id),
    urun_id           INTEGER NOT NULL REFERENCES dim_urun(urun_id),
    adet              INTEGER NOT NULL,
    birim_fiyat       NUMERIC(10,2) NOT NULL,
    toplam_tutar      NUMERIC(10,2) NOT NULL,
    durum             VARCHAR(30) NOT NULL
);
