from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
import pytz

# Türkiye saat dilimi
TURKEY_TZ = pytz.timezone('Europe/Istanbul')

# Flask uygulamasını oluştur
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Çalışan bilgileri
CALISANLAR = [
    {'id': 1, 'ad': 'Fatma', 'soyad': 'Yılmaz', 'telefon': '05551234567'},
    {'id': 2, 'ad': 'Mehmet', 'soyad': 'Kaya', 'telefon': '05551234568'},
    {'id': 3, 'ad': 'Ayşe', 'soyad': 'Demir', 'telefon': '05551234569'},
    {'id': 4, 'ad': 'Ali', 'soyad': 'Çelik', 'telefon': '05551234570'},
    {'id': 5, 'ad': 'Zeynep', 'soyad': 'Arslan', 'telefon': '05551234571'},
    {'id': 6, 'ad': 'Hasan', 'soyad': 'Korkmaz', 'telefon': '05551234572'},
    {'id': 7, 'ad': 'Elif', 'soyad': 'Özkan', 'telefon': '05551234573'}
]

def get_turkey_time():
    return datetime.now(TURKEY_TZ)

def get_calisan_by_id(calisan_id):
    for calisan in CALISANLAR:
        if calisan['id'] == calisan_id:
            return calisan
    return None

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
