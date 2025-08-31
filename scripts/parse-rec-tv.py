import requests
import re
import json
import os

def download_rec_tv_kt():
    """RecTV.kt dosyasını indir ve analiz et"""
    url = "https://raw.githubusercontent.com/nikyokki/nik-cloudstream/b46ee3286c3232ac1b40715e5db49bf090350586/RecTV/src/main/kotlin/com/keyiflerolsun/RecTV.kt"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        content = response.text
        print("✓ RecTV.kt başarıyla indirildi")
        
        # Firebase configini parse et
        firebase_config = {}
        
        # API anahtarlarını bul
        patterns = {
            'apiKey': r'apiKey\s*=\s*"([^"]+)"',
            'authDomain': r'authDomain\s*=\s*"([^"]+)"',
            'projectId': r'projectId\s*=\s*"([^"]+)"',
            'storageBucket': r'storageBucket\s*=\s*"([^"]+)"',
            'messagingSenderId': r'messagingSenderId\s*=\s*"([^"]+)"',
            'appId': r'appId\s*=\s*"([^"]+)"'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, content)
            if match:
                firebase_config[key] = match.group(1)
                print(f"✓ {key}: {match.group(1)}")
        
        # API endpoint'lerini bul
        api_patterns = {
            'mainUrl': r'override\s+var\s+mainUrl\s*=\s*"([^"]+)"',
            'swKey': r'private\s+(val|var)\s+swKey\s*=\s*"([^"]+)"',
            'userAgent': r'"user-agent"\s*to\s*"([^"]+)"',
            'referer': r'"Referer"\s*to\s*"([^"]+)"'
        }
        
        api_config = {}
        for key, pattern in api_patterns.items():
            match = re.search(pattern, content)
            if match:
                if key == 'swKey':
                    api_config[key] = match.group(2)
                else:
                    api_config[key] = match.group(1)
                print(f"✓ {key}: {api_config[key]}")
        
        # Configleri kaydet
        with open('firebase-config.json', 'w') as f:
            json.dump(firebase_config, f, indent=2)
        
        with open('api-config.json', 'w') as f:
            json.dump(api_config, f, indent=2)
            
        print("✓ Config dosyaları oluşturuldu")
        
    except Exception as e:
        print(f"✗ Hata: {e}")
        # Fallback config
        fallback_config = {
            'mainUrl': 'https://m.prectv55.lol',
            'swKey': '4F5A9C3D9A86FA54EACEDDD635185/64f9535b-bd2e-4483-b234-89060b1e631c',
            'userAgent': 'Dart/3.7 (dart:io)',
            'referer': 'https://twitter.com/'
        }
        with open('api-config.json', 'w') as f:
            json.dump(fallback_config, f, indent=2)
        print("✓ Fallback config oluşturuldu")

if __name__ == "__main__":
    download_rec_tv_kt()
