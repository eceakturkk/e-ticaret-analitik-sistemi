-- ============================================
-- OLTP ŞEMASI (eticaret_oltp veritabanında çalıştırılmalı)
-- ============================================

-- 1. KATEGORİ tablosu
CREATE TABLE kategori (
    kategori_id     SERIAL PRIMARY KEY,
    kategori_adi    VARCHAR(100) NOT NULL
);

-- 2. ÜRÜN tablosu
CREATE TABLE urun (
    urun_id         SERIAL PRIMARY KEY,
    urun_adi        VARCHAR(200) NOT NULL,
    kategori_id     INTEGER NOT NULL REFERENCES kategori(kategori_id),
    fiyat           NUMERIC(10,2) NOT NULL,
    stok_miktari    INTEGER NOT NULL DEFAULT 0
);

-- 3. MÜŞTERİ tablosu
CREATE TABLE musteri (
    musteri_id      SERIAL PRIMARY KEY,
    ad_soyad        VARCHAR(150) NOT NULL,
    email           VARCHAR(150) NOT NULL UNIQUE,
    sehir           VARCHAR(100),
    yas_grubu       VARCHAR(10) NOT NULL,   -- '18-24', '25-34', '35-44', '45-54', '55+'
    kayit_tarihi    DATE NOT NULL
);

-- 4. SİPARİŞ tablosu
CREATE TABLE siparis (
    siparis_id      SERIAL PRIMARY KEY,
    musteri_id      INTEGER NOT NULL REFERENCES musteri(musteri_id),
    siparis_tarihi  TIMESTAMP NOT NULL,
    durum           VARCHAR(30) NOT NULL DEFAULT 'Tamamlandı'  -- 'Tamamlandı', 'İptal', 'İade'
);

-- 5. SİPARİŞ DETAY tablosu
CREATE TABLE siparis_detay (
    siparis_detay_id  SERIAL PRIMARY KEY,
    siparis_id        INTEGER NOT NULL REFERENCES siparis(siparis_id),
    urun_id           INTEGER NOT NULL REFERENCES urun(urun_id),
    adet              INTEGER NOT NULL,
    birim_fiyat       NUMERIC(10,2) NOT NULL
);
