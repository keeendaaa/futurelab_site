import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'futurelab_site.settings')
django.setup()

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from asgiref.sync import sync_to_async
from futurelabsite.models import BotWhitelist

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


ADMIN_BOT_TOKEN = '7948591411:AAFJ-d46OoKX6azLW3TSVMlnqIVC4a5FXCk'
ADMIN_CHAT_ID = 1267841885  
class AdminBot:
    def __init__(self):
        logger.info("Инициализация админ-бота...")
        self.application = Application.builder().token(ADMIN_BOT_TOKEN).build()
        self.setup_handlers()
        logger.info("Админ-бот инициализирован")

    def setup_handlers(self):
        logger.info("Настройка обработчиков команд...")
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("request", self.request_access))
        self.application.add_handler(CommandHandler("whitelist", self.show_whitelist))
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))
        logger.info("Обработчики команд настроены")

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.info(f"Получена команда /start от пользователя {update.effective_user.id}")
        await update.message.reply_text(
            "Это админ-бот для управления доступом к сервису.\n"
            "Пользователи могут отправить /request для запроса доступа.\n"
            "Администратор может просматривать и управлять whitelist." )

    async def request_access(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        logger.info(f"Получен запрос доступа от пользователя {chat_id}")
        first_name = update.effective_user.first_name
        last_name = update.effective_user.last_name
        username = update.effective_user.username
        logger.info(f"Данные пользователя: first_name={first_name}, last_name={last_name}, username={username}")
        
        # Уведомить администратора о новом запросе
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"Запрос на доступ от пользователя {update.effective_user.full_name} (chat_id: {chat_id})",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("Одобрить", callback_data=f"approve_{chat_id}_{first_name}_{last_name}_{username}"),
                    InlineKeyboardButton("Отклонить", callback_data=f"deny_{chat_id}")
                ]
            ])
        )
        await update.message.reply_text("Ваш запрос отправлен администратору. Ожидайте решения.")

    @sync_to_async
    def add_to_whitelist(self, chat_id, first_name=None, last_name=None, username=None):
        logger.info(f"Добавление пользователя в whitelist: chat_id={chat_id}, first_name={first_name}, last_name={last_name}, username={username}")
        obj, created = BotWhitelist.objects.get_or_create(
            chat_id=str(chat_id),
            defaults={
                "first_name": first_name,
                "last_name": last_name,
                "username": username
            }
        )
        logger.info(f"Пользователь {'создан' if created else 'уже существует'} в whitelist")
        return obj

    @sync_to_async
    def remove_from_whitelist(self, chat_id):
        logger.info(f"Удаление пользователя из whitelist: chat_id={chat_id}")
        deleted, _ = BotWhitelist.objects.filter(chat_id=str(chat_id)).delete()
        logger.info(f"Удалено записей: {deleted}")
        return deleted

    @sync_to_async
    def get_whitelist(self):
        logger.info("Получение списка whitelist")
        whitelist = list(BotWhitelist.objects.all())
        logger.info(f"Найдено {len(whitelist)} пользователей в whitelist")
        return whitelist

    async def show_whitelist(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_chat.id
        logger.info(f"Получена команда /whitelist от пользователя {user_id}")
        logger.info(f"ADMIN_CHAT_ID: {ADMIN_CHAT_ID}, тип: {type(ADMIN_CHAT_ID)}")
        logger.info(f"user_id: {user_id}, тип: {type(user_id)}")
        
        if user_id != ADMIN_CHAT_ID:
            logger.warning(f"Попытка доступа к whitelist от неавторизованного пользователя {user_id}")
            await update.message.reply_text("Нет доступа.")
            return

        whitelist = await self.get_whitelist()
        if not whitelist:
            logger.info("Whitelist пуст")
            await update.message.reply_text("Whitelist пуст.")
            return

        msg = "Whitelist пользователей:\n"
        keyboard = []
        for user in whitelist:
            first_name = (user.first_name or "не задано")
            last_name = (user.last_name or "не задано")
            username = (user.username or "не задано")
            msg += f"chat_id: {user.chat_id}, имя: {first_name} {last_name}, username: {username}\n"
            keyboard.append([InlineKeyboardButton(f"Удалить {user.chat_id}", callback_data=f"remove_{user.chat_id}")])
        
        logger.info(f"Отправка списка whitelist пользователю {user_id}")
        await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        user_id = query.from_user.id
        logger.info(f"Получен callback от пользователя {user_id}: {query.data}")
        
        await query.answer()
        if user_id != ADMIN_CHAT_ID:
            logger.warning(f"Попытка обработки callback от неавторизованного пользователя {user_id}")
            await query.edit_message_text("Нет доступа.")
            return

        if query.data.startswith("approve_"):
            parts = query.data.split("_", 4)
            chat_id = parts[1]
            first_name = parts[2] if len(parts) > 2 else None
            last_name = parts[3] if len(parts) > 3 else None
            username = parts[4] if len(parts) > 4 else None
            logger.info(f"Одобрение доступа для пользователя {chat_id}")
            await self.add_to_whitelist(chat_id, first_name, last_name, username)
            await query.edit_message_text(f"Пользователь (chat_id: {chat_id}, имя: {first_name} {last_name}, username: {username}) добавлен в whitelist.")
        elif query.data.startswith("deny_"):
            chat_id = query.data.split("_", 1)[1]
            logger.info(f"Отклонение доступа для пользователя {chat_id}")
            await query.edit_message_text(f"Пользователь (chat_id: {chat_id}) отклонён.")
        elif query.data.startswith("remove_"):
            chat_id = query.data.split("_", 1)[1]
            logger.info(f"Удаление пользователя {chat_id} из whitelist")
            await self.remove_from_whitelist(chat_id)
            await query.edit_message_text(f"Пользователь (chat_id: {chat_id}) удалён из whitelist.")

    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.info(f"Получено текстовое сообщение от пользователя {update.effective_chat.id}")
        await update.message.reply_text("Используйте команды или кнопки для управления доступом.")

    def run(self):
        """Запуск бота"""
        logger.info("Запуск админ-бота...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    try:
        logger.info("Запуск админ-бота...")
        bot = AdminBot()
        bot.run()
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}", exc_info=True)
        raise 