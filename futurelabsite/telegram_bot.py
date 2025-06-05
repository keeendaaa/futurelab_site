import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from django.conf import settings
from .models import News
import requests
from io import BytesIO
from django.core.files import File
import re
import asyncio
from asgiref.sync import sync_to_async
from django.core.wsgi import get_wsgi_application

logger = logging.getLogger(__name__)

# Замените на ваш токен бота
TELEGRAM_BOT_TOKEN = '7260981978:AAH8z_hK4gtpvI4K71A-eQMkm6tRRitEsgM'
# ID администратора, который может публиковать новости
ADMIN_CHAT_ID = '1267841885'

# Инициализируем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'futurelab_site.settings')
application = get_wsgi_application()

class TelegramBot:
    def __init__(self):
        self.application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        self.setup_handlers()

    def setup_handlers(self):
        """Настройка обработчиков команд"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(MessageHandler(filters.PHOTO & filters.CAPTION, self.handle_photo_message))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_message))

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        await update.message.reply_text(
            "Привет! Я бот для публикации новостей на сайте.\n\n"
            "Отправьте мне текст новости, и я опубликую его на сайте.\n"
            "Вы также можете отправить фото с подписью.\n\n"
            "Формат новости:\n"
            "1. Первая строка - заголовок (можно добавить эмодзи в начале)\n"
            "2. Остальной текст - содержание новости"
        )

    def extract_emoji(self, text):
        """Извлекает эмодзи из начала текста"""
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE)
        
        match = emoji_pattern.match(text)
        if match:
            return match.group(0)
        return "🚁"  # дефолтный эмодзи

    @sync_to_async
    def save_news(self, title, content, emoji, message_id, photo_bytes=None):
        """Синхронное сохранение новости"""
        news = News(
            title=title,
            content=content,
            emoji=emoji,
            telegram_message_id=str(message_id)
        )
        
        if photo_bytes:
            image_file = File(BytesIO(photo_bytes), name=f"news_{message_id}.jpg")
            news.image.save(f"news_{message_id}.jpg", image_file, save=False)
        
        news.save()
        return news

    async def handle_photo_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик сообщений с фотографиями"""
        if str(update.effective_chat.id) != ADMIN_CHAT_ID:
            await update.message.reply_text("Извините, у вас нет прав для публикации новостей.")
            return

        try:
            # Получаем фото
            photo = await update.message.photo[-1].get_file()
            photo_bytes = await photo.download_as_bytearray()
            
            # Разбираем текст
            caption = update.message.caption or ""
            lines = caption.split('\n', 1)
            title = lines[0].strip()
            content = lines[1].strip() if len(lines) > 1 else ""
            
            # Извлекаем эмодзи
            emoji = self.extract_emoji(title)
            title = title.replace(emoji, "").strip()
            
            # Сохраняем новость
            await self.save_news(title, content, emoji, update.message.message_id, photo_bytes)
            
            await update.message.reply_text("Новость успешно опубликована на сайте!")
            
        except Exception as e:
            logger.error(f"Ошибка при обработке фото: {str(e)}")
            await update.message.reply_text("Произошла ошибка при публикации новости.")

    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик текстовых сообщений"""
        if str(update.effective_chat.id) != ADMIN_CHAT_ID:
            await update.message.reply_text("Извините, у вас нет прав для публикации новостей.")
            return

        try:
            # Разбираем текст
            text = update.message.text
            lines = text.split('\n', 1)
            title = lines[0].strip()
            content = lines[1].strip() if len(lines) > 1 else ""
            
            # Извлекаем эмодзи
            emoji = self.extract_emoji(title)
            title = title.replace(emoji, "").strip()
            
            # Сохраняем новость
            await self.save_news(title, content, emoji, update.message.message_id)
            
            await update.message.reply_text("Новость успешно опубликована на сайте!")
            
        except Exception as e:
            logger.error(f"Ошибка при обработке текста: {str(e)}")
            await update.message.reply_text("Произошла ошибка при публикации новости.")

    def run(self):
        """Запуск бота"""
        self.application.run_polling() 