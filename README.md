# Простая система лицензий

## Генерация ключей
Используйте админ-панель или команду:
```python
from core.license_manager import LicenseManager
print(LicenseManager.generate_license_key(30, 'days'))
```

## Файлы
- `app_data/license.key` — активированная лицензия
- Удалите `check_blacklist()` — нет удаленной проверки!

## Безопасность
Только локальная активация по ключу.