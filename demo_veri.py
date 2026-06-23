import sqlite3
from database import DB_NAME

def demo_verileri_yukle():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Yeni formata uygun Örnek Öğrenciler 
    # (Ad, Email, Okul, Adres, Sınıf, Tip, Zaman, Ders Ücreti, Grup Ücreti)
    ogrenciler = [
        ("Çınar Yılmaz", "cinar.y@ornek.com", "Atatürk Anadolu Lisesi", "Bornova / İzmir", "LGS 8. Sınıf", "1-1 Özel Ders", "Cumartesi 14:00", 500, 300),
        ("Toprak Kaya", "toprak.k@ornek.com", "Buca Fen Lisesi", "Buca / İzmir", "YKS 12. Sınıf", "Grup Ders", "Pazar 10:00", 600, 350),
        ("Hakan Demir", "hakan.d@ornek.com", "Karşıyaka Lisesi", "Karşıyaka / İzmir", "Ara Sınıf 10", "1-1 Özel Ders", "Cuma 18:00", 450, 250),
        ("Zeynep Çelik", "zeynep.c@ornek.com", "Gelişim Koleji", "Çiğli / İzmir", "LGS 8. Sınıf", "Grup Ders", "Çarşamba 17:00", 550, 300),
        ("Elif Şahin", "elif.s@ornek.com", "İzmir Kız Lisesi", "Konak / İzmir", "YKS 11. Sınıf", "1-1 Özel Ders", "Salı 19:00", 600, 400)
    ]

    veliler = [
        ("Anne", "Ayşe Yılmaz", "905551112233"),
        ("Baba", "Ahmet Kaya", "905324445566"),
        ("Anne", "Fatma Demir", "905447778899"),
        ("Baba", "Mustafa Çelik", "905051234567"),
        ("Abla", "Zeliha Şahin", "905339876543")
    ]

    try:
        for i in range(len(ogrenciler)):
            cursor.execute("""
                INSERT INTO ogrenciler (ad_soyad, email, okul, adres, sinif, ders_tipi, uygun_zamanlar, ders_ucreti, grup_ucreti) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, ogrenciler[i])
            ogrenci_id = cursor.lastrowid
            
            veli = veliler[i]
            cursor.execute("INSERT INTO veliler (ogrenci_id, yakinlik, ad_soyad, telefon) VALUES (?, ?, ?, ?)", 
                           (ogrenci_id, veli[0], veli[1], veli[2]))

        conn.commit()
        print("✅ 5 adet yeni formatlı örnek öğrenci ve veli başarıyla eklendi!")
    except Exception as e:
        print(f"❌ Bir hata oluştu: {e}")
    finally:
        conn.close()

#if __name__ == "__main__":
 #   demo_verileri_yukle()
