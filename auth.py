import hashlib
import sqlite3
from database import DB_NAME

class AuthManager:
    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    @classmethod
    def verify_password(cls, password: str, hashed_password: str) -> bool:
        return cls.hash_password(password) == hashed_password

    @classmethod
    def register_user(cls, username, password, fullname="", email="") -> bool:
        hashed = cls.hash_password(password)
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO kullanicilar (kullanici_adi, sifre_hash, ad_soyad, eposta) VALUES (?, ?, ?, ?)",
                (username, hashed, fullname, email)
            )
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False

    @classmethod
    def login(cls, username, password):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT sifre_hash, ad_soyad FROM kullanicilar WHERE kullanici_adi = ?", (username,))
        result = cursor.fetchone()
        conn.close()

        if result:
            db_hash, fullname = result
            if cls.verify_password(password, db_hash):
                cls.save_session(username, fullname)
                return {"success": True, "fullname": fullname, "username": username}
        
        return {"success": False, "message": "Kullanıcı adı veya şifre hatalı!"}

    @classmethod
    def create_default_admin(cls):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM kullanicilar")
        if cursor.fetchone()[0] == 0:
            cls.register_user("admin", "admin123", "Özel Ders Öğretmeni", "iletisim@tutors.com")
        conn.close()

    # --- KALICI HAFIZA (SQLITE OTURUM) YÖNETİMİ ---
    @classmethod
    def save_session(cls, username, fullname):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM oturum")
        cursor.execute("INSERT INTO oturum (kullanici_adi, ad_soyad) VALUES (?, ?)", (username, fullname))
        conn.commit()
        conn.close()

    @classmethod
    def get_session(cls):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT kullanici_adi, ad_soyad FROM oturum LIMIT 1")
        result = cursor.fetchone()
        conn.close()
        return result

    @classmethod
    def clear_session(cls):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM oturum")
        conn.commit()
        conn.close()