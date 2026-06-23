import flet as ft
import sqlite3
import json
from database import DB_NAME

def ogrenci_detay_gorunumu(page, ogrenci_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT ad_soyad, email, okul, adres, sinif, ders_tipi, uygun_zamanlar, ders_ucreti, grup_ucreti, aldigi_ders FROM ogrenciler WHERE id = ?", (ogrenci_id,))
    ogr = cursor.fetchone()
    
    if not ogr:
        conn.close()
        return ft.Text("Öğrenci kaydı bulunamadı!", color=ft.Colors.RED)

    # Müsaitlik durumunu çözümlüyoruz
    try:
        dolu_zamanlar = json.loads(ogr[6]) if ogr[6] else []
    except:
        dolu_zamanlar = []

    # Sadece okuma amaçlı (tıklanamayan) görsel zaman tablosu oluşturuyoruz
    gunler = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]
    saatler = [f"{i:02}:00" for i in range(9, 22)]
    tablo_satirlari = []

    for saat in saatler:
        hucreler = [ft.DataCell(ft.Text(saat, weight=ft.FontWeight.BOLD, size=12))]
        for gun in gunler:
            anahtar = f"{gun}-{saat}"
            dolu_mu = anahtar in dolu_zamanlar
            
            kutu = ft.Container(
                content=ft.Text("Dolu" if dolu_mu else "Uygun", color=ft.Colors.WHITE, size=10),
                bgcolor=ft.Colors.RED_400 if dolu_mu else ft.Colors.GREEN_400,
                padding=8,
                border_radius=5
            )
            hucreler.append(ft.DataCell(kutu))
        tablo_satirlari.append(ft.DataRow(cells=hucreler))

    salt_okunur_tablo = ft.DataTable(
        columns=[ft.DataColumn(ft.Text("Saat"))] + [ft.DataColumn(ft.Text(g)) for g in gunler],
        rows=tablo_satirlari,
        heading_row_color=ft.Colors.BLUE_GREY_100,
        column_spacing=15,
        data_row_min_height=40,
        data_row_max_height=40
    )

    cursor.execute("SELECT DISTINCT ders_adi, ders_tipi FROM ders_programi WHERE ogrenci_id = ?", (ogrenci_id,))
    aldigi_dersler = cursor.fetchall()

    cursor.execute("SELECT yakinlik, ad_soyad, telefon FROM veliler WHERE ogrenci_id = ?", (ogrenci_id,))
    veliler = cursor.fetchall()
    conn.close()

    veli_sutunu = ft.Column(spacing=5)
    for v in veliler:
        veli_sutunu.controls.append(ft.Text(f"👤 {v[0]} - {v[1]}: 📞 {v[2]}", size=14))

    return ft.ListView(
        expand=True,
        spacing=15,
        controls=[
            ft.Container(
                content=ft.Column([
                    ft.Text(ogr[0], size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
                    ft.Text(f"🏫 Sınıf Durumu: {ogr[4] or 'Girilmemiş'} | Okul: {ogr[2]}", size=14),
                    ft.Text(f"📚 Kayıtlı Ana Branşı: {ogr[9] or 'Belirtilmedi'}", size=14, weight=ft.FontWeight.W_500),
                    ft.Text(f"💰 Ücretler -> Birebir: {ogr[7]} TL / Grup: {ogr[8]} TL", size=14, weight=ft.FontWeight.BOLD)
                ]),
                bgcolor=ft.Colors.BLUE_50, padding=15, border_radius=10
            ),
            ft.Text("🗓 Öğrenci Uygunluk Çizelgesi", size=18, weight=ft.FontWeight.BOLD),
            ft.Column([salt_okunur_tablo], scroll=ft.ScrollMode.AUTO, height=250),
            ft.Divider(),
            ft.Text("👨‍👩‍👦 Aile ve Veli İletişim Bilgileri", size=18, weight=ft.FontWeight.BOLD),
            ft.Container(content=veli_sutunu, bgcolor=ft.Colors.GREY_50, padding=15, border_radius=10)
        ]
    )