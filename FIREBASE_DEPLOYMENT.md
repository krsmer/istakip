# Firebase + Vercel Deployment Kılavuzu

## 1. Firebase Projesi Kurulumu

### Firebase Console'da Yeni Proje Oluşturma:
1. https://console.firebase.google.com/ adresine gidin
2. "Add project" (Proje ekle) butonuna tıklayın
3. Proje adı: `istakip-attendance` 
4. Google Analytics'i devre dışı bırakabilirsiniz
5. "Create project" butonuna tıklayın

### Firestore Database Kurulumu:
1. Sol menüden "Firestore Database" seçin
2. "Create database" butonuna tıklayın
3. "Start in production mode" seçin
4. Location: `europe-west3` (Frankfurt) seçin
5. "Enable" butonuna tıklayın

### Service Account Key Oluşturma:
1. Sol menüden "Project settings" (⚙️ ikonu) tıklayın
2. "Service accounts" sekmesine gidin
3. "Generate new private key" butonuna tıklayın
4. JSON dosyasını indirin
5. Dosya adını `firebase-service-account.json` yapın
6. Bu dosyayı proje klasörünüze kopyalayın

### Firestore Security Rules:
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Devam kayıtları koleksiyonu
    match /attendance/{document} {
      allow read, write: if true; // Basit demo için - production'da güvenlik kuralları eklenebilir
    }
  }
}
```

## 2. Vercel Deployment

### Vercel CLI Kurulumu:
```bash
npm install -g vercel
```

### Vercel'e Deploy:
```bash
vercel login
vercel --prod
```

### Environment Variables (Vercel Dashboard'da):
1. Vercel dashboard'ınızda projeye gidin
2. "Settings" > "Environment Variables"
3. Yeni environment variable ekleyin:
   - Name: `FIREBASE_CREDENTIALS`
   - Value: `firebase-service-account.json` dosyasının içeriğini kopyalayın (tüm JSON)
   - Environments: Production, Preview, Development seçin

## 3. Test Etme

### Local Test:
```bash
python app_firebase.py
```

### Production Test:
- Vercel URL'nize gidin
- Firebase bağlantısını test edin
- GPS konum kontrolünü test edin

## 4. Firebase Console'da Veri İzleme

1. Firebase Console > Firestore Database
2. "attendance" collection'ını görebilirsiniz
3. Her giriş kaydı bir document olarak saklanır

## 5. Güvenlik (Opsiyonel)

### Firestore Security Rules (Production için):
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /attendance/{document} {
      allow read: if true;
      allow create: if request.auth == null; // Anonim erişim için
      allow update, delete: if false; // Güvenlik için
    }
  }
}
```

## 6. Backup ve Monitoring

- Firebase Console'da Firestore backups ayarlayabilirsiniz
- Cloud Functions ile otomatik raporlama kurabilirsiniz
- Firebase Analytics ile kullanım istatistikleri takip edebilirsiniz
