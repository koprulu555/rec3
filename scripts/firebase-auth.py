import json
import os
import firebase_admin
from firebase_admin import credentials, auth

def authenticate_firebase():
    """Firebase authentication yap"""
    try:
        # Firebase configini oku
        with open('firebase-config.json', 'r') as f:
            firebase_config = json.load(f)
        
        # Service account (GitHub Secrets'tan veya environment variable)
        service_account = os.getenv('FIREBASE_SERVICE_ACCOUNT')
        
        if service_account:
            cred = credentials.Certificate(json.loads(service_account))
            firebase_admin.initialize_app(cred, firebase_config)
            
            # Custom token oluştur
            uid = os.getenv('FIREBASE_UID', 'default-user')
            custom_token = auth.create_custom_token(uid)
            
            print("✓ Firebase authentication başarılı")
            return custom_token.decode('utf-8')
        else:
            print("ℹ Service account bulunamadı, devam ediliyor...")
            return None
            
    except Exception as e:
        print(f"✗ Firebase auth hatası: {e}")
        return None

if __name__ == "__main__":
    token = authenticate_firebase()
    if token:
        with open('firebase-token.txt', 'w') as f:
            f.write(token)
