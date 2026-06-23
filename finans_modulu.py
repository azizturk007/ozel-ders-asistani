import flet as ft
import sqlite3
from datetime import datetime, timedelta
from database import DB_NAME

def finans_gorunumu(page):
    ogrenci_dropdown = ft.Dropdown(label="Finansal Durumu İncelenecek Öğrenci", width=320)
    
    bakiye_text = ft.Text("Kalan Güncel Alacak: 0 TL", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_700)
    tahsilat_input = ft.TextField(label="Alınan Ödeme Tutarı (TL)", width=160)
    
    # 1 Haftalık Onay Listesi İçin Alan
    haftalik_onay_alani = ft.Column(spacing=10)

    def ogrencileri_yukle():
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, ad_soyad FROM ogrenciler")
        ogrenci_dropdown.options.clear()
        for row in cursor.fetchall():
            ogrenci_dropdown.options.append(ft.dropdown.Option(key=str(row[0]), text=row[1]))
        conn.close()

    def finans_ve_onay_hesapla(e=None):
        if not ogrenci_dropdown.value: return
        oid = int(ogrenci_dropdown.value)
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Öğrencinin ücretlerini çek
        cursor.execute("SELECT ders_ucreti, grup_ucreti FROM ogrenciler WHERE id = ?", (oid,))
        ucretler = cursor.fetchone()
        
        # 1. Bakiye Hesaplama
        cursor.execute("SELECT ders_tipi FROM ders_programi WHERE ogrenci_id = ? AND durum = 1 AND ucret_yansit = 1", (oid,))
        gecerli_dersler = cursor.fetchall()
        
        toplam_hakedis = 0.0
        for d in gecerli_dersler:
            toplam_hakedis += ucretler[1] if d[0] == "Grup Dersi" else ucretler[0]
                
        cursor.execute("SELECT SUM(miktar) FROM odemeler WHERE ogrenci_id = ?", (oid,))
        toplam_odenen = cursor.fetchone()[0] or 0.0
        
        kalan = toplam_hakedis - toplam_odenen
        bakiye_text.value = f"Kalan Net Bakiye: {kalan:,.2f} TL"
        bakiye_text.color = ft.Colors.RED_700 if kalan > 0 else ft.Colors.GREEN_700

        # 2. Son 7 Günlük Dersleri Çekme (Onay Listesi İçin)
        bugun_dt = datetime.now()
        bir_hafta_once = (bugun_dt - timedelta(days=7)).strftime("%d.%m.%Y")
        
        # Tüm dersleri çekip Python'da tarih sırasına göre süzüyoruz
        cursor.execute("SELECT id, tarih, saat, ders_adi, durum, ucret_yansit FROM ders_programi WHERE ogrenci_id = ? ORDER BY id DESC", (oid,))
        tum_dersler = cursor.fetchall()
        conn.close()

        haftalik_onay_alani.controls.clear()
        
        son_hafta_var_mi = False
        for d in tum_dersler:
            try:
                ders_tarihi = datetime.strptime(d[1], "%d.%m.%Y")
                fark_gun = (bugun_dt - ders_tarihi).days
                # Son 7 gün ile bugün dahil olan dersleri listele
                if 0 <= fark_gun <= 8:
                    son_hafta_var_mi = True
                    
                    # Onay Değişim Fonksiyonu (Veritabanını ve bakiyeyi anında günceller)
                    def onay_degistir(e, ders_id=d[0]):
                        secim = e.control.value
                        conn2 = sqlite3.connect(DB_NAME)
                        cursor2 = conn2.cursor()
                        if secim == "yapildi":
                            cursor2.execute("UPDATE ders_programi SET durum = 1, gelmedi = 0, ucret_yansit = 1 WHERE id = ?", (ders_id,))
                        elif secim == "iptal":
                            cursor2.execute("UPDATE ders_programi SET durum = 1, gelmedi = 1, ucret_yansit = 0 WHERE id = ?", (ders_id,))
                        conn2.commit()
                        conn2.close()
                        finans_ve_onay_hesapla() # Listeyi ve bakiyeyi yenile
                        page.show_snack_bar(ft.SnackBar(ft.Text("Ders durumu güncellendi, bakiye yeniden hesaplandı!", color=ft.Colors.GREEN)))

                    # Mevcut durum tespiti
                    mevcut_secim = None
                    if d[4] == 1 and d[5] == 1: mevcut_secim = "yapildi"
                    elif d[4] == 1 and d[5] == 0: mevcut_secim = "iptal"

                    r_group = ft.RadioGroup(
                        content=ft.Row([
                            ft.Radio(value="yapildi", label="Yapıldı (Ücret Ekle)"),
                            ft.Radio(value="iptal", label="İptal (Ücret Ekleme)")
                        ]),
                        value=mevcut_secim,
                        on_change=lambda e, did=d[0]: onay_degistir(e, did)
                    )

                    haftalik_onay_alani.controls.append(
                        ft.Container(
                            content=ft.Column([
                                ft.Text(f"📅 {d[1]} {d[2]} | {d[3]}", weight=ft.FontWeight.BOLD),
                                r_group
                            ]),
                            bgcolor=ft.Colors.BLUE_50, padding=10, border_radius=8
                        )
                    )
            except ValueError:
                pass

        if not son_hafta_var_mi:
            haftalik_onay_alani.controls.append(ft.Text("Son 1 haftaya ait ders kaydı bulunamadı.", italic=True))

        page.update()

    def odeme_kaydet_click(e):
        if not ogrenci_dropdown.value or not tahsilat_input.value: return
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO odemeler (ogrenci_id, tarih, miktar) VALUES (?, ?, ?)",
                       (int(ogrenci_dropdown.value), datetime.now().strftime("%d.%m.%Y"), float(tahsilat_input.value)))
        conn.commit()
        conn.close()
        tahsilat_input.value = ""
        finans_ve_onay_hesapla()

    ogrenci_dropdown.on_change = finans_ve_onay_hesapla
    ogrencileri_yukle()

    return ft.ListView(
        expand=True, spacing=15,
        controls=[
            ft.Text("Finans Hesap ve Haftalık Ders Onay Ekranı", size=24, weight=ft.FontWeight.BOLD),
            ogrenci_dropdown,
            ft.Divider(),
            ft.Text("Geçtiğimiz 1 Haftanın Dersleri (Ücretlendirme Onayı)", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
            ft.Text("Buradan yaptığınız seçimler bakiyeyi anlık olarak artırır veya azaltır.", size=12, color=ft.Colors.GREY_600),
            haftalik_onay_alani,
            ft.Divider(),
            ft.Container(
                content=ft.Column([bakiye_text]),
                bgcolor=ft.Colors.GREY_100, padding=20, border_radius=10
            ),
            ft.Divider(),
            ft.Text("Tahsilat Giriş Ekranı", size=16, weight=ft.FontWeight.BOLD),
            ft.Row([tahsilat_input, ft.ElevatedButton("Ödemeyi Al ve İşle", on_click=odeme_kaydet_click, bgcolor=ft.Colors.GREEN_600, color=ft.Colors.WHITE)])
        ]
    )