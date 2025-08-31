import requests
import json
import os
import uuid

def get_firebase_remote_config():
    """Firebase Remote Config'ten güncel API ayarlarını al"""
    
    # Firebase bilgileri (RecTV uygulamasının gerçek değerleri)
    config = {
        'api_key': 'AIzaSyBbhpzG8Ecohu9yArfCO5tF13BQLhjLahc',
        'project_id': '791583031279',
        'app_id': '1:791583031279:android:8a641d9e7d1e2c8d',
        'package_name': 'com.rectv.shot'
    }
    
    # Dynamic device ID
    app_instance_id = str(uuid.uuid4()).replace('-', '')[:24]
    
    # Firebase Remote Config isteği
    url = f"https://firebaseremoteconfig.googleapis.com/v1/projects/{config['project_id']}/namespaces/firebase:fetch?key={config['api_key']}"
    
    headers = {
        'Content-Type': 'application/json',
        'X-Goog-Api-Key': config['api_key'],
        'X-Android-Package': config['package_name'],
        'X-Android-Cert': '6A:7D:CF:60:90:9A:2E:85:2A:9D:23:34:FA:2D:45:EE:9B:41:27:4C'
    }
    
    payload = {
        'appId': config['app_id'],
        'appInstanceId': app_instance_id,
        'appBuild': '81',
        'appVersion': '1.5.0',
        'languageCode': 'tr',
        'timeZone': 'Europe/Istanbul'
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        response_data = response.json()
        
        print(f"Firebase Status: {response_data.get('state', 'UNKNOWN')}")
        
        if response_data.get('state') == 'UPDATE' and 'entries' in response_data:
            entries = response_data['entries']
            print("✓ Firebase Remote Config başarılı!")
            
            # Önemli configleri logla
            important_keys = ['api_url', 'api_url_son', 'rectv_domain', 'api_secure_key']
            for key in important_keys:
                if key in entries:
                    print(f"📦 {key}: {entries[key]}")
            
            # API config için özel anahtar kontrol et
            api_config = {}
            
            # Öncelikle en güncel API URL'ini bul
            if 'api_url_son' in entries:
                api_config['mainUrl'] = entries['api_url_son'].rstrip('/')
            elif 'api_url' in entries:
                api_config['mainUrl'] = entries['api_url'].rstrip('/')
            elif 'rectv_domain' in entries:
                api_config['mainUrl'] = f"https://{entries['rectv_domain']}"
            
            # Diğer configler (RecTV.kta'dakilerle birleştir)
            api_config['userAgent'] = 'Dart/3.7 (dart:io)'
            api_config['referer'] = 'https://twitter.com/'
            
            # swKey için api_secure_key'i dene
            if 'api_secure_key' in entries:
                # API secure key'den swKey çıkarımı yap
                secure_key = entries['api_secure_key']
                if 'prectv' in secure_key:
                    domain_part = secure_key.split('//')[1].split('/')[0]
                    api_config['swKey'] = f"4F5A9C3D9A86FA54EACEDDD635185/{str(uuid.uuid4())}"
            
            print("✓ Firebase'den API config oluşturuldu")
            return api_config
            
        else:
            print("ℹ Firebase'de güncelleme yok veya template yok")
            return None
            
    except Exception as e:
        print(f"✗ Firebase Remote Config hatası: {e}")
        return None

def merge_configs(firebase_config, local_config):
    """Firebase ve local configleri birleştir"""
    if not firebase_config:
        return local_config
    
    # Firebase configi öncelikli, local fallback
    merged = local_config.copy()
    merged.update(firebase_config)
    
    return merged

if __name__ == "__main__":
    # Önce Firebase'den config al
    firebase_config = get_firebase_remote_config()
    
    # Local configi oku
    try:
        with open('api-config.json', 'r') as f:
            local_config = json.load(f)
    except:
        local_config = {
            'mainUrl': 'https://m.prectv55.lol',
            'swKey': '4F5A9C3D9A86FA54EACEDDD635185/64f9535b-bd2e-4483-b234-89060b1e631c',
            'userAgent': 'Dart/3.7 (dart:io)',
            'referer': 'https://twitter.com/'
        }
    
    # Configleri birleştir
    final_config = merge_configs(firebase_config, local_config)
    
    # Final configi kaydet
    with open('final-config.json', 'w') as f:
        json.dump(final_config, f, indent=2)
    
    print("✓ Final config oluşturuldu:")
    print(json.dumps(final_config, indent=2))
