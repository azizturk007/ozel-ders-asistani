import flet as ft
import sqlite3
from database import DB_NAME

def rapor_gorunumu(page):
    ogrenci_dropdown = ft.Dropdown(label="Raporu Çıkarılacak Öğrenci", width=350)
    rapor_gövde_alani = ft.Column(spacing=15, expand=True)

    def ogrencileri_yukle():
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, ad_soyad FROM ogrenciler")
        ogrenci_dropdown.options.clear()
        for r in cursor.fetchall():
            ogrenci_dropdown.options.append(ft.dropdown.Option(key=str(r[0]), text=r[1]))
        conn.close()

    def rapor_olustur(e):
        if not ogrenci_dropdown.value: return
        oid = int(ogrenci_dropdown.value)
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute("SELECT ders_ucreti, grup_ucreti FROM ogrenciler WHERE id = ?", (oid,))
        ucretler = cursor.fetchone()
        
        cursor.execute("SELECT ders_tipi, durum, gelmedi, ucret_yansit FROM ders_programi WHERE ogrenci_id = ?", (oid,))
        program_verileri = cursor.fetchall()
        
        toplam_hakedis = 0.0
        for d in program_verileri:
            if d[1] == 1 or (d[2] == 1 and d[3] == 1):
                toplam_hakedis += ucretler[1] if d[0] == "Grup Dersi" else ucretler[0]
                
        cursor.execute("SELECT tarih, miktar FROM odemeler WHERE ogrenci_id = ?", (oid,))
        odeme_gecmisi = cursor.fetchall()
        
        toplam_odenen = sum(o[1] for o in odeme_gecmisi)
        kalan_bakiye = toplam_hakedis - toplam_odenen
        
        cursor.execute("SELECT tarih, saat, ders_adi, ders_tipi, durum, gelmedi FROM ders_programi WHERE ogrenci_id = ? ORDER BY id DESC", (oid,))
        ders_gecmisi = cursor.fetchall()
        conn.close()

        rapor_gövde_alani.controls.clear()
        
        rapor_gövde_alani.controls.append(ft.Container(
            content=ft.Column([
                ft.Text("📊 Öğrenci Cari Hesap Bilgisi", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
                ft.Row([
                    ft.Text(f"💵 Toplam Ödenen: {toplam_odenen:,.2f} TL", color=ft.Colors.GREEN_800, weight=ft.FontWeight.BOLD, size=15),
                    ft.Text(f"🚨 Kalan Bakiye: {kalan_bakiye:,.2f} TL", color=ft.Colors.RED_800, weight=ft.FontWeight.BOLD, size=15)
                ])
            ]),
            bgcolor=ft.Colors.BLUE_50, padding=15, border_radius=10
        ))
        
        # Ödeme Detayları
        if odeme_gecmisi:
            odeme_sutunu = ft.Column()
            for od in odeme_gecmisi:
                odeme_sutunu.controls.append(ft.Text(f"✅ {od[0]} tarihinde {od[1]} TL tahsil edildi.", color=ft.Colors.GREEN_700))
            rapor_gövde_alani.controls.append(ft.Container(content=odeme_sutunu, padding=10, bgcolor=ft.Colors.GREEN_50, border_radius=8))

        rapor_gövde_alani.controls.append(ft.Text("📋 Müfredat ve Planlı Ders Geçmişi", size=16, weight=ft.FontWeight.BOLD))
        
        listview_paneli = ft.ListView(expand=True, spacing=8)
        for d in ders_gecmisi:
            tarih, saat, ders_adi, ders_tipi, durum, gelmedi = d
            if durum == 1:
                bg, renk, etiket = ft.Colors.GREEN_50, ft.Colors.GREEN_900, "İŞLENDİ"
            elif gelmedi == 1:
                bg, renk, etiket = ft.Colors.RED_50, ft.Colors.RED_900, "DEVAMSIZLIK"
            else:
                bg, renk, etiket = ft.Colors.BLUE_50, ft.Colors.BLUE_900, "YAPILMADI / PLANLANDI"

            listview_paneli.controls.append(ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.BOOKMARK_BORDER, color=renk),
                    ft.Column([
                        ft.Text(f"📅 {tarih} - Saat: {saat} | Tür: {ders_tipi}", weight=ft.FontWeight.BOLD, color=renk),
                        ft.Text(f"📖 Konu: {ders_adi}", size=14, color=renk),
                        ft.Text(etiket, size=11, italic=True, color=renk)
                    ], expand=True)
                ]),
                bgcolor=bg, padding=10, border_radius=8
            ))
            
        rapor_gövde_alani.controls.append(listview_paneli)
        page.update()

    ogrenci_dropdown.on_change = rapor_olustur
    ogrencileri_yukle()

    return ft.Column([
        ft.Text("Öğrenci Akademik & Cari Raporlama", size=22, weight=ft.FontWeight.BOLD),
        ogrenci_dropdown,
        ft.Divider(),
        rapor_gövde_alani
    ], expand=True)