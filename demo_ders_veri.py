import sqlite3
from database import DB_NAME

def demo_ders_ve_konulari_yukle():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Eklenecek Dersler ve Alt Konuları
    dersler_ve_konular = {
        "Matematik": [
            "Çarpanlar ve Katlar", 
            "Üslü İfadeler", 
            "Kareköklü İfadeler"
        ],
        "Türkçe": [
            "Fiilimsiler", 
            "Cümlenin Ögeleri", 
            "Paragrafta Anlam"
        ],
        "Fen Bilimleri": [
            "Mevsimler ve İklim", 
            "DNA ve Genetik Kod", 
            "Basınç"
        ],
        "İngilizce": [
            "Friendship", 
            "Teen Life", 
            "In the Kitchen"
        ]
    }

    try:
        for ders_adi, konular in dersler_ve_konular.items():
            # 1. Dersi ekle (Eğer sistemde yoksa)
            cursor.execute("INSERT OR IGNORE INTO dersler (ders_adi) VALUES (?)", (ders_adi,))
            
            # 2. Eklenen veya zaten var olan dersin ID'sini çek
            cursor.execute("SELECT id FROM dersler WHERE ders_adi = ?", (ders_adi,))
            ders_id = cursor.fetchone()[0]

            # 3. İlgili dersin alt konularını ekle
            for konu in konular:
                # Konu daha önce eklenmemişse ekle (Çift kaydı önlemek için)
                cursor.execute("SELECT id FROM alt_konular WHERE ders_id = ? AND konu_adi = ?", (ders_id, konu))
                if not cursor.fetchone():
                    cursor.execute("INSERT INTO alt_konular (ders_id, konu_adi) VALUES (?, ?)", (ders_id, konu))

        conn.commit()
        print("✅ 4 adet örnek ders ve her birine 3'er alt konu başarıyla veritabanına eklendi!")
    except Exception as e:
        print(f"❌ Bir hata oluştu: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    demo_ders_ve_konulari_yukle()