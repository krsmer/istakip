# İş Takip Sistemi - Firebase + Vercel

7 çalışan için geliştirilmiş devam takip sistemi. Çalışanlar mobil cihazlarından "İşe Geldim" butonuna tıklayarak giriş yapabilir. GPS konum kontrolü ile sahte girişler engellenir.

## 🚀 Teknolojiler

- **Backend:** Python Flask
- **Veritabanı:** Google Firebase Firestore
- **Deployment:** Vercel
- **GPS:** Haversine Distance Calculation
- **Timezone:** Türkiye (Europe/Istanbul)

## 🔧 Kurulum

### 1. Firebase Projesi Oluşturma
1. [Firebase Console](https://console.firebase.google.com/) üzerinde yeni proje oluşturun
2. Firestore Database'i etkinleştirin
3. Service Account Key'i indirin ve `firebase-service-account.json` olarak kaydedin

### 2. Yerel Geliştirme
```bash
# Bağımlılıkları yükle
pip install -r requirements.txt

# Uygulamayı çalıştır
python app.py
```

### 3. Vercel'e Deploy
```bash
# Vercel CLI yükle
npm install -g vercel

# Deploy et
vercel --prod
```

### 4. Environment Variables
Vercel Dashboard'da şu environment variable'ı ekleyin:
- `FIREBASE_CREDENTIALS`: Firebase service account JSON'unun içeriği

## 📱 Özellikler

### Çalışan Özellikleri
- ✅ Mobil uyumlu arayüz
- ✅ GPS konum kontrolü (150m tolerans)
- ✅ Tek tıkla giriş yapma
- ✅ Günlük tekrar giriş engelleme
- ✅ Türkçe arayüz

### Admin Özellikleri
- ✅ Tüm çalışanların giriş raporları
- ✅ Bireysel çalışan detay sayfaları
- ✅ Excel raporu indirme
- ✅ Gerçek zamanlı veri
- ✅ Güvenli admin paneli

### Güvenlik
- ✅ GPS tabanlı konum kontrolü
- ✅ Admin authentication
- ✅ Firebase security rules
- ✅ HTTPS zorunlu

## 🗂️ Dosya Yapısı

```
istakip/
├── app.py                          # Ana Flask uygulaması
├── firebase_config.py              # Firebase yapılandırması
├── templates/                      # HTML şablonları
│   ├── index.html                 # Ana sayfa
│   ├── calisan.html               # Çalışan giriş sayfası
│   ├── admin_login.html           # Admin girişi
│   ├── admin_panel.html           # Admin paneli
│   └── admin_calisan_detay.html   # Çalışan detay raporu
├── vercel.json                     # Vercel deployment config
├── requirements.txt                # Python bağımlılıkları
├── firebase-service-account.json   # Firebase credentials (gizli)
└── FIREBASE_DEPLOYMENT.md         # Deployment kılavuzu
```

## 🎯 Kullanım

1. **Çalışanlar için:** Ana sayfadan kendi ismine tıklayıp "İşe Geldim" butonuna basın
2. **Admin için:** `/admin` adresinden giriş yapın (Kullanıcı: Hilmi, Şifre: admin123)

## 📊 Veritabanı Yapısı

### Firebase Firestore Collections

#### `attendance` Collection:
```json
{
  "name": "Fatma",
  "check_in_time": "2025-08-21T19:18:56+03:00",
  "date": "2025-08-21",
  "time": "19:18:56",
  "timestamp": "Firestore Server Timestamp"
}
```

## 🌍 GPS Konum Ayarları

`app.py` dosyasındaki `WORK_LOCATION` değişkenini güncelleyin:
```python
WORK_LOCATION = {
    'latitude': 36.938609,    # İş yerinin enlemi
    'longitude': 34.847155,   # İş yerinin boylamı
    'radius': 150            # İzin verilen mesafe (metre)
}
```

## 🔐 Admin Bilgileri

- **Kullanıcı Adı:** Hilmi
- **Şifre:** admin123

## 📈 Monitoring

- Vercel Dashboard'dan deployment loglarını izleyebilirsiniz
- Firebase Console'dan veritabanı kullanımını takip edebilirsiniz
- `/health` endpoint ile sistem durumunu kontrol edebilirsiniz

## 🆘 Sorun Giderme

1. **Firebase Bağlantı Sorunu:** Service account key'in doğru uploadlandığından emin olun
2. **GPS Sorunu:** HTTPS üzerinde çalışıyor olduğunuzdan emin olun
3. **Deployment Sorunu:** Vercel loglarını kontrol edin

## 📞 İletişim

Sorularınız için GitHub Issues kullanabilirsiniz.
