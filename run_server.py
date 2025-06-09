import subprocess
import sys
import os
import signal
import time
from multiprocessing import Process
import atexit

# Глобальные переменные для хранения процессов
django_process = None
telegram_bot_process = None
admin_bot_process = None

def get_python_path():
    """Получение пути к Python в виртуальном окружении"""
    if os.name == 'nt':  # Windows
        return os.path.join('venv', 'Scripts', 'python.exe')
    else:  # Linux/Mac
        return os.path.join('venv', 'bin', 'python')

def run_django():
    """Запуск Django сервера"""
    global django_process
    print("[INFO] Запуск Django сервера...")
    try:
        django_process = subprocess.Popen(
            [get_python_path(), 'manage.py', 'runserver'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        # Вывод логов Django сервера
        while True:
            output = django_process.stdout.readline()
            if output == '' and django_process.poll() is not None:
                break
            if output:
                print(f"[Django] {output.strip()}")
    except Exception as e:
        print(f"[ERROR] Ошибка запуска Django сервера: {e}")
        sys.exit(1)

def run_telegram_bot():
    """Запуск Telegram бота"""
    global telegram_bot_process
    print("[INFO] Запуск Telegram новостного бота...")
    try:
        telegram_bot_process = subprocess.Popen(
            [get_python_path(), 'manage.py', 'run_telegram_bot'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        # Вывод логов Telegram бота
        while True:
            output = telegram_bot_process.stdout.readline()
            if output == '' and telegram_bot_process.poll() is not None:
                break
            if output:
                print(f"[Telegram Bot] {output.strip()}")
    except Exception as e:
        print(f"[ERROR] Ошибка запуска Telegram бота: {e}")
        sys.exit(1)

def run_admin_bot():
    """Запуск админ-бота"""
    global admin_bot_process
    print("[INFO] Запуск админ-бота...")
    try:
        admin_bot_process = subprocess.Popen(
            [get_python_path(), '-m', 'futurelabsite.admin_bot'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        # Вывод логов админ-бота
        while True:
            output = admin_bot_process.stdout.readline()
            if output == '' and admin_bot_process.poll() is not None:
                break
            if output:
                print(f"[Admin Bot] {output.strip()}")
    except Exception as e:
        print(f"[ERROR] Ошибка запуска админ-бота: {e}")
        sys.exit(1)

def cleanup():
    """Очистка процессов при завершении"""
    print("\n[INFO] Завершение работы...")
    if django_process:
        django_process.terminate()
        django_process.wait()
    if telegram_bot_process:
        telegram_bot_process.terminate()
        telegram_bot_process.wait()
    if admin_bot_process:
        admin_bot_process.terminate()
        admin_bot_process.wait()
    print("[INFO] Все процессы остановлены")

def signal_handler(signum, frame):
    """Обработчик сигналов для корректного завершения"""
    print("\n[INFO] Получен сигнал завершения")
    cleanup()
    sys.exit(0)

if __name__ == '__main__':
    # Регистрация обработчиков для корректного завершения
    atexit.register(cleanup)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("[INFO] Старт проекта: Django + Telegram боты")
    
    # Проверка наличия виртуального окружения
    if not os.path.exists(get_python_path()):
        print("[ERROR] Виртуальное окружение не найдено. Создайте его с помощью:")
        print("python -m venv venv")
        print("source venv/bin/activate  # для Linux/Mac")
        print("venv\\Scripts\\activate  # для Windows")
        print("pip install -r requirements.txt")
        sys.exit(1)
    
    # Запускаем Django сервер в отдельном процессе
    django_proc = Process(target=run_django)
    django_proc.start()
    
    # Даем Django серверу время на запуск
    time.sleep(2)
    
    # Запускаем Telegram бота в отдельном процессе
    telegram_proc = Process(target=run_telegram_bot)
    telegram_proc.start()

    # Запускаем админ-бота в отдельном процессе
    admin_proc = Process(target=run_admin_bot)
    admin_proc.start()
    
    try:
        # Ждем завершения процессов
        django_proc.join()
        telegram_proc.join()
        admin_proc.join()
    except KeyboardInterrupt:
        print("\n[INFO] Получен сигнал прерывания")
        cleanup()
        sys.exit(0) 