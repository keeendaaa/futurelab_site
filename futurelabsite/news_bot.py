import requests
from bs4 import BeautifulSoup
import feedparser
from datetime import datetime
import logging
from .models import News
from django.conf import settings
import os

logger = logging.getLogger(__name__)

class NewsBot:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def fetch_rss_news(self, rss_url):
        """Получение новостей из RSS-ленты"""
        try:
            feed = feedparser.parse(rss_url)
            for entry in feed.entries:
                # Проверяем, существует ли уже такая новость
                if not News.objects.filter(source_url=entry.link).exists():
                    news = News(
                        title=entry.title,
                        content=entry.description,
                        source=feed.feed.title,
                        source_url=entry.link,
                        published_date=datetime(*entry.published_parsed[:6])
                    )
                    news.save()
                    logger.info(f"Добавлена новость: {news.title}")
        except Exception as e:
            logger.error(f"Ошибка при получении RSS-новостей: {str(e)}")

    def fetch_web_news(self, url, title_selector, content_selector):
        """Получение новостей с веб-страницы"""
        try:
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            title = soup.select_one(title_selector).text.strip()
            content = soup.select_one(content_selector).text.strip()
            
            if not News.objects.filter(title=title).exists():
                news = News(
                    title=title,
                    content=content,
                    source=url,
                    source_url=url
                )
                news.save()
                logger.info(f"Добавлена новость: {news.title}")
        except Exception as e:
            logger.error(f"Ошибка при получении веб-новостей: {str(e)}")

    def run(self):
        """Запуск бота для всех источников"""
        # Пример RSS-лент
        rss_sources = [
            'https://example.com/rss',
            'https://another-site.com/feed'
        ]
        
        # Пример веб-страниц
        web_sources = [
            {
                'url': 'https://example.com/news',
                'title_selector': 'h1.title',
                'content_selector': 'div.content'
            }
        ]
        
        # Получаем новости из RSS
        for rss_url in rss_sources:
            self.fetch_rss_news(rss_url)
        
        # Получаем новости с веб-страниц
        for source in web_sources:
            self.fetch_web_news(
                source['url'],
                source['title_selector'],
                source['content_selector']
            ) 