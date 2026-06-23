import flet as ft
import sqlite3
from database import DB_NAME

def liste_gorunumu(page):
    def get_ogrenciler():
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, ad_soyad, okul, sinif FROM ogrenciler")
        data = cursor.fetchall()
        conn.close()
        return data

    liste_alani = ft.ListView(expand=True, spacing=10)

    def liste_yenile():
        liste_alani.controls.clear()
        for o in get_ogrenciler():
            liste_alani.controls.append(
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.ACCOUNT_BOX, color=ft.Colors.BLUE_ACCENT, size=32),
                    title=ft.Text(o[1], weight=ft.FontWeight.BOLD, size=16),
                    subtitle=ft.Text(f"🏫 Sınıf: {o[3] or 'Belirtilmedi'} | Okul: {o[2]}"),
                    trailing=ft.Icon(ft.Icons.ARROW_FORWARD_IOS, size=14, color=ft.Colors.GREY_400),
                    on_click=lambda e, ogrenci_id=o[0]: page.goster_detay(ogrenci_id)
                )
            )

    liste_yenile()

    return ft.Column([
        ft.Text("Kayıtlı Aktif Öğrenci Listesi", size=22, weight=ft.FontWeight.BOLD),
        ft.Text("Öğrencinin aldığı dersleri ve profil detaylarını görmek için isme tıklayın.", color=ft.Colors.GREY_600),
        ft.Divider(),
        liste_alani
    ], expand=True)