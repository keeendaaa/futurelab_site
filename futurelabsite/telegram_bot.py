import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'futurelab_site.settings')
django.setup()

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from django.conf import settings
from .models import News, BotWhitelist
import requests
from io import BytesIO
from django.core.files import File
import re
import asyncio
from asgiref.sync import sync_to_async
from django.core.wsgi import get_wsgi_application
from django.utils import timezone

logger = logging.getLogger(__name__)

# Замените на ваш токен бота
TELEGRAM_BOT_TOKEN = '7260981978:AAH8z_hK4gtpvI4K71A-eQMkm6tRRitEsgM'
# ID администратора, который может публиковать новости
ADMIN_CHAT_ID = '1267841885'

# Инициализируем Django
application = get_wsgi_application()

class TelegramBot:
    def __init__(self):
        self.application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        self.setup_handlers()

    def setup_handlers(self):
        """Настройка обработчиков команд"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("list", self.list_news_command))
        self.application.add_handler(CommandHandler("delete", self.delete_news_command))
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
        self.application.add_handler(MessageHandler(filters.PHOTO & filters.CAPTION, self.handle_photo_message))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_message))

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        await update.message.reply_text(
            "Привет! Я бот для управления новостями на сайте.\n\n"
            "Доступные команды:\n"
            "/list - показать список последних новостей\n"
            "/delete - удалить новость\n\n"
            "Для публикации новости:\n"
            "1. Отправьте текст новости\n"
            "2. Или отправьте фото с подписью\n\n"
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

    @sync_to_async
    def get_latest_news(self, limit=5):
        """Получение последних новостей"""
        return list(News.objects.filter(is_active=True).order_by('-published_date')[:limit])

    @sync_to_async
    def delete_news(self, news_id):
        """Удаление новости"""
        try:
            news = News.objects.get(id=news_id)
            news.delete()
            return True
        except News.DoesNotExist:
            return False

    @sync_to_async
    def is_whitelisted(self, chat_id):
        return BotWhitelist.objects.filter(chat_id=str(chat_id)).exists()

    async def handle_photo_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик сообщений с фотографиями"""
        if not await self.is_whitelisted(update.effective_chat.id):
            await update.message.reply_text("Доступ запрещён. Обратитесь к администратору.")
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
        if not await self.is_whitelisted(update.effective_chat.id):
            await update.message.reply_text("Доступ запрещён. Обратитесь к администратору.")
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

    async def list_news_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /list"""
        if not await self.is_whitelisted(update.effective_chat.id):
            await update.message.reply_text("Доступ запрещён. Обратитесь к администратору.")
            return

        news_list = await self.get_latest_news()
        if not news_list:
            await update.message.reply_text("Нет доступных новостей.")
            return

        message = "Последние новости:\n\n"
        for news in news_list:
            message += f"ID: {news.id}\n"
            message += f"Заголовок: {news.emoji} {news.title}\n"
            message += f"Дата: {news.published_date.strftime('%d.%m.%Y %H:%M')}\n"
            message += f"Содержание: {news.content[:100]}...\n\n"

        await update.message.reply_text(message)

    async def delete_news_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /delete"""
        if not await self.is_whitelisted(update.effective_chat.id):
            await update.message.reply_text("Доступ запрещён. Обратитесь к администратору.")
            return

        news_list = await self.get_latest_news()
        if not news_list:
            await update.message.reply_text("Нет доступных новостей для удаления.")
            return

        keyboard = []
        for news in news_list:
            keyboard.append([
                InlineKeyboardButton(
                    f"{news.emoji} {news.title[:30]}...",
                    callback_data=f"delete_{news.id}"
                )
            ])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Выберите новость для удаления:",
            reply_markup=reply_markup
        )

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик callback-запросов от inline-кнопок"""
        query = update.callback_query
        await query.answer()

        if not await self.is_whitelisted(update.effective_chat.id):
            await query.edit_message_text("Извините, у вас нет прав для этого действия.")
            return

        if query.data.startswith("delete_"):
            news_id = int(query.data.split("_")[1])
            if await self.delete_news(news_id):
                await query.edit_message_text("Новость успешно удалена!")
            else:
                await query.edit_message_text("Ошибка при удалении новости.")

    def run(self):
        """Запуск бота"""
        print("[News Bot] Бот запущен и ожидает сообщения...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    try:
        print("[News Bot] Запуск новостного бота...")
        bot = TelegramBot()
        bot.run()
    except Exception as e:
        print(f"[News Bot] Ошибка при запуске бота: {e}")
        raise 