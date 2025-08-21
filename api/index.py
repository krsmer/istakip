from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd
import os
from werkzeug.security import generate_password_hash, check_password_hash

# Flask uygulamasını oluştur
app = Flask(__name__, template_folder='../templates')
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Vercel için database yolu
db_path = os.environ.get('DATABASE_URL', 'sqlite:////tmp/calisanlar.db')
app.config['SQLALCHEMY_DATABASE_URI'] = db_path
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

# Devam Kaydı Modeli
class DevamKaydi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    calisan_id = db.Column(db.Integer, db.ForeignKey('calisan.id'), nullable=False)
    tarih = db.Column(db.Date, nullable=False, default=datetime.now().date)
    saat = db.Column(db.Time, nullable=False, default=datetime.now().time)
    
    # İlişki
    calisan = db.relationship('Calisan', backref=db.backref('devam_kayitlari', lazy=True))
    
    def __repr__(self):
        return f'<DevamKaydi {self.calisan.ad} {self.tarih} {self.saat}>'

# Veritabanını oluştur ve örnek veriler ekle
def create_tables():
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

# Ana sayfa - Çalışan listesi
@app.route('/')
def index():
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
    
    # Bugün zaten kayıt var mı kontrol et
    bugun = datetime.now().date()
    mevcut_kayit = DevamKaydi.query.filter_by(
        calisan_id=id, 
        tarih=bugun
    ).first()
    
    if mevcut_kayit:
        return jsonify({
            'success': False, 
            'message': f'{calisan.ad} {calisan.soyad}, bugün zaten iş yerine geldiğinizi kaydetmişsiniz!'
        })
    
    # Yeni kayıt oluştur
    yeni_kayit = DevamKaydi(calisan_id=id)
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
        sifre = request.form.get('sifre', '')
        
        # Babanz için şifre: "yonetici123"
        if sifre == 'yonetici123':
            session['admin_logged_in'] = True
            flash('Başarıyla giriş yaptınız!', 'success')
            return redirect(url_for('yonetici'))
        else:
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
    
    # Son 30 günün kayıtları
    kayitlar = db.session.query(DevamKaydi, Calisan).join(Calisan).order_by(DevamKaydi.tarih.desc(), DevamKaydi.saat.desc()).limit(100).all()
    return render_template('yonetici.html', kayitlar=kayitlar)

# Excel rapor indir - şifre korumalı
@app.route('/excel_indir')
def excel_indir():
    # Giriş kontrolü
    if not session.get('admin_logged_in'):
        flash('Excel indirmek için yönetici girişi gerekli!', 'warning')
        return redirect(url_for('admin_login'))
    
    # Tüm kayıtları al
    kayitlar = db.session.query(
        Calisan.ad,
        Calisan.soyad, 
        DevamKaydi.tarih,
        DevamKaydi.saat
    ).join(DevamKaydi).order_by(DevamKaydi.tarih.desc()).all()
    
    # DataFrame oluştur
    df = pd.DataFrame(kayitlar, columns=['Ad', 'Soyad', 'Tarih', 'Saat'])
    
    # Excel dosyası oluştur
    excel_dosya = '/tmp/devam_raporu.xlsx'
    df.to_excel(excel_dosya, index=False)
    
    return send_file(excel_dosya, as_attachment=True, download_name=f'devam_raporu_{datetime.now().strftime("%Y%m%d")}.xlsx')

# Vercel için initialization
with app.app_context():
    create_tables()

# Vercel handler
def handler(event, context):
    return app

# Default export for Vercel
app = app
