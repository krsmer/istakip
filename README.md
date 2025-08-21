# Çalışan Devam Takip Sistemi

Bu sistem bab3. **"Rapor İndir"** butonuyla raporu bilgisayara indir (CSV formatında)
4. Geç kalma durumlarını renkli olarak gör:ızın 7 çalışanı için devam takip sistemidir. Çalışanlar telefonlarından "İşe Geldim" butonuna tıklayarak gelişlerini kaydedebilir, yönetici panelinden de raporlar görülebilir.

## Özellikler

- ✅ Çalışanlar için mobil uyumlu arayüz
- ✅ "İşe Geldim" butonu ile kolay kayıt
- ✅ Yönetici paneli ile detaylı raporlar
- ✅ CSV raporu indirme (Excel'e açılabilir)
- ✅ Gerçek zamanlı saat gösterimi
- ✅ Geç kalma analizi (Zamanında/Hafif Gecikme/Geç Kaldı)
- ✅ Türkçe arayüz

## Kurulum

1. **Python Environment kuruldu ve paketler yüklendi**
   ```powershell
   # Paketler zaten yüklendi:
   # Flask==2.3.3
   # Flask-SQLAlchemy==3.0.5  
   # pandas==2.1.1
   # openpyxl==3.1.2
   # python-dotenv==1.0.0
   ```

2. **Uygulamayı çalıştırın**
   ```powershell
   C:/Users/ahmet/OneDrive/Desktop/istakip/.venv/Scripts/python.exe app.py
   ```

3. **Web tarayıcınızda açın**
   ```
   http://localhost:5000
   ```

## Kullanım

### Çalışanlar için:
1. Ana sayfadan ismini seç
2. "İşE GELDİM" butonuna tıkla
3. Kayıt başarıyla tamamlandı mesajını gör

### Yönetici (Baban) için:
1. "Yönetici Paneli" linkine tıkla
2. Tüm çalışanların geliş kayıtlarını gör
3. "Excel İndir" butonuyla raporu bilgisayara indir
4. Geç kalma durumlarını renkli olarak gör:
   - ✅ Yeşil: Zamanında (08:00 ve öncesi)
   - ⚠️ Sarı: Hafif Gecikme (08:01-09:00)
   - ❌ Kırmızı: Geç Kaldı (09:01 ve sonrası)

## Teknik Detaylar

- **Backend**: Python Flask
- **Veritabanı**: SQLite (calisanlar.db)
- **Frontend**: Bootstrap 5 + JavaScript
- **Rapor**: CSV formatı (Excel'de açılabilir)

## Dosya Yapısı

```
istakip/
├── app.py                 # Ana uygulama
├── requirements.txt       # Python paketleri
├── calisanlar.db         # Veritabanı (otomatik oluşur)
└── templates/
    ├── base.html         # Temel şablon
    ├── index.html        # Ana sayfa
    ├── calisan.html      # Çalışan sayfası  
    └── yonetici.html     # Yönetici paneli
```

## Örnek Çalışanlar

Sistem ilk çalıştırıldığında 7 örnek çalışan otomatik eklenir:
- Ahmet Yılmaz
- Fatma Demir  
- Mehmet Kaya
- Ayşe Öztürk
- Ali Şahin
- Zeynep Çelik
- Mustafa Arslan

## Önemli Notlar

- Her çalışan günde sadece 1 kez kaydedebilir
- Kayıtlar tarih ve saat ile birlikte saklanır
- Excel raporu tüm kayıtları içerir
- Sistem yerel ağda çalışır (0.0.0.0:5000)
- Veritabanı SQLite ile otomatik oluşturulur

## İletişim

Sorularınız için Ahmet ile iletişime geçin.
