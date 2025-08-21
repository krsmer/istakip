# Firebase yapılandırması
import os
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import json

class FirebaseDB:
    def __init__(self):
        self.db = None
        self.init_firebase()
    
    def init_firebase(self):
        """Firebase'i başlat"""
        try:
            # Firebase credentials JSON'dan oku (environment variable'dan)
            firebase_creds = os.environ.get('FIREBASE_CREDENTIALS')
            
            if firebase_creds:
                # Production (Vercel) - environment variable'dan
                try:
                    cred_dict = json.loads(firebase_creds)
                    cred = credentials.Certificate(cred_dict)
                except json.JSONDecodeError as json_error:
                    print(f"❌ Firebase credentials JSON parse hatası: {json_error}")
                    self.db = None
                    return
            else:
                # Local development - service account key dosyasından
                cred = credentials.Certificate('firebase-service-account.json')
            
            if not firebase_admin._apps:
                firebase_admin.initialize_app(cred)
            
            self.db = firestore.client()
            print("🔥 Firebase bağlantısı başarılı!")
            
        except Exception as e:
            print(f"❌ Firebase bağlantı hatası: {e}")
            import traceback
            traceback.print_exc()
            self.db = None
    
    def add_attendance(self, name, check_in_time=None):
        """Devam kaydı ekle"""
        if not self.db:
            return False
        
        try:
            if not check_in_time:
                check_in_time = datetime.now()
            
            doc_data = {
                'name': name,
                'check_in_time': check_in_time,
                'date': check_in_time.strftime('%Y-%m-%d'),
                'time': check_in_time.strftime('%H:%M:%S'),
                'timestamp': firestore.SERVER_TIMESTAMP
            }
            
            # Firestore'a kaydet
            doc_ref = self.db.collection('attendance').add(doc_data)
            print(f"✅ Firebase'e kayıt eklendi: {name} - {doc_ref[1].id}")
            return True
            
        except Exception as e:
            print(f"❌ Firebase kayıt hatası: {e}")
            return False
    
    def get_all_attendance(self):
        """Tüm devam kayıtlarını getir"""
        if not self.db:
            return []
        
        try:
            docs = self.db.collection('attendance').order_by('check_in_time', direction=firestore.Query.DESCENDING).stream()
            
            records = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                records.append(data)
            
            return records
            
        except Exception as e:
            print(f"❌ Firebase veri getirme hatası: {e}")
            return []
    
    def get_employee_attendance(self, name, date=None):
        """Belirli çalışanın devam kayıtlarını getir"""
        if not self.db:
            return []
        
        try:
            query = self.db.collection('attendance').where('name', '==', name)
            
            if date:
                query = query.where('date', '==', date)
            
            docs = query.order_by('check_in_time', direction=firestore.Query.DESCENDING).stream()
            
            records = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                records.append(data)
            
            return records
            
        except Exception as e:
            print(f"❌ Firebase çalışan veri getirme hatası: {e}")
            return []
    
    def check_today_attendance(self, name):
        """Bugün çalışanın girişi var mı kontrol et"""
        if not self.db:
            return False
        
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            docs = self.db.collection('attendance').where('name', '==', name).where('date', '==', today).limit(1).stream()
            
            return len(list(docs)) > 0
            
        except Exception as e:
            print(f"❌ Firebase bugünkü giriş kontrolü hatası: {e}")
            return False

# Global Firebase instance
firebase_db = FirebaseDB()
