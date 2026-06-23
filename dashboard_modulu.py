import flet as ft
import sqlite3
from datetime import datetime
from database import DB_NAME

def dashboard_gorunumu(page):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    bugun = datetime.now().strftime("%d.%m.%Y")
    
    # Sadece bugünün planlanmış derslerini çekiyoruz
    cursor.execute("""
        SELECT dp.saat, o.ad_soyad, dp.ders_adi, dp.durum 
        FROM ders_programi dp 
        JOIN ogrenciler o ON dp.ogrenci_id = o.id
        WHERE dp.tarih = ? 
        ORDER BY dp.saat
    """, (bugun,))
    
    bugunku_dersler = cursor.fetchall()
    conn.close()

    bugun_liste = ft.Column(spacing=10)
    
    if bugunku_dersler:
        for d in bugunku_dersler:
            ikon = ft.Icons.CHECK_CIRCLE if d[3] == 1 else ft.Icons.SCHEDULE
            renk = ft.Colors.GREEN if d[3] == 1 else ft.Colors.ORANGE
            
            bugun_liste.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ikon, color=renk, size=30),
                        ft.Column([
                            ft.Text(f"Saat: {d[0]} - {d[1]}", weight=ft.FontWeight.BOLD, size=16),
                            ft.Text(f"İşlenecek: {d[2]}", size=14, color=ft.Colors.GREY_700)
                        ])
                    ]),
                    bgcolor=ft.Colors.BLUE_GREY_50, padding=10, border_radius=8
                )
            )
    else:
        bugun_liste.controls.append(
            ft.Text("Bugün için planlanmış bir ders bulunmuyor.", italic=True, color=ft.Colors.GREY_600)
        )

    return ft.ListView(
        expand=True,
        spacing=20,
        controls=[
            ft.Text(f"Bugünün Ders Programı ({bugun})", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            bugun_liste
        ]
    )