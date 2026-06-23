import flet as ft
import pandas as pd
import sqlite3
import os
from database import DB_NAME

def excel_ice_aktar_gorunumu(page):
    # Dosya yolunu yazmak için metin kutusu
    # Android'de genellikle: /storage/emulated/0/Download/dosya_adi.xlsx
    dosya_yolu_input = ft.TextField(
        label="Excel Dosyasının Tam Yolu",
        hint_text="Örn: /storage/emulated/0/Download/ogrenciler.xlsx",
        expand=True
    )

    def aktar_tiklandi(e):
        dosya_yolu = dosya_yolu_input.value.strip()
        
        # Tırnak işaretlerini temizle
        dosya_yolu = dosya_yolu.replace('"', '').replace("'", "")
        
        if not os.path.exists(dosya_yolu):
            page.open(ft.SnackBar(content=ft.Text("Hata: Dosya bulunamadı! Yolu kontrol edin.")))
            page.update()
            return

        try:
            df = pd.read_excel(dosya_yolu)
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            
            # Excel sütun isimlerinin veritabanı ile eşleştiğini varsayıyoruz
            # Örnek sütunlar: ad_soyad, email, okul, adres, sinif, ders_tipi, ders_ucreti
            for _, row in df.iterrows():
                cursor.execute("""
                    INSERT INTO ogrenciler (ad_soyad, email, okul, adres, sinif, ders_tipi, ders_ucreti) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    str(row.get('ad_soyad', '')), 
                    str(row.get('email', '')), 
                    str(row.get('okul', '')), 
                    str(row.get('adres', '')),
                    str(row.get('sinif', '')),
                    str(row.get('ders_tipi', '1-1 Özel Ders')),
                    float(row.get('ders_ucreti', 0))
                ))
            
            conn.commit()
            conn.close()
            page.open(ft.SnackBar(content=ft.Text("Excel başarıyla aktarıldı!", color=ft.Colors.GREEN)))
            dosya_yolu_input.value = "" 
        except Exception as ex:
            page.open(ft.SnackBar(content=ft.Text(f"Aktarım Hatası: {ex}")))
        
        page.update()

    return ft.Column([
        ft.Text("Excel'den Öğrenci Aktar", size=20, weight=ft.FontWeight.BOLD),
        ft.Text("Dosyanın telefonunuzdaki tam yolunu aşağıya yapıştırın.", color=ft.Colors.GREY_700),
        ft.Row([
            dosya_yolu_input,
            ft.ElevatedButton("İçe Aktar", icon=ft.Icons.DOWNLOAD, on_click=aktar_tiklandi)
        ])
    ])