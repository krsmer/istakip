import sqlite3
from datetime import datetime
import os

# Veritabanına bağlan
if os.path.exists('instance/calisanlar.db'):
    conn = sqlite3.connect('instance/calisanlar.db')
    cursor = conn.cursor()
    
    # Toplam kayıt sayısı
    cursor.execute('SELECT COUNT(*) FROM attendance')
    total = cursor.fetchone()[0]
    print(f"📈 Toplam kayıt sayısı: {total}")
    
    # Son 5 kayıt
    cursor.execute('SELECT * FROM attendance ORDER BY check_in_time DESC LIMIT 5')
    records = cursor.fetchall()
    
    if records:
        print(f"\n📊 Son 5 kayıt:")
        for i, record in enumerate(records, 1):
            print(f"  {i}. 👤 {record[1]} - {record[2]} - ID: {record[0]}")
    
    # Bugün Fatma'nın kaydı
    today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('SELECT * FROM attendance WHERE name = ? AND date(check_in_time) = ?', ('Fatma', today))
    fatma_today = cursor.fetchall()
    
    if fatma_today:
        print(f"\n✅ Fatma'nın bugünkü kaydı bulundu:")
        for record in fatma_today:
            print(f"   {record[1]} - {record[2]}")
    else:
        print(f"\n❌ Fatma'nın bugünkü kaydı bulunamadı")
    
    conn.close()
else:
    print("❌ Veritabanı dosyası bulunamadı")
