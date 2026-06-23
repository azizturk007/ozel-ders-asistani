import sqlite3

DB_NAME = "ders_takip.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ogrenciler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ad_soyad TEXT,
            email TEXT,
            okul TEXT,
            adres TEXT,
            sinif TEXT,
            ders_tipi TEXT,
            uygun_zamanlar TEXT,
            ders_ucreti REAL DEFAULT 0,
            grup_ucreti REAL DEFAULT 0
        )
    """)
    
    # Yeni eklenen "aldığı ders" sütununu hata vermeden veritabanına entegre ediyoruz
    try:
        cursor.execute("ALTER TABLE ogrenciler ADD COLUMN aldigi_ders TEXT")
    except sqlite3.OperationalError:
        pass
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS veliler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ogrenci_id INTEGER,
            yakinlik TEXT,
            ad_soyad TEXT,
            telefon TEXT,
            FOREIGN KEY(ogrenci_id) REFERENCES ogrenciler(id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dersler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ders_adi TEXT UNIQUE
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alt_konular (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ders_id INTEGER,
            konu_adi TEXT,
            FOREIGN KEY(ders_id) REFERENCES dersler(id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ders_programi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ogrenci_id INTEGER,
            ders_adi TEXT,
            tarih TEXT,
            saat TEXT,
            ders_tipi TEXT,
            durum INTEGER DEFAULT 0,
            gelmedi INTEGER DEFAULT 0,
            ucret_yansit INTEGER DEFAULT 1,
            FOREIGN KEY(ogrenci_id) REFERENCES ogrenciler(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS odemeler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ogrenci_id INTEGER,
            tarih TEXT,
            miktar REAL,
            FOREIGN KEY(ogrenci_id) REFERENCES ogrenciler(id)
        )
    """)
    
    conn.commit()
    conn.close()