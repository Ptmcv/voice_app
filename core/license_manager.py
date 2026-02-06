# core/license_manager.py
"""Система управления лицензиями с удаленной блокировкой"""

import os
import json
import hashlib
import base64
import requests
from datetime import datetime, timedelta
from cryptography.fernet import Fernet

class LicenseManager:
    """Управление лицензиями"""
    
    # Секретный ключ для шифрования (ДОЛЖЕН СОВПАДАТЬ С ГЕНЕРАТОРОМ!)
    SECRET_KEY = b'VoiceApp2026SecretKey_ChangeThis_12345'
    LICENSE_FILE = "license.dat"
    
    # URL для удаленной проверки (замените на свой GitHub!)
    REMOTE_BLACKLIST_URL = "https://raw.githubusercontent.com/YOUR_USERNAME/voice-app-licenses/main/blacklist.json"
    REMOTE_CHECK_ENABLED = False  # Пока отключено (поставьте True когда настроите GitHub)
    
    def __init__(self):
        # Генерируем Fernet ключ из секрета
        key = base64.urlsafe_b64encode(hashlib.sha256(self.SECRET_KEY).digest())
        self.cipher = Fernet(key)
    
    def check_license(self):
        """Проверить лицензию"""
        if not os.path.exists(self.LICENSE_FILE):
            return False, "Лицензия не найдена"
        
        try:
            with open(self.LICENSE_FILE, 'rb') as f:
                encrypted_data = f.read()
            
            # Расшифровываем
            decrypted_data = self.cipher.decrypt(encrypted_data)
            license_data = json.loads(decrypted_data.decode())
            
            # Проверяем срок действия
            expire_date = datetime.fromisoformat(license_data['expire_date'])
            
            if datetime.now() > expire_date:
                return False, "Лицензия истекла"
            
            # Проверяем удаленную блокировку
            if self.REMOTE_CHECK_ENABLED:
                is_blocked, block_reason = self.check_remote_blacklist(license_data['key'])
                if is_blocked:
                    return False, f"Лицензия заблокирована: {block_reason}"
            
            return True, license_data
        
        except Exception as e:
            return False, f"Ошибка проверки лицензии: {e}"
    
    def check_remote_blacklist(self, license_key):
        """Проверить ключ в удаленном blacklist"""
        try:
            response = requests.get(self.REMOTE_BLACKLIST_URL, timeout=3)
            
            if response.status_code == 200:
                blacklist = response.json()
                key_hash = hashlib.sha256(license_key.encode()).hexdigest()
                
                for blocked in blacklist.get('blocked_keys', []):
                    if blocked.get('key_hash') == key_hash:
                        return True, blocked.get('reason', 'Нарушение условий использования')
                
                return False, None
            
            return False, None
        
        except:
            return False, None
    
    def activate_license(self, license_key):
        """Активировать лицензию по ключу"""
        try:
            # Декодируем ключ
            decoded = base64.b64decode(license_key)
            key_data = json.loads(decoded.decode())
            
            # Проверяем подпись
            expected_signature = self._generate_signature(key_data)
            if key_data.get('signature') != expected_signature:
                return False, "Неверный ключ лицензии"
            
            # Проверяем удаленную блокировку
            if self.REMOTE_CHECK_ENABLED:
                is_blocked, block_reason = self.check_remote_blacklist(license_key)
                if is_blocked:
                    return False, f"Ключ заблокирован: {block_reason}"
            
            # Проверяем, не использован ли ключ
            used_keys_file = "used_keys.json"
            used_keys = []
            
            if os.path.exists(used_keys_file):
                with open(used_keys_file, 'r') as f:
                    used_keys = json.load(f)
            
            if license_key in used_keys:
                return False, "Ключ уже использован"
            
            # Получаем время из ключа (НОВЫЙ ФОРМАТ)
            time_value = key_data.get('time_value', key_data.get('days', 30))  # Совместимость
            time_unit = key_data.get('time_unit', 'days')
            
            # Вычисляем дату истечения
            if time_unit == 'minutes':
                expire_date = datetime.now() + timedelta(minutes=time_value)
            elif time_unit == 'hours':
                expire_date = datetime.now() + timedelta(hours=time_value)
            else:  # days
                expire_date = datetime.now() + timedelta(days=time_value)
            
            license_data = {
                'activated_date': datetime.now().isoformat(),
                'expire_date': expire_date.isoformat(),
                'time_value': time_value,
                'time_unit': time_unit,
                'key': license_key
            }
            
            # Шифруем и сохраняем
            encrypted_data = self.cipher.encrypt(json.dumps(license_data).encode())
            
            with open(self.LICENSE_FILE, 'wb') as f:
                f.write(encrypted_data)
            
            # Сохраняем использованный ключ
            used_keys.append(license_key)
            with open(used_keys_file, 'w') as f:
                json.dump(used_keys, f)
            
            return True, license_data
        
        except Exception as e:
            return False, f"Ошибка активации: {e}"
    
    def get_remaining_time(self):
        """Получить оставшееся время лицензии"""
        success, result = self.check_license()
        
        if not success:
            return None
        
        expire_date = datetime.fromisoformat(result['expire_date'])
        remaining = expire_date - datetime.now()
        
        days = remaining.days
        hours = remaining.seconds // 3600
        minutes = (remaining.seconds % 3600) // 60
        
        return {
            'days': days,
            'hours': hours,
            'minutes': minutes,
            'total_seconds': remaining.total_seconds()
        }
    
    def _generate_signature(self, key_data):
        """Генерировать подпись ключа"""
        # НОВЫЙ ФОРМАТ
        if 'time_value' in key_data:
            data_string = f"{key_data['time_value']}{key_data['time_unit']}{key_data['created']}"
        # СТАРЫЙ ФОРМАТ (совместимость)
        elif 'days' in key_data:
            data_string = f"{key_data['days']}{key_data['created']}"
        else:
            raise ValueError("Неизвестный формат ключа")
        
        signature = hashlib.sha256((data_string + self.SECRET_KEY.decode()).encode()).hexdigest()
        return signature
    
    @staticmethod
    def generate_license_key(time_value, time_unit='days'):
        """
        Генерировать лицензионный ключ
        time_unit: 'minutes', 'hours', 'days'
        """
        key_data = {
            'time_value': time_value,
            'time_unit': time_unit,
            'created': datetime.now().isoformat()
        }
        
        lm = LicenseManager()
        key_data['signature'] = lm._generate_signature(key_data)
        
        encoded = base64.b64encode(json.dumps(key_data).encode()).decode()
        
        return encoded
