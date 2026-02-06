# core/api_client.py
"""Клиент для работы с Voice API"""

import requests
import time
from .config import Config

class VoiceAPIClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = Config.API_BASE_URL
    
    def _get_headers(self):
        return {"X-API-Key": self.api_key}
    
    def check_balance(self):
        """Проверить баланс"""
        try:
            response = requests.get(
                f"{self.base_url}/balance",
                headers=self._get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, response.json().get("detail", "Ошибка API")
        except Exception as e:
            return False, str(e)
    
    def get_templates(self):
        """Получить список шаблонов"""
        try:
            response = requests.get(
                f"{self.base_url}/templates",
                headers=self._get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, []
        except Exception as e:
            return False, []
    
    def create_task(self, text, template_uuid, chunk_size=None):
        """Создать задачу на озвучивание"""
        data = {
            "template_uuid": template_uuid,
            "text": text
        }
        
        if chunk_size:
            data["chunk_size"] = chunk_size
        
        try:
            response = requests.post(
                f"{self.base_url}/tasks",
                headers=self._get_headers(),
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, response.json().get("detail", "Ошибка создания задачи")
        except Exception as e:
            return False, str(e)
    
    def get_task_status(self, task_id):
        """Получить статус задачи"""
        try:
            response = requests.get(
                f"{self.base_url}/tasks/{task_id}/status",
                headers=self._get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, None
        except Exception as e:
            return False, None
    
    def get_task_result(self, task_id):
        """Получить результат задачи"""
        try:
            response = requests.get(
                f"{self.base_url}/tasks/{task_id}/result",
                headers=self._get_headers(),
                timeout=60
            )
            
            if response.status_code == 200:
                return True, response.content
            else:
                return False, None
        except Exception as e:
            return False, None
    
    def wait_for_task(self, task_id, max_attempts=300, callback=None):
        """Ждать выполнения задачи"""
        for attempt in range(max_attempts):
            time.sleep(1)
            
            success, status_data = self.get_task_status(task_id)
            
            if not success:
                continue
            
            status = status_data.get("status")
            
            if callback:
                callback(status, status_data, attempt + 1)
            
            if status == "ending":
                return True, "completed"
            elif status == "error":
                return False, "error"
        
        return False, "timeout"
