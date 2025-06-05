from django.core.management.base import BaseCommand
from futurelabsite.news_bot import NewsBot

class Command(BaseCommand):
    help = 'Запускает бота для сбора новостей'

    def handle(self, *args, **options):
        bot = NewsBot()
        bot.run()
        self.stdout.write(self.style.SUCCESS('Сбор новостей завершен')) 