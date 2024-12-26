from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from chromedriver_py import binary_path
import time
import re
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import *

def mail_gonder(sefer_bilgisi, ilk_kontrol=False):
    """
    Belirtilen sefer bilgisiyle mail gönderir
    
    Args:
        sefer_bilgisi (dict veya list): Sefer bilgilerini içeren sözlük veya sözlük listesi
        ilk_kontrol (bool): İlk kontrol için tüm seferleri gönderme
    """
    try:
        # Mail içeriğini hazırla
        mesaj = MIMEMultipart()
        mesaj["From"] = f"TCDD Bilet Bulucu Bot <{GMAIL_USER}>"
        mesaj["To"] = ALICI_MAIL
        
        if ilk_kontrol:
            mesaj["Subject"] = "TCDD Mevcut Seferler Bildirimi!"
            
            # Tüm seferleri içeren body oluştur
            body = "Mevcut Tüm Seferler:\n\n"
            for sefer in sefer_bilgisi:
                body += f"""
Tren: {sefer['tren_no']}
Kalkış-Varış: {sefer['kalkis_saat']} - {sefer['varis_saat']}
Ekonomi Sınıfı Boş Koltuk: {sefer['ekonomi_koltuk']}
------------------------
"""
        else:
            mesaj["Subject"] = "TCDD Yeni Boş Koltuk Bildirimi!"
            
            body = f"""
Yeni Boş Koltuk Bulundu!

Tren: {sefer_bilgisi['tren_no']}
Kalkış-Varış: {sefer_bilgisi['kalkis_saat']} - {sefer_bilgisi['varis_saat']}
Ekonomi Sınıfı Boş Koltuk: {sefer_bilgisi['ekonomi_koltuk']}
"""
        
        body += f"""
Kontrol Zamanı: {datetime.now().strftime('%H:%M:%S')}

İyi yolculuklar dileriz!
TCDD Bilet Bulucu Bot
"""
        
        mesaj.attach(MIMEText(body, "plain"))
        
        # Gmail SMTP sunucusuna bağlan
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            server.send_message(mesaj)
            
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Mail başarıyla gönderildi!")
        
    except Exception as e:
        print(f"\nMail gönderilirken hata oluştu: {str(e)}")

def ekonomi_koltuk_sayisi_bul(driver):
    """
    Sayfadaki tüm seferleri tarar ve ekonomi sınıfındaki boş koltuk sayılarını döndürür
    
    Returns:
        list: Her seferin ekonomi sınıfı koltuk sayısı ve sefer bilgilerini içeren sözlük listesi
    """
    seferler = []
    
    try:
        # Tüm sefer kartlarını bul
        sefer_kartlari = driver.find_elements(By.CLASS_NAME, "card")
        
        for kart in sefer_kartlari:
            try:
                # Sefer detaylarını almak için kartı aç
                detay_btn = kart.find_element(By.CLASS_NAME, "btn-link")
                detay_btn.click()
                time.sleep(1)  # Detayların yüklenmesini bekle
                
                # Sefer bilgilerini al
                tren_no = kart.find_element(By.CLASS_NAME, "textDepartureArrival").text
                kalkis_saat = kart.find_element(By.CLASS_NAME, "textDepartureArea").text.strip()
                varis_saat = kart.find_element(By.CLASS_NAME, "textArrivalArea").text.strip()
                
                # Ekonomi sınıfı butonunu bul
                ekonomi_btn = kart.find_element(By.XPATH, ".//span[contains(text(), 'EKONOMİ')]/../../../..")
                
                # Koltuk sayısını al (parantez içindeki sayıyı çek)
                koltuk_text = ekonomi_btn.find_element(By.CLASS_NAME, "emptySeat").text
                koltuk_sayisi = int(re.search(r'\((\d+)\)', koltuk_text).group(1))
                
                sefer = {
                    'tren_no': tren_no,
                    'kalkis_saat': kalkis_saat,
                    'varis_saat': varis_saat,
                    'ekonomi_koltuk': koltuk_sayisi
                }
                
                seferler.append(sefer)
                
            except Exception as e:
                print(f"Sefer bilgileri alınırken hata: {str(e)}")
                continue
                
    except Exception as e:
        print(f"Seferler taranırken hata: {str(e)}")
    
    return seferler

def sonuclari_yazdir(seferler):
    """Bulunan seferleri ekrana yazdırır"""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Kontrol Sonuçları:")
    if seferler:
        for sefer in seferler:
            print(f"\nTren: {sefer['tren_no']}")
            print(f"Kalkış-Varış: {sefer['kalkis_saat']} - {sefer['varis_saat']}")
            print(f"Ekonomi Sınıfı Boş Koltuk: {sefer['ekonomi_koltuk']}")
    else:
        print("Hiç sefer bulunamadı veya bir hata oluştu.")
    print("-" * 50)

def main():
    """Ana program"""
    svc = webdriver.ChromeService(executable_path=binary_path)
    driver = webdriver.Chrome(service=svc)

    driver.get("https://ebilet.tcddtasimacilik.gov.tr/sefer-listesi")

    print(f"{ILK_BEKLEME_SURESI} saniye içinde sefer arama kriterlerini girin...")
    time.sleep(ILK_BEKLEME_SURESI)

    # İlk kontrol için boş seferler listesi
    onceki_dolu_seferler = []

    try:
        print("\nKontroller başlıyor... (Durdurmak için Ctrl+C'ye basın)")
        
        # İlk kontrolü yap ve tüm seferleri mail at
        bulunan_seferler = ekonomi_koltuk_sayisi_bul(driver)
        sonuclari_yazdir(bulunan_seferler)
        
        if bulunan_seferler:
            print("\nİlk kontrol sonuçları mail olarak gönderiliyor...")
            mail_gonder(bulunan_seferler, ilk_kontrol=True)
        
        # Dolu seferleri kaydet
        onceki_dolu_seferler = [sefer for sefer in bulunan_seferler if sefer['ekonomi_koltuk'] == 0]
        
        # Sürekli kontrol döngüsü
        while True:
            time.sleep(BEKLEME_SURESI)  # Belirlenen süre kadar bekle
            
            # Sayfayı yenile
            driver.refresh()
            time.sleep(SAYFA_YUKLEME_SURESI)  # Sayfanın yüklenmesini bekle
            
            # Seferleri tara ve sonuçları yazdır
            bulunan_seferler = ekonomi_koltuk_sayisi_bul(driver)
            sonuclari_yazdir(bulunan_seferler)
            
            # Daha önce dolu olan seferleri kontrol et
            for sefer in bulunan_seferler:
                tren_no = sefer['tren_no']
                # Bu sefer daha önce dolu muydu?
                onceki_sefer = next((s for s in onceki_dolu_seferler if s['tren_no'] == tren_no), None)
                
                if onceki_sefer and sefer['ekonomi_koltuk'] > 0:
                    # Daha önce doluydu, şimdi boş koltuk var!
                    print(f"\n*** {tren_no} seferinde boş koltuk bulundu! ***")
                    mail_gonder(sefer)
            
            # Dolu seferleri güncelle
            onceki_dolu_seferler = [sefer for sefer in bulunan_seferler if sefer['ekonomi_koltuk'] == 0]

    except KeyboardInterrupt:
        print("\nProgram kullanıcı tarafından durduruldu.")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()