from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, session
from datetime import datetime, timedelta
import os
import csv
import io
from werkzeug.security import generate_password_hash, check_password_hash
import pytz
import math
from firebase_config import firebase_db

# Türkiye saat dilimi
TURKEY_TZ = pytz.timezone('Europe/Istanbul')

# İş yeri konum ayarları (GPS koordinatları)
WORK_LOCATION = {
    'latitude': 36.938609,    # Babanızın iş yerinin gerçek enlemi
    'longitude': 34.847155,   # Babanızın iş yerinin gerçek boylamı
    'radius': 150           # İzin verilen mesafe (metre) - iş yerinden 150m içinde
}

# Flask uygulamasını oluştur
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Türkiye saati için yardımcı fonksiyon
def get_turkey_time():
    return datetime.now(TURKEY_TZ)

def get_turkey_date():
    return get_turkey_time().date()

def get_turkey_time_only():
    return get_turkey_time().time()

# Çalışan bilgileri (Firebase'de ayrı collection olarak saklanabilir)
CALISANLAR = [
    {'id': 1, 'ad': 'Fatma', 'soyad': 'Yılmaz', 'telefon': '05551234567'},
    {'id': 2, 'ad': 'Mehmet', 'soyad': 'Kaya', 'telefon': '05551234568'},
    {'id': 3, 'ad': 'Ayşe', 'soyad': 'Demir', 'telefon': '05551234569'},
    {'id': 4, 'ad': 'Ali', 'soyad': 'Çelik', 'telefon': '05551234570'},
    {'id': 5, 'ad': 'Zeynep', 'soyad': 'Arslan', 'telefon': '05551234571'},
    {'id': 6, 'ad': 'Hasan', 'soyad': 'Korkmaz', 'telefon': '05551234572'},
    {'id': 7, 'ad': 'Elif', 'soyad': 'Özkan', 'telefon': '05551234573'}
]

def get_calisan_by_id(calisan_id):
    """ID'ye göre çalışan bilgisi getir"""
    for calisan in CALISANLAR:
        if calisan['id'] == calisan_id:
            return calisan
    return None

def get_calisan_by_name(name):
    """Ad'a göre çalışan bilgisi getir"""
    for calisan in CALISANLAR:
        if calisan['ad'] == name:
            return calisan
    return None

# Haversine formülü ile mesafe hesabı (km cinsinden)
def haversine(lat1, lon1, lat2, lon2):
    # Koordinatları radyan cinsine çevir
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formülü
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Dünya'nın yarıçapı (km)
    r = 6371
    
    # Mesafeyi km cinsinden döndür
    return c * r * 1000  # metre cinsine çevir

# Admin kullanıcı bilgileri
ADMIN_USERNAME = "Hilmi"
ADMIN_PASSWORD_HASH = generate_password_hash("admin123")

# Ana sayfa - Çalışan listesi
@app.route('/')
def index():
    return render_template('index.html', calisanlar=CALISANLAR)

# Çalışan detay sayfası
@app.route('/calisan/<int:calisan_id>')
def calisan_detay(calisan_id):
    calisan = get_calisan_by_id(calisan_id)
    if not calisan:
        flash("Çalışan bulunamadı!", "error")
        return redirect(url_for('index'))
    
    # Bugün çalışanın girişi var mı kontrol et
    bugun_giris_var = firebase_db.check_today_attendance(calisan['ad'])
    
    return render_template('calisan.html', 
                         calisan=calisan, 
                         bugun_giris_var=bugun_giris_var,
                         bugunun_tarihi=get_turkey_time().strftime('%d %B %Y %A'),
                         su_anki_saat=get_turkey_time().strftime('%H:%M:%S'))

# İşe geldi kaydı
@app.route('/ise_geldi', methods=['POST'])
def ise_geldi():
    calisan_id = request.form.get('calisan_id')
    user_lat = float(request.form.get('latitude', 0))
    user_lng = float(request.form.get('longitude', 0))
    
    calisan = get_calisan_by_id(int(calisan_id))
    
    if not calisan:
        return jsonify({"success": False, "message": "Çalışan bulunamadı!"})
    
    # GPS mesafe kontrolü
    mesafe = haversine(user_lat, user_lng, WORK_LOCATION['latitude'], WORK_LOCATION['longitude'])
    
    if mesafe > WORK_LOCATION['radius']:
        return jsonify({
            "success": False, 
            "message": f"İş yerine çok uzaksınız! (Mesafe: {mesafe:.0f}m) Maksimum {WORK_LOCATION['radius']}m mesafede olmalısınız."
        })
    
    # Bugün zaten giriş yapmış mı kontrol et
    if firebase_db.check_today_attendance(calisan['ad']):
        return jsonify({"success": False, "message": "Bu çalışan bugün zaten işe geldi kaydı yaptı!"})
    
    try:
        # Firebase'e kaydet
        turkey_time = get_turkey_time()
        if firebase_db.add_attendance(calisan['ad'], turkey_time, user_lat, user_lng):
            message = f"Merhaba {calisan['ad']}! İşe geldiniz kaydı yapıldı. Saat: {turkey_time.strftime('%H:%M:%S')}"
            return jsonify({"success": True, "message": message})
        else:
            return jsonify({"success": False, "message": "Kayıt sırasında hata oluştu!"})
            
    except Exception as e:
        print(f"Kayıt hatası: {e}")
        return jsonify({"success": False, "message": "Kayıt sırasında hata oluştu!"})

# Admin girişi
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session['admin_logged_in'] = True
            session['admin_username'] = username
            return redirect(url_for('admin_panel'))
        else:
            flash('Kullanıcı adı veya şifre yanlış!', 'error')
    
    return render_template('admin_login.html')

# Admin panel
@app.route('/admin/panel')
def admin_panel():
    if not session.get('admin_logged_in'):
        flash('Lütfen önce giriş yapın!', 'error')
        return redirect(url_for('admin'))
    
    # Firebase'den tüm kayıtları getir
    kayitlar = firebase_db.get_all_attendance()
    
    admin_username = session.get('admin_username', 'Admin')
    return render_template('admin_panel.html', kayitlar=kayitlar, admin_username=admin_username)

# Çalışan detaylı raporu
@app.route('/admin/calisan/<calisan_adi>')
def admin_calisan_detay(calisan_adi):
    if not session.get('admin_logged_in'):
        flash('Lütfen önce giriş yapın!', 'error')
        return redirect(url_for('admin'))
    
    # Çalışan bilgilerini bul
    calisan = get_calisan_by_name(calisan_adi)
    if not calisan:
        flash("Çalışan bulunamadı!", "error")
        return redirect(url_for('admin_panel'))
    
    # Firebase'den çalışanın kayıtlarını getir
    kayitlar = firebase_db.get_employee_attendance(calisan_adi)
    
    return render_template('admin_calisan_detay.html', 
                         calisan=calisan, 
                         kayitlar=kayitlar,
                         admin_username=session.get('admin_username', 'Admin'))

# Excel raporu indir
@app.route('/admin/excel')
def excel_raporu():
    if not session.get('admin_logged_in'):
        flash('Lütfen önce giriş yapın!', 'error')
        return redirect(url_for('admin'))
    
    # Firebase'den tüm kayıtları getir
    kayitlar = firebase_db.get_all_attendance()
    
    # CSV dosyası oluştur
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Başlık satırı
    writer.writerow(['Çalışan Adı', 'Tarih', 'Saat'])
    
    # Veri satırları
    for kayit in kayitlar:
        writer.writerow([kayit.get('name', ''), kayit.get('date', ''), kayit.get('time', '')])
    
    # CSV içeriğini BytesIO'ya dönüştür
    output.seek(0)
    csv_bytes = io.BytesIO()
    csv_bytes.write(output.getvalue().encode('utf-8-sig'))  # BOM ekle
    csv_bytes.seek(0)
    
    return send_file(
        csv_bytes,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'devam_takip_{datetime.now().strftime("%Y_%m_%d")}.csv'
    )

# Admin çıkışı
@app.route('/admin/logout')
def admin_logout():
    session.clear()
    flash('Başarıyla çıkış yaptınız!', 'success')
    return redirect(url_for('index'))

@app.route('/check_location', methods=['POST'])
def check_location():
    """Çalışanın konumunu kontrol eder"""
    try:
        data = request.get_json()
        user_lat = float(data['latitude'])
        user_lon = float(data['longitude'])
        
        # İş yeri koordinatları
        work_lat = WORK_LOCATION['latitude']
        work_lon = WORK_LOCATION['longitude']
        allowed_radius = WORK_LOCATION['radius']
        
        # Mesafe hesapla
        distance = haversine(work_lat, work_lon, user_lat, user_lon)
        
        if distance <= allowed_radius:
            return jsonify({
                'success': True,
                'message': f'Konum doğrulandı. İş yerine {distance:.0f} metre uzaklıktasınız.',
                'distance': round(distance)
            })
        else:
            return jsonify({
                'success': False,
                'message': f'İş yerine çok uzaksınız ({distance:.0f} metre). Lütfen iş yerine yaklaşın.',
                'distance': round(distance),
                'required_distance': allowed_radius
            })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Konum kontrolü başarısız. Lütfen GPS\'inizin açık olduğundan emin olun.',
            'error': str(e)
        })

# Vercel için gerekli keep-alive endpoint'leri
@app.route('/ping')
def ping():
    return jsonify({"status": "alive", "timestamp": datetime.now().isoformat()})

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "database": "firebase",
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🔥 Firebase + Vercel yapısı başlatılıyor...")
    
    # Firebase bağlantısını test et
    if firebase_db.db:
        print("✅ Firebase bağlantısı başarılı!")
    else:
        print("❌ Firebase bağlantısı başarısız!")
    
    # Local development
    app.run(debug=True, host='0.0.0.0', port=5000)

# Ana sayfa
@app.route('/')
def index():
    return render_template('index.html', calisanlar=CALISANLAR)

# Çalışan detay sayfası
@app.route('/calisan/<int:calisan_id>')
def calisan_detay(calisan_id):
    calisan = get_calisan_by_id(calisan_id)
    if not calisan:
        flash("Çalışan bulunamadı!", "error")
        return redirect(url_for('index'))
    
    return render_template('calisan.html', 
                         calisan=calisan, 
                         bugun_giris_var=False,  # Firebase olmadan false
                         bugunun_tarihi=get_turkey_time().strftime('%d %B %Y %A'),
                         su_anki_saat=get_turkey_time().strftime('%H:%M:%S'))

# Test endpoint
@app.route('/test')
def test():
    return jsonify({
        "status": "OK",
        "message": "Uygulama çalışıyor",
        "time": get_turkey_time().isoformat(),
        "firebase": "Disabled for testing"
    })

# Health check
@app.route('/health')
def health():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
