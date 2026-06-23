import flet as ft
from database import init_db
from ogrenci_modulu import ogrenci_kayit_gorunumu
from ders_modulu import ders_ve_konu_gorunumu
from finans_modulu import finans_gorunumu
from liste_modulu import liste_gorunumu
from takvim_modulu import takvim_gorunumu
from dashboard_modulu import dashboard_gorunumu
from rapor_modulu import rapor_gorunumu
from yedek_modulu import yedek_gorunumu

def main(page: ft.Page):
    init_db()
    
    page.title = "Özel Ders Asistanı v2"
    page.theme_mode = ft.ThemeMode.LIGHT
    
    ana_govde = ft.Column(expand=True)

    def ana_ekrana_don(e=None):
        ana_govde.controls.clear()
        ana_govde.controls.append(dashboard_gorunumu(page))
        page.update()

    # Varsayılan başlangıç ekranı
    ana_ekrana_don()

    # Her modülün tepesinde görünmesini sağlayacak ortak bir Başlık barı oluşturucu
    def modul_kapsayici(icerik_fonksiyonu):
        return ft.Column(
            expand=True,
            controls=[
                ft.Row([
                    ft.IconButton(icon=ft.Icons.HOME, icon_color=ft.Colors.BLUE_600, icon_size=30, on_click=ana_ekrana_don, tooltip="Ana Ekrana Dön"),
                    ft.Text("Ana Ekran", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_600)
                ]),
                icerik_fonksiyonu(page)
            ]
        )

    def goster_detay(ogr_id):
        ana_govde.controls.clear()
        from detay_modulu import ogrenci_detay_gorunumu
        ana_govde.controls.append(modul_kapsayici(lambda p: ogrenci_detay_gorunumu(p, ogr_id)))
        page.update()

    page.goster_detay = goster_detay

    def menuyu_guncelle(e):
        ana_govde.controls.clear()
        secim = e.control.data
        
        if secim == "dashboard":
            ana_ekrana_don()
        elif secim == "liste":
            ana_govde.controls.append(modul_kapsayici(liste_gorunumu))
        elif secim == "ogrenci":
            ana_govde.controls.append(modul_kapsayici(ogrenci_kayit_gorunumu))
        elif secim == "ders":
            ana_govde.controls.append(modul_kapsayici(ders_ve_konu_gorunumu))
        elif secim == "takvim":
            ana_govde.controls.append(modul_kapsayici(takvim_gorunumu))
        elif secim == "finans":
            ana_govde.controls.append(modul_kapsayici(finans_gorunumu))
        elif secim == "rapor":
            ana_govde.controls.append(modul_kapsayici(rapor_gorunumu))
        elif secim == "yedek":
            ana_govde.controls.append(modul_kapsayici(yedek_gorunumu))
            
        page.update()

    page.add(
        ft.Row(controls=[
            ft.TextButton("Ana Ekran", data="dashboard", on_click=menuyu_guncelle, icon=ft.Icons.DASHBOARD),
            ft.TextButton("Kayıt", data="ogrenci", on_click=menuyu_guncelle),
            ft.TextButton("Liste", data="liste", on_click=menuyu_guncelle),
            ft.TextButton("Dersler", data="ders", on_click=menuyu_guncelle),
            ft.TextButton("Takvim", data="takvim", on_click=menuyu_guncelle),
            ft.TextButton("Finans", data="finans", on_click=menuyu_guncelle),
            ft.TextButton("Rapor", data="rapor", on_click=menuyu_guncelle),
            ft.TextButton("Yedek", data="yedek", on_click=menuyu_guncelle),
        ], scroll=ft.ScrollMode.AUTO),
        ft.Divider(),
        ana_govde
    )

if __name__ == "__main__":
    ft.app(target=main)