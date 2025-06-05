import subprocess
import sys
import os
from threading import Thread
import time

def run_django():
    """Запуск Django сервера"""
    subprocess.run([sys.executable, 'manage.py', 'runserver'])

def run_telegram_bot():
    """Запуск Telegram бота"""
    subprocess.run([sys.executable, 'manage.py', 'run_telegram_bot'])

if __name__ == '__main__':
    # Запускаем Django сервер в отдельном потоке
    django_thread = Thread(target=run_django)
    django_thread.daemon = True  # Поток завершится вместе с основной программой
    django_thread.start()
    
    # Даем Django серверу время на запуск
    time.sleep(2)
    
    # Запускаем Telegram бота в основном потоке
    run_telegram_bot() 