import flet as ft
import sqlite3
from datetime import datetime, timedelta
from database import DB_NAME

def takvim_gorunumu(page):
    ogrenci_dropdown = ft.Dropdown(label="Öğrenci Seçin", width=250)
    ders_dropdown = ft.Dropdown(label="İşlenecek Ders / Branş", width=250)
    konu_dropdown = ft.Dropdown(label="Alt Konu Seçin", width=250)
    
    tarih_dropdown = ft.Dropdown(label="Tarih Seçin", width=200)
    saat_dropdown = ft.Dropdown(label="Saat Seçin", width=150)
    
    bugun = datetime.now()
    for i in range(-7, 31):
        gun_tarih = bugun + timedelta(days=i)
        tarih_dropdown.options.append(ft.dropdown.Option(gun_tarih.strftime("%d.%m.%Y")))
        
    for h in range(8, 23):
        for m in ["00", "30"]:
            saat_dropdown.options.append(ft.dropdown.Option(f"{h:02}:{m}"))

    tip_dropdown = ft.Dropdown(
        label="Ders Seçeneği / Türü",
        options=[ft.dropdown.Option("Ders"), ft.dropdown.Option("Grup Dersi"), ft.dropdown.Option("Etüt"), ft.dropdown.Option("Sınav")],
        value="Ders"
    )

    liste_alani = ft.ListView(expand=True, spacing=10)

    def verileri_yukle():
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, ad_soyad FROM ogrenciler")
        for r in cursor.fetchall(): ogrenci_dropdown.options.append(ft.dropdown.Option(key=str(r[0]), text=r[1]))
        
        cursor.execute("SELECT id, ders_adi FROM dersler")
        for r in cursor.fetchall(): ders_dropdown.options.append(ft.dropdown.Option(key=str(r[0]), text=r[1]))
        conn.close()

    def konulari_bagla(e):
        if not ders_dropdown.value: return
        konu_dropdown.options.clear()
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT konu_adi FROM alt_konular WHERE ders_id = ?", (ders_dropdown.value,))
        for r in cursor.fetchall(): konu_dropdown.options.append(ft.dropdown.Option(r[0]))
        conn.close()
        konu_dropdown.value = None
        page.update()

    ders_dropdown.on_change = konulari_bagla

    def takvimi_yenile():
        liste_alani.controls.clear()
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT dp.id, o.ad_soyad, dp.ders_adi, dp.tarih, dp.saat, dp.ders_tipi, dp.durum, dp.gelmedi, dp.ucret_yansit 
            FROM ders_programi dp JOIN ogrenciler o ON dp.ogrenci_id = o.id ORDER BY dp.id DESC
        """)
        for d in cursor.fetchall():
            durum = "Yapıldı" if d[6] else "Planlandı"
            if d[7]: durum = "Gelmedi (" + ("Ücretli" if d[8] else "Ücretsiz") + ")"
            
            liste_alani.controls.append(ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.CALENDAR_TODAY, color=ft.Colors.BLUE_400),
                    ft.Column([
                        ft.Text(f"👤 {d[1]} - 📚 {d[2]}", weight=ft.FontWeight.BOLD),
                        ft.Text(f"📅 {d[3]} @ {d[4]} | Tür: {d[5]} | Durum: {durum}", size=12, color=ft.Colors.GREY_700)
                    ], expand=True)
                ]),
                bgcolor=ft.Colors.BLUE_GREY_50, padding=10, border_radius=8
            ))
        conn.close()
        page.update()

    def ders_kaydet(e):
        if not ogrenci_dropdown.value or not ders_dropdown.value or not konu_dropdown.value or not tarih_dropdown.value or not saat_dropdown.value: 
            # GÜNCELLENEN KISIM 1
            page.open(ft.SnackBar(content=ft.Text("Lütfen tüm alanları (Öğrenci, Ders, Konu, Tarih, Saat) seçin!", color=ft.Colors.RED)))
            return
        
        secilen_ders_ismi = next((opt.text for opt in ders_dropdown.options if opt.key == ders_dropdown.value), "")
        birlestirilmis_isim = f"{secilen_ders_ismi} - {konu_dropdown.value}"
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO ders_programi (ogrenci_id, ders_adi, tarih, saat, ders_tipi, gelmedi, ucret_yansit, durum)
            VALUES (?, ?, ?, ?, ?, 0, 1, 0)
        """, (int(ogrenci_dropdown.value), birlestirilmis_isim, tarih_dropdown.value, saat_dropdown.value, tip_dropdown.value))
        conn.commit()
        conn.close()
        
        tarih_dropdown.value = saat_dropdown.value = None
        # GÜNCELLENEN KISIM 2
        page.open(ft.SnackBar(content=ft.Text("Ders takvime başarıyla işlendi!", color=ft.Colors.GREEN)))
        takvimi_yenile()

    verileri_yukle()
    takvimi_yenile()

    return ft.ListView(
        expand=True, spacing=15,
        controls=[
            ft.Text("Takvim, Planlama ve Yoklama", size=24, weight=ft.FontWeight.BOLD),
            ogrenci_dropdown,
            ft.Row([ders_dropdown, konu_dropdown]),
            ft.Row([tarih_dropdown, saat_dropdown, tip_dropdown]),
            ft.ElevatedButton("Takvime Ekle", on_click=ders_kaydet, bgcolor=ft.Colors.BLUE_600, color=ft.Colors.WHITE),
            ft.Divider(),
            liste_alani
        ]
    )