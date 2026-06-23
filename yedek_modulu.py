import flet as ft
import os
import shutil
from datetime import datetime
from database import DB_NAME

def yedek_gorunumu(page):
    # Android cihazlar için standart İndirilenler klasörü yolu
    android_download_yolu = "/storage/emulated/0/Download"
    
    # APK öncesi bilgisayarda test ederken hata vermemesi için güvenli geçiş
    if os.path.exists(android_download_yolu):
        hedef_klasor = android_download_yolu
        klasor_adi = "Telefonun İndirilenler (Download) Klasörü"
    else:
        hedef_klasor = os.getcwd() 
        klasor_adi = "Uygulama Ana Klasörü (PC Test Modu)"
        
    yedek_yolu_input = ft.TextField(
        label="Geri Yüklenecek Yedek Dosyasının Tam Yolu",
        hint_text="/storage/emulated/0/Download/ders_takip_yedek_20260623_2230.db",
        expand=True
    )

    def yedek_olustur_click(e):
        try:
            if not os.path.exists(DB_NAME):
                page.show_snack_bar(ft.SnackBar(ft.Text("Hata: Mevcut veritabanı dosyası bulunamadı!", color=ft.Colors.RED)))
                return
            
            # Zaman damgalı dosya adı
            zaman_damgasi = datetime.now().strftime("%Y%m%d_%H%M")
            yedek_dosya_adi = f"ders_takip_yedek_{zaman_damgasi}.db"
            hedef_yol = os.path.join(hedef_klasor, yedek_dosya_adi)
            
            # Veritabanını telefonun hafızasına kopyala
            shutil.copy2(DB_NAME, hedef_yol)
            
            page.show_snack_bar(ft.SnackBar(ft.Text(f"✅ Yedek başarıyla alındı!\nKonum: {klasor_adi}\nDosya: {yedek_dosya_adi}", color=ft.Colors.GREEN)))
        except Exception as ex:
            page.show_snack_bar(ft.SnackBar(ft.Text(f"Yedekleme Hatası: {ex}", color=ft.Colors.RED)))
        page.update()

    def yedek_geri_yukle_click(e):
        secilen_yol = yedek_yolu_input.value.strip().replace('"', '').replace("'", "")
        
        if not secilen_yol:
            page.show_snack_bar(ft.SnackBar(ft.Text("Lütfen geri yüklenecek dosya yolunu girin!", color=ft.Colors.RED)))
            return
            
        if not os.path.exists(secilen_yol):
            page.show_snack_bar(ft.SnackBar(ft.Text("Hata: Belirtilen yedek dosyası bulunamadı! Yolu doğru yazdığınızdan emin olun.", color=ft.Colors.RED)))
            return

        try:
            # İşlem öncesi anlık güvenlik yedeği
            if os.path.exists(DB_NAME):
                shutil.copy2(DB_NAME, DB_NAME + ".gecici")
            
            # Seçilen yedeği ana sisteme yaz
            shutil.copy2(secilen_yol, DB_NAME)
            
            # Sorun yoksa geçici dosyayı sil
            if os.path.exists(DB_NAME + ".gecici"):
                os.remove(DB_NAME + ".gecici")
                
            yedek_yolu_input.value = ""
            page.show_snack_bar(ft.SnackBar(ft.Text("🎉 Veritabanı başarıyla telefondaki eski yedeğe döndürüldü!", color=ft.Colors.GREEN)))
        except Exception as ex:
            # Hata durumunda sistemi kurtar
            if os.path.exists(DB_NAME + ".gecici"):
                shutil.move(DB_NAME + ".gecici", DB_NAME)
            page.show_snack_bar(ft.SnackBar(ft.Text(f"Geri Yükleme Hatası: {ex}", color=ft.Colors.RED)))
        page.update()

    return ft.Column([
        ft.Text("Telefon Veritabanı Yedekleme", size=22, weight=ft.FontWeight.BOLD),
        ft.Text("Tüm verilerinizi cihazınızın kendi hafızasında güvence altına alın.", color=ft.Colors.GREY_700),
        ft.Divider(),
        
        # Yedek Alma Bölümü
        ft.Text("1. Sistemi Telefona Yedekle", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800),
        ft.Text("Aşağıdaki butona tıkladığınızda mevcut tüm kayıtlarınız Android telefonunuzun 'İndirilenler (Download)' klasörüne kopyalanır."),
        ft.ElevatedButton(
            "Şimdi Telefona Yedek Al", 
            icon=ft.Icons.PHONE_ANDROID, 
            on_click=yedek_olustur_click,
            bgcolor=ft.Colors.BLUE_600,
            color=ft.Colors.WHITE
        ),
        ft.Divider(),
        
        # Geri Yükleme Bölümü
        ft.Text("2. Yedekten Geri Yükle", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_800),
        ft.Text("Geri yüklemek istediğiniz dosyanın Android klasör yolunu (Örn: /storage/emulated/0/Download/...) aşağıya yapıştırın.", color=ft.Colors.GREY_700),
        ft.Column([
            yedek_yolu_input,
            ft.ElevatedButton(
                "Yedeği Geri Yükle", 
                icon=ft.Icons.SETTINGS_BACKUP_RESTORE, 
                on_click=yedek_geri_yukle_click,
                bgcolor=ft.Colors.RED_600,
                color=ft.Colors.WHITE
            )
        ])
    ], expand=True)