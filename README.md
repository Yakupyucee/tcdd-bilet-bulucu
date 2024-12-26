# TCDD Bilet Bulucu Bot

Bu bot, TCDD'nin e-bilet sitesinde belirtilen seferler için ekonomi sınıfı biletlerini otomatik olarak kontrol eder ve boş bilet bulunduğunda mail ile bildirim gönderir.

## Özellikler

- İlk çalıştırmada mevcut tüm seferleri mail ile bildirir
- Her 20 saniyede bir kontrol yapar
- Daha önce dolu olan bir seferde boşalma olduğunda anında mail gönderir
- Mail bildirimlerinde sefer detayları (tren no, kalkış-varış saati, boş koltuk sayısı) yer alır

## Kurulum

1. Repoyu klonlayın:
```bash
git clone https://github.com/Yakupyucee/tcdd-bilet-bulucu.git
cd tcdd-bilet-bulucu
```

2. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

3. Gmail için "Uygulama Şifresi" oluşturun:
   - Gmail hesabınıza giriş yapın
   - [Google Hesap Ayarları](https://myaccount.google.com/)'na gidin
   - Güvenlik > 2 Adımlı Doğrulama'yı açın
   - Güvenlik > Uygulama Şifreleri'ne gidin
   - "Uygulama Seç" dropdown'undan "Diğer"i seçin
   - İsim olarak "TCDD Bilet Bulucu" yazın
   - "Oluştur" butonuna tıklayın
   - Oluşturulan 16 haneli şifreyi kopyalayın

4. `config.py` dosyasını düzenleyin:
```python
# Mail Ayarları
GMAIL_USER = "your.email@gmail.com"  # Gmail adresiniz
GMAIL_PASSWORD = "xxxx xxxx xxxx xxxx"  # Gmail uygulama şifreniz
ALICI_MAIL = "alici@example.com"  # Bildirim alacak mail adresi

# Program Ayarları (isteğe bağlı)
BEKLEME_SURESI = 20  # İki kontrol arası bekleme süresi (saniye)
SAYFA_YUKLEME_SURESI = 5  # Sayfa yenilendikten sonra bekleme süresi (saniye)
ILK_BEKLEME_SURESI = 30  # Program başlangıcında kullanıcı girişi için bekleme süresi (saniye)
```

## Kullanım

1. Programı çalıştırın:
```bash
python biletbulucu.py
```

2. Program başladığında size 30 saniye süre verecek. Bu sürede:
   - TCDD e-bilet sitesinde nereden-nereye seçimini yapın
   - Tarih seçin
   - Yolcu sayısını belirleyin
   - "Sefer Ara" butonuna tıklayın

3. Program otomatik olarak:
   - İlk kontrolde bulunan tüm seferleri mail ile bildirecek
   - Her 20 saniyede bir kontrol yapacak
   - Dolu olan bir seferde boşalma olduğunda size mail gönderecek

4. Programı durdurmak için:
   - Terminal/Komut penceresinde Ctrl+C tuşlarına basın

## Notlar

- Program çalışırken Chrome tarayıcısı otomatik olarak açılacak ve kontroller bu pencerede yapılacaktır
- Mail göndermek için kullanılan Gmail hesabında "2 Adımlı Doğrulama" açık olmalı ve "Uygulama Şifresi" oluşturulmalıdır
- Program, ekonomi sınıfı biletlerini kontrol eder
- Her kontrolün sonuçlarını terminal ekranında görebilirsiniz

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın. 