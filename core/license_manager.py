import os
import json
import hashlib
import secrets
from datetime import datetime, timedelta

USED_KEYS_FILE = "app_data/used_keys.json"
LICENSE_FILE = "app_data/license.key"

class LicenseManager:
    @staticmethod
    def generate_license_key(days):
        """Генерация для админки"""
        unique_id = secrets.token_hex(12)
        data_str = f'{unique_id}:{days}:{datetime.now().isoformat()}'
        signature = hashlib.sha256(data_str.encode()).hexdigest()[:8]
        return f'{unique_id}-{days}-{signature}'
    
    @staticmethod
    def activate_license(key):
        """Одноразовая активация"""
        try:
            parts = key.split('-')
            if len(parts) != 3:
                return False, 'Неверный формат'
            
            uid, days_str, sig = parts
            days = int(days_str)
            
            # Проверка подписи
            data_str = f'{uid}:{days}:{datetime.now().isoformat()[:10]}'
            expected_sig = hashlib.sha256(data_str.encode()).hexdigest()[:8]
            if sig != expected_sig:
                return False, 'Неверный ключ'
            
            # Проверка одноразовости
            used_keys = []
            if os.path.exists(USED_KEYS_FILE):
                with open(USED_KEYS_FILE, 'r') as f:
                    used_keys = json.load(f)
            
            key_hash = hashlib.sha256(key.encode()).hexdigest()
            if key_hash in used_keys:
                return False, 'Ключ уже использован'
            
            # Активация
            expire_date = datetime.now() + timedelta(days=days)
            license_data = {
                'key_hash': key_hash,
                'days': days,
                'activated': datetime.now().isoformat(),
                'expires': expire_date.isoformat()
            }
            
            os.makedirs('app_data', exist_ok=True)
            with open(LICENSE_FILE, 'w') as f:
                json.dump(license_data, f)
            
            # Помечаем использованным
            used_keys.append(key_hash)
            with open(USED_KEYS_FILE, 'w') as f:
                json.dump(used_keys, f)
            
            return True, f'Активировано на {days} дней'
        except:
            return False, 'Ошибка активации'
    
    @staticmethod
    def check_license():
        if not os.path.exists(LICENSE_FILE):
            return False, 'Не активировано'
        
        try:
            with open(LICENSE_FILE, 'r') as f:
                data = json.load(f)
            expires = datetime.fromisoformat(data['expires'])
            if datetime.now() > expires:
                return False, 'Истек'
            days_left = (expires - datetime.now()).days
            return True, f'{days_left}д'
        except:
            return False, 'Ошибка'