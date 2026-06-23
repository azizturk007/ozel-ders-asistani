import flet as ft
import sqlite3
import json
from database import DB_NAME

def ogrenci_kayit_gorunumu(page):
    ad_input = ft.TextField(label="Öğrenci Adı Soyadı")
    email_input = ft.TextField(label="E-posta")
    okul_input = ft.TextField(label="Okul")
    adres_input = ft.TextField(label="Adres")
    
    # Sınıf girişini açılır menü (Dropdown) yaptık
    sinif_dropdown = ft.Dropdown(
        label="Öğrencinin Sınıfı",
        options=[
            ft.dropdown.Option("İlkokul"),
            ft.dropdown.Option("5. Sınıf"), ft.dropdown.Option("6. Sınıf"),
            ft.dropdown.Option("7. Sınıf"), ft.dropdown.Option("8. Sınıf"),
            ft.dropdown.Option("9. Sınıf"), ft.dropdown.Option("10. Sınıf"),
            ft.dropdown.Option("11. Sınıf"), ft.dropdown.Option("12. Sınıf"),
            ft.dropdown.Option("Üniversite"), ft.dropdown.Option("Yurtdışı")
        ],
        width=200
    )
    
    ders_tipi_dropdown = ft.Dropdown(
        label="Ders Alım Türü",
        options=[ft.dropdown.Option("1-1 Özel Ders"), ft.dropdown.Option("Grup Ders")],
        value="1-1 Özel Ders"
    )
    
    ders_secimi_dropdown = ft.Dropdown(label="Aldığı Branş / Ders")
    
    ders_ucret_input = ft.TextField(label="Birebir Ders Ücreti (TL)", value="0", width=180)
    grup_ucret_input = ft.TextField(label="Grup Ders Ücreti (TL)", value="0", width=180)

    # Dinamik Veli Alanı
    veliler_listesi = ft.Column()
    
    def veli_alani_olustur(baslik):
        return ft.Row([
            ft.TextField(label=f"{baslik} Adı Soyadı", expand=True),
            ft.TextField(label="Yakınlık (Örn: Anne)", width=150),
            ft.TextField(label="Telefon", width=150)
        ])

    veliler_listesi.controls.append(veli_alani_olustur("1. Veli"))

    def ikinci_veli_ekle(e):
        if len(veliler_listesi.controls) < 2:
            veliler_listesi.controls.append(veli_alani_olustur("2. Veli"))
            page.update()

    # Etkileşimli Zaman Tablosu
    gunler = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]
    saatler = [f"{i:02}:00" for i in range(9, 22)]
    zaman_hucreleri = {}

    def hucre_tiklandi(e):
        mevcut_renk = e.control.bgcolor
        e.control.bgcolor = ft.Colors.RED_400 if mevcut_renk == ft.Colors.GREEN_400 else ft.Colors.GREEN_400
        e.control.content.value = "Dolu" if e.control.bgcolor == ft.Colors.RED_400 else "Uygun"
        page.update()

    tablo_satirlari = []
    for saat in saatler:
        hucreler = [ft.DataCell(ft.Text(saat, weight=ft.FontWeight.BOLD))]
        for gun in gunler:
            anahtar = f"{gun}-{saat}"
            kutu = ft.Container(
                content=ft.Text("Uygun", color=ft.Colors.WHITE, size=10),
                bgcolor=ft.Colors.GREEN_400,
                padding=10,
                border_radius=5,
                on_click=hucre_tiklandi,
                data=anahtar
            )
            zaman_hucreleri[anahtar] = kutu
            hucreler.append(ft.DataCell(kutu))
        tablo_satirlari.append(ft.DataRow(cells=hucreler))

    zaman_tablosu = ft.DataTable(
        columns=[ft.DataColumn(ft.Text("Saat"))] + [ft.DataColumn(ft.Text(g)) for g in gunler],
        rows=tablo_satirlari,
        heading_row_color=ft.Colors.BLUE_GREY_100,
    )

    def dersleri_yukle():
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT ders_adi FROM dersler")
        ders_secimi_dropdown.options.clear()
        for row in cursor.fetchall():
            ders_secimi_dropdown.options.append(ft.dropdown.Option(row[0]))
        conn.close()
        page.update()

    def kaydet_click(e):
        if not ad_input.value:
            page.show_snack_bar(ft.SnackBar(ft.Text("Öğrenci adı alanı boş bırakılamaz!", color=ft.Colors.RED)))
            return
        
        dolu_zamanlar = [anahtar for anahtar, kutu in zaman_hucreleri.items() if kutu.bgcolor == ft.Colors.RED_400]
        zaman_json = json.dumps(dolu_zamanlar)

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO ogrenciler (ad_soyad, email, okul, adres, sinif, ders_tipi, uygun_zamanlar, ders_ucreti, grup_ucreti, aldigi_ders)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (ad_input.value, email_input.value, okul_input.value, adres_input.value,
              sinif_dropdown.value, ders_tipi_dropdown.value, zaman_json,
              float(ders_ucret_input.value or 0), float(grup_ucret_input.value or 0), ders_secimi_dropdown.value))
        
        ogr_id = cursor.lastrowid
        
        for veli_row in veliler_listesi.controls:
            v_ad = veli_row.controls[0].value
            v_yak = veli_row.controls[1].value
            v_tel = veli_row.controls[2].value
            if v_ad:
                cursor.execute("INSERT INTO veliler (ogrenci_id, yakinlik, ad_soyad, telefon) VALUES (?, ?, ?, ?)", 
                               (ogr_id, v_yak, v_ad, v_tel))
            
        conn.commit()
        conn.close()
        page.show_snack_bar(ft.SnackBar(ft.Text("Öğrenci başarıyla kaydedildi!", color=ft.Colors.GREEN)))
        
        ad_input.value = email_input.value = okul_input.value = adres_input.value = ""
        sinif_dropdown.value = ders_secimi_dropdown.value = None
        ders_ucret_input.value = grup_ucret_input.value = "0"
        for kutu in zaman_hucreleri.values():
            kutu.bgcolor = ft.Colors.GREEN_400
            kutu.content.value = "Uygun"
        page.update()

    dersleri_yukle()

    return ft.ListView(
        expand=True, spacing=15,
        controls=[
            ft.Text("Öğrenci Profil ve İdari Kayıt Modülü", size=22, weight=ft.FontWeight.BOLD),
            ft.Row([ad_input, sinif_dropdown, okul_input]), 
            ft.Row([email_input, adres_input]),
            ft.Row([ders_tipi_dropdown, ders_secimi_dropdown], expand=True),
            ft.Divider(),
            ft.Text("Müsaitlik Çizelgesi (Kapatmak istediğiniz saatlere tıklayıp kırmızı yapın)", size=16, weight=ft.FontWeight.BOLD),
            ft.Column([zaman_tablosu], scroll=ft.ScrollMode.AUTO, height=300),
            ft.Divider(),
            ft.Text("Öğrenci Ücret Tanımlama", size=18, weight=ft.FontWeight.BOLD),
            ft.Row([ders_ucret_input, grup_ucret_input]),
            ft.Divider(),
            ft.Text("Veli Bilgileri", size=18, weight=ft.FontWeight.BOLD),
            veliler_listesi,
            ft.TextButton("İkinci Veli Ekle", icon=ft.Icons.ADD, on_click=ikinci_veli_ekle),
            ft.ElevatedButton("Öğrenci Kaydını Tamamla", icon=ft.Icons.SAVE, on_click=kaydet_click, bgcolor=ft.Colors.BLUE_600, color=ft.Colors.WHITE)
        ]
    )