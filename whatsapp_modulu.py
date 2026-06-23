import flet as ft
import sqlite3
import webbrowser
import urllib.parse
from datetime import datetime
from database import DB_NAME

def whatsapp_gorunumu(page):
    ogrenci_dropdown = ft.Dropdown(label="Öğrenci Seçin", width=300)
    veli_dropdown = ft.Dropdown(label="Gönderilecek Veli/Kişi", width=300)
    
    zaman_araligi = ft.RadioGroup(
        content=ft.Row([
            ft.Radio(value="yarin", label="Sadece Yarınki Dersler"),
            ft.Radio(value="haftalik", label="Önümüzdeki 7 Günlük Program")
        ]),
        value="haftalik"
    )
    
    mesaj_onizleme = ft.TextField(
        label="Mesaj Önizleme (Göndermeden önce düzenleyebilirsiniz)", 
        multiline=True, 
        min_lines=6, 
        expand=True
    )
    
    def ogrencileri_yukle():
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, ad_soyad FROM ogrenciler")
        ogrenci_dropdown.options.clear()
        for row in cursor.fetchall():
            ogrenci_dropdown.options.append(ft.dropdown.Option(key=str(row[0]), text=row[1]))
        conn.close()

    def velileri_yukle(e):
        if not ogrenci_dropdown.value:
            return
        
        veli_dropdown.options.clear()
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT ad_soyad, telefon FROM veliler WHERE ogrenci_id = ?", (ogrenci_dropdown.value,))
        veliler = cursor.fetchall()
        conn.close()
        
        for v in veliler:
            # Telefon numarasını WhatsApp formatına uygun hale getiriyoruz (Sadece rakamlar)
            tel_temiz = ''.join(filter(str.isdigit, str(v[1])))
            if not tel_temiz.startswith("90"):
                tel_temiz = "90" + tel_temiz[-10:] # Başına ülke kodu ekle
                
            veli_dropdown.options.append(ft.dropdown.Option(key=tel_temiz, text=f"{v[0]} ({v[1]})"))
        
        veli_dropdown.value = None
        mesaj_olustur()
        page.update()

    def mesaj_olustur(e=None):
        if not ogrenci_dropdown.value:
            return
            
        secili_ogrenci_adi = next((opt.text for opt in ogrenci_dropdown.options if opt.key == str(ogrenci_dropdown.value)), "")
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        # Sadece durumu 0 olan (yapılmamış/bekleyen) dersleri çekiyoruz
        cursor.execute("SELECT tarih, saat, ders_adi FROM ders_programi WHERE durum = 0 AND ders_adi LIKE ?", ('%' + secili_ogrenci_adi + '%',))
        bekleyen_dersler = cursor.fetchall()
        conn.close()
        
        bugun = datetime.now()
        hedef_dersler = []
        
        for d in bekleyen_dersler:
            try:
                # Veritabanındaki DD.MM.YYYY formatını Python tarihine çevir
                ders_tarihi = datetime.strptime(d[0], "%d.%m.%Y")
                fark_gun = (ders_tarihi.date() - bugun.date()).days
                
                # Seçilen aralığa göre filtrele
                if zaman_araligi.value == "yarin" and fark_gun == 1:
                    hedef_dersler.append(d)
                elif zaman_araligi.value == "haftalik" and 0 <= fark_gun <= 7:
                    hedef_dersler.append(d)
            except ValueError:
                pass # Tarih formatı hatalı girilmişse atla
                
        if not hedef_dersler:
            mesaj_onizleme.value = f"Merhaba,\n{secili_ogrenci_adi} için bu tarih aralığında planlanmış bir dersimiz bulunmamaktadır.\nİyi günler dilerim."
        else:
            mesaj = f"Merhaba,\n{secili_ogrenci_adi} için yaklaşan ders programımız aşağıdadır:\n\n"
            for d in hedef_dersler:
                mesaj += f"📅 Tarih: {d[0]}\n⏰ Saat: {d[1]}\n📖 İşlenecek Konu: {d[2]}\n\n"
            mesaj += "İyi çalışmalar dilerim."
            mesaj_onizleme.value = mesaj
            
        page.update()

    def whatsapp_gonder(e):
        telefon = veli_dropdown.value
        mesaj = mesaj_onizleme.value
        
        if not telefon:
            page.show_snack_bar(ft.SnackBar(ft.Text("Lütfen mesajın gönderileceği veliyi seçin!", color=ft.Colors.RED)))
            page.update()
            return
            
        if not mesaj:
            return
            
        # Mesajı URL formatına çevir ve WhatsApp linkini oluştur
        mesaj_url = urllib.parse.quote(mesaj)
        whatsapp_link = f"https://wa.me/{telefon}?text={mesaj_url}"
        
        try:
            # Bilgisayarın varsayılan tarayıcısında (veya uygulamasında) linki açar
            webbrowser.open(whatsapp_link)
            page.show_snack_bar(ft.SnackBar(ft.Text("WhatsApp açılıyor...", color=ft.Colors.GREEN)))
        except Exception as ex:
            page.show_snack_bar(ft.SnackBar(ft.Text(f"Bağlantı açılamadı: {ex}", color=ft.Colors.RED)))
        
        page.update()

    # Değişim tetikleyicileri
    ogrenci_dropdown.on_change = velileri_yukle
    zaman_araligi.on_change = mesaj_olustur
    
    ogrencileri_yukle()

    return ft.Column([
        ft.Text("WhatsApp Ders Hatırlatıcı", size=24, weight=ft.FontWeight.BOLD),
        ft.Text("Öğrenciyi ve hatırlatma aralığını seçerek otomatik WhatsApp mesajı oluşturun.", color=ft.Colors.GREY_700),
        ft.Divider(),
        ft.Row([ogrenci_dropdown, veli_dropdown]),
        ft.Container(height=10),
        ft.Text("Hatırlatma Aralığı:", weight=ft.FontWeight.BOLD),
        zaman_araligi,
        ft.Divider(),
        mesaj_onizleme,
        ft.ElevatedButton(
            "WhatsApp ile Gönder", 
            icon=ft.Icons.SEND, 
            bgcolor=ft.Colors.GREEN_600, 
            color=ft.Colors.WHITE,
            on_click=whatsapp_gonder
        )
    ], expand=True)