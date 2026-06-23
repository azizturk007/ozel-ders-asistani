import flet as ft
import sqlite3
from database import DB_NAME

def ders_ve_konu_gorunumu(page):
    yeni_ders_input = ft.TextField(label="Yeni Branş / Ders Ekle")
    ders_dropdown = ft.Dropdown(label="İncelenecek Dersi Seçin")
    
    konu_listesi_alani = ft.Column(spacing=5)
    yeni_konu_input = ft.TextField(label="Bu Derse Yeni Alt Konu Ekle", expand=True)
    
    def dersleri_yukle():
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, ders_adi FROM dersler")
        ders_dropdown.options.clear()
        for r in cursor.fetchall():
            ders_dropdown.options.append(ft.dropdown.Option(key=str(r[0]), text=r[1]))
        conn.close()

    def konulari_getir(e):
        if not ders_dropdown.value: return
        konu_listesi_alani.controls.clear()
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT konu_adi FROM alt_konular WHERE ders_id = ?", (ders_dropdown.value,))
        konular = cursor.fetchall()
        conn.close()

        for k in konular:
            konu_listesi_alani.controls.append(
                ft.Row([ft.Icon(ft.Icons.SUBDIRECTORY_ARROW_RIGHT), ft.Text(k[0], size=16)])
            )
        page.update()

    def manuel_ders_ekle(e):
        if not yeni_ders_input.value: return
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO dersler (ders_adi) VALUES (?)", (yeni_ders_input.value,))
            conn.commit()
            page.show_snack_bar(ft.SnackBar(ft.Text("Ders başarıyla eklendi!", color=ft.Colors.GREEN)))
            yeni_ders_input.value = ""
            dersleri_yukle()
        except sqlite3.IntegrityError:
            page.show_snack_bar(ft.SnackBar(ft.Text("Bu ders zaten sistemde var!", color=ft.Colors.RED)))
        conn.close()
        page.update()

    def manuel_konu_ekle(e):
        if not ders_dropdown.value or not yeni_konu_input.value: return
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO alt_konular (ders_id, konu_adi) VALUES (?, ?)", (int(ders_dropdown.value), yeni_konu_input.value))
        conn.commit()
        conn.close()
        yeni_konu_input.value = ""
        konulari_getir(None)

    ders_dropdown.on_change = konulari_getir
    dersleri_yukle()

    return ft.ListView(
        expand=True, spacing=20,
        controls=[
            ft.Text("Müfredat ve Alt Konu Yönetimi", size=22, weight=ft.FontWeight.BOLD),
            ft.Row([yeni_ders_input, ft.ElevatedButton("Yeni Branş Ekle", on_click=manuel_ders_ekle)]),
            ft.Divider(),
            ders_dropdown,
            ft.Container(
                content=konu_listesi_alani,
                padding=15, bgcolor=ft.Colors.GREY_50, border_radius=10
            ),
            ft.Row([
                yeni_konu_input, 
                ft.ElevatedButton("Konuyu Derse Ekle", on_click=manuel_konu_ekle, bgcolor=ft.Colors.BLUE_600, color=ft.Colors.WHITE)
            ])
        ]
    )