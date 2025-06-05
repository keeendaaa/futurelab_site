# FutureLab Site

## Быстрый старт

1. **Создайте и активируйте виртуальное окружение:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Примените миграции:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
4. **Запустите сервер и ботов:**
   ```bash
   python run_server.py
   ```

## Рекомендации
- После изменения моделей всегда делайте миграции (`makemigrations` и `migrate`).
- Для фронтенда обновляйте страницу с очисткой кэша (Ctrl+F5).
- Проверяйте консоль браузера на наличие ошибок JS.
- Используйте git для контроля версий.
- Для тестов и линтеров см. разделы ниже (будут добавлены). 