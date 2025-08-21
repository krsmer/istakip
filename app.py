from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
import csv
import io
from werkzeug.security import generate_password_hash, check_password_hash
import pytz

# Türkiye saat dilimi
TURKEY_TZ = pytz.timezone('Europe/Istanbul')

# Flask uygulamasını oluştur
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Database yapılandırması - PostgreSQL öncelikli, SQLite fallback
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    # PostgreSQL (Render.com production)
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    print("🐘 PostgreSQL veritabanı kullanılıyor (Kalıcı veri)")
else:
    # SQLite (yerel geliştirme)
    import tempfile
    db_path = f'sqlite:///{tempfile.gettempdir()}/calisanlar.db'
    app.config['SQLALCHEMY_DATABASE_URI'] = db_path
    print("📁 SQLite veritabanı kullanılıyor (Yerel test)")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Veritabanı
db = SQLAlchemy(app)

# Çalışan Modeli
class Calisan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ad = db.Column(db.String(100), nullable=False)
    soyad = db.Column(db.String(100), nullable=False)
    telefon = db.Column(db.String(15), unique=True, nullable=False)
    
    def __repr__(self):
        return f'<Calisan {self.ad} {self.soyad}>'

# Türkiye saati için yardımcı fonksiyon
def get_turkey_time():
    return datetime.now(TURKEY_TZ)

def get_turkey_date():
    return get_turkey_time().date()

def get_turkey_time_only():
    return get_turkey_time().time()

# Otomatik temizlik fonksiyonu - 60 günden eski kayıtları sil
def temizle_eski_kayitlar():
    try:
        # Türkiye saatine göre 60 gün önceki tarihi hesapla
        altmis_gun_once = get_turkey_date() - timedelta(days=60)
        
        # 60 günden eski kayıtları bul
        eski_kayitlar = DevamKaydi.query.filter(DevamKaydi.tarih < altmis_gun_once).all()
        
        if eski_kayitlar:
            silinen_sayisi = len(eski_kayitlar)
            # Eski kayıtları sil
            for kayit in eski_kayitlar:
                db.session.delete(kayit)
            
            db.session.commit()
            print(f"✅ Otomatik temizlik: {silinen_sayisi} adet eski kayıt silindi (60 günden eski)")
        else:
            print("ℹ️  Otomatik temizlik: Silinecek eski kayıt bulunamadı")
            
    except Exception as e:
        print(f"❌ Otomatik temizlik hatası: {str(e)}")
        db.session.rollback()

# Devam Kaydı Modeli
class DevamKaydi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    calisan_id = db.Column(db.Integer, db.ForeignKey('calisan.id'), nullable=False)
    tarih = db.Column(db.Date, nullable=False, default=get_turkey_date)
    saat = db.Column(db.Time, nullable=False, default=get_turkey_time_only)
    
    # İlişki
    calisan = db.relationship('Calisan', backref=db.backref('devam_kayitlari', lazy=True))
    
    def __repr__(self):
        return f'<DevamKaydi {self.calisan.ad} {self.tarih} {self.saat}>'

# Ana sayfa - Çalışan listesi
@app.route('/')
def index():
    try:
        calisanlar = Calisan.query.all()
        return render_template('index.html', calisanlar=calisanlar)
    except Exception as e:
        print(f"Ana sayfa hatası: {e}")
        # Veritabanı sorunu varsa yeniden oluştur
        create_tables()
        calisanlar = Calisan.query.all()
        return render_template('index.html', calisanlar=calisanlar)

# Çalışan giriş sayfası
@app.route('/calisan/<int:id>')
def calisan_sayfasi(id):
    calisan = Calisan.query.get_or_404(id)
    return render_template('calisan.html', calisan=calisan)

# İşe geldi kaydı
@app.route('/ise_geldi/<int:id>', methods=['POST'])
def ise_geldi(id):
    calisan = Calisan.query.get_or_404(id)
    
    # Türkiye saatini kullan
    turkey_time = get_turkey_time()
    bugun = turkey_time.date()
    
    # Bugün zaten kayıt var mı kontrol et
    mevcut_kayit = DevamKaydi.query.filter_by(
        calisan_id=id, 
        tarih=bugun
    ).first()
    
    if mevcut_kayit:
        return jsonify({
            'success': False, 
            'message': f'{calisan.ad} {calisan.soyad}, bugün zaten iş yerine geldiğinizi kaydetmişsiniz!'
        })
    
    # Yeni kayıt oluştur (Türkiye saati ile)
    yeni_kayit = DevamKaydi(
        calisan_id=id,
        tarih=bugun,
        saat=turkey_time.time()
    )
    db.session.add(yeni_kayit)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Merhaba {calisan.ad} {calisan.soyad}! İş yerine geldiğiniz başarıyla kaydedildi. Kayıt saati: {yeni_kayit.saat.strftime("%H:%M")}'
    })

# Yönetici giriş sayfası
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        sifre = request.form.get('sifre', '').strip()
        print(f"POST isteği geldi. Girilen şifre: '{sifre}'")  # Debug için
        
        # Babanz için şifre: "yonetici123"
        if sifre == 'yonetici123':
            session['admin_logged_in'] = True
            print("Şifre doğru, session ayarlandı, yönlendiriliyor...")  # Debug
            flash('Başarıyla giriş yaptınız!', 'success')
            return redirect(url_for('yonetici'))
        else:
            print(f"Şifre yanlış: '{sifre}' != 'yonetici123'")  # Debug
            flash('Yanlış şifre! Tekrar deneyin.', 'danger')
    
    return render_template('admin_login.html')

# Yönetici çıkış
@app.route('/admin-logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Başarıyla çıkış yaptınız!', 'info')
    return redirect(url_for('index'))

# Yönetici paneli - şifre korumalı
@app.route('/yonetici')
def yonetici():
    # Giriş kontrolü
    if not session.get('admin_logged_in'):
        flash('Yönetici paneline erişim için giriş yapmalısınız!', 'warning')
        return redirect(url_for('admin_login'))
    
    # Son 100 kayıt (tüm çalışanlardan)
    kayitlar = db.session.query(DevamKaydi, Calisan).join(Calisan).order_by(DevamKaydi.tarih.desc(), DevamKaydi.saat.desc()).limit(100).all()
    
    # Çalışan listesi de gönder (detay için)
    calisanlar = Calisan.query.all()
    
    return render_template('yonetici.html', kayitlar=kayitlar, calisanlar=calisanlar)

# Çalışan detay sayfası - belirli bir çalışanın tüm kayıtları
@app.route('/calisan_detay/<int:calisan_id>')
def calisan_detay(calisan_id):
    # Giriş kontrolü
    if not session.get('admin_logged_in'):
        flash('Bu sayfaya erişim için yönetici girişi gerekli!', 'warning')
        return redirect(url_for('admin_login'))
    
    # Çalışan bilgileri
    calisan = Calisan.query.get_or_404(calisan_id)
    
    # Bu çalışanın tüm kayıtları (en yeniden eskiye)
    kayitlar = DevamKaydi.query.filter_by(calisan_id=calisan_id).order_by(DevamKaydi.tarih.desc(), DevamKaydi.saat.desc()).all()
    
    # İstatistikler hesapla
    toplam_gun = len(kayitlar)
    zamaninda = len([k for k in kayitlar if k.saat.hour <= 8])
    hafif_gec = len([k for k in kayitlar if 9 <= k.saat.hour <= 9])
    gec_kaldi = len([k for k in kayitlar if k.saat.hour >= 10])
    
    istatistikler = {
        'toplam_gun': toplam_gun,
        'zamaninda': zamaninda,
        'hafif_gec': hafif_gec,
        'gec_kaldi': gec_kaldi,
        'zamaninda_oran': round((zamaninda/toplam_gun*100) if toplam_gun > 0 else 0, 1),
        'gec_oran': round(((hafif_gec+gec_kaldi)/toplam_gun*100) if toplam_gun > 0 else 0, 1)
    }
    
    return render_template('calisan_detay.html', calisan=calisan, kayitlar=kayitlar, istatistikler=istatistikler)

# CSV rapor indir - şifre korumalı  
@app.route('/excel_indir')
def excel_indir():
    # Giriş kontrolü
    if not session.get('admin_logged_in'):
        flash('Rapor indirmek için yönetici girişi gerekli!', 'warning')
        return redirect(url_for('admin_login'))
    
    # Tüm kayıtları al
    kayitlar = db.session.query(
        Calisan.ad,
        Calisan.soyad, 
        DevamKaydi.tarih,
        DevamKaydi.saat
    ).join(DevamKaydi).order_by(DevamKaydi.tarih.desc()).all()
    
    # CSV formatında oluştur
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Başlık satırı
    writer.writerow(['Ad', 'Soyad', 'Tarih', 'Saat'])
    
    # Veri satırları
    for kayit in kayitlar:
        writer.writerow([
            kayit.ad, 
            kayit.soyad, 
            kayit.tarih.strftime('%d/%m/%Y'), 
            kayit.saat.strftime('%H:%M')
        ])
    
    # Response oluştur - Türkiye saati ile dosya adı
    turkey_now = get_turkey_time()
    response = app.response_class(
        output.getvalue(),
        mimetype='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename=devam_raporu_{turkey_now.strftime("%Y%m%d")}.csv'
        }
    )
    
    return response

# Manuel temizlik rotası - Yönetici için
@app.route('/temizlik', methods=['POST'])
def manuel_temizlik():
    # Giriş kontrolü
    if not session.get('admin_logged_in'):
        flash('Bu işlem için yönetici girişi gerekli!', 'warning')
        return redirect(url_for('admin_login'))
    
    try:
        # 60 günden eski kayıtları temizle
        altmis_gun_once = get_turkey_date() - timedelta(days=60)
        eski_kayitlar = DevamKaydi.query.filter(DevamKaydi.tarih < altmis_gun_once).all()
        
        if eski_kayitlar:
            silinen_sayisi = len(eski_kayitlar)
            for kayit in eski_kayitlar:
                db.session.delete(kayit)
            db.session.commit()
            flash(f'✅ {silinen_sayisi} adet eski kayıt (60 günden eski) başarıyla temizlendi!', 'success')
        else:
            flash('ℹ️ Temizlenecek eski kayıt bulunamadı.', 'info')
            
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Temizlik sırasında hata oluştu: {str(e)}', 'danger')
    
    return redirect(url_for('yonetici'))

# Veritabanını oluştur ve örnek veriler ekle
def create_tables():
    try:
        db.create_all()
        
        # Örnek çalışanlar ekle (sadece ilk çalıştırmada)
        if not Calisan.query.first():
            ornekler = [
                Calisan(ad='Ahmet', soyad='Yılmaz', telefon='05551234567'),
                Calisan(ad='Fatma', soyad='Demir', telefon='05551234568'),
                Calisan(ad='Mehmet', soyad='Kaya', telefon='05551234569'),
                Calisan(ad='Ayşe', soyad='Öztürk', telefon='05551234570'),
                Calisan(ad='Ali', soyad='Şahin', telefon='05551234571'),
                Calisan(ad='Zeynep', soyad='Çelik', telefon='05551234572'),
                Calisan(ad='Mustafa', soyad='Arslan', telefon='05551234573')
            ]
            
            for calisan in ornekler:
                db.session.add(calisan)
            
            db.session.commit()
            print("Veritabanı ve örnek veriler oluşturuldu!")
        
        # Uygulama başlangıcında otomatik temizlik yap
        temizle_eski_kayitlar()
        
    except Exception as e:
        print(f"Veritabanı oluşturma hatası: {e}")
        # Hata durumunda boş tablo oluştur
        db.create_all()

if __name__ == '__main__':
    with app.app_context():
        create_tables()
    # Production'da debug False olmalı ama sorun giderme için True
    debug_mode = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
