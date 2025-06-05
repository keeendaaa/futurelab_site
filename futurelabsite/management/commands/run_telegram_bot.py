from django.core.management.base import BaseCommand
from futurelabsite.telegram_bot import TelegramBot

class Command(BaseCommand):
    help = 'Запускает Telegram бота'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Запуск Telegram бота...'))
        bot = TelegramBot()
        bot.run() 