from django.db import models
from django.utils import timezone

# Create your models here.

class Product(models.Model):
    CATEGORY_CHOICES = [
        ("kanatohod", "Комплексы канатоход"),
        ("bas", "Многофункциональные БАС"),
        ("fpv", "FPV-Дроны"),
        ("cargo", "Грузовые дроны"),
        ("software", "Программное обеспечение"),
        ("champ", "Оборудование для чемпионатов"),
    ]
    name = models.CharField("Название", max_length=200)
    description = models.TextField("Описание")
    image = models.ImageField("Изображение", upload_to="products/")
    category = models.CharField("Категория", max_length=100, choices=CATEGORY_CHOICES, blank=True, null=True, help_text="Выберите категорию из списка")
    slug = models.SlugField("Слаг", unique=True)

    def __str__(self):
        return self.name

class News(models.Model):
    title = models.CharField("Заголовок", max_length=200)
    content = models.TextField("Содержание")
    image = models.ImageField("Изображение", upload_to="news/", null=True, blank=True)
    published_date = models.DateTimeField("Дата публикации", default=timezone.now)
    is_active = models.BooleanField("Активна", default=True)
    telegram_message_id = models.CharField("ID сообщения в Telegram", max_length=100, null=True, blank=True)
    emoji = models.CharField("Эмодзи", max_length=10, default="🚁")  # Эмодзи для заголовка

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"
        ordering = ['-published_date']

    def __str__(self):
        return self.title

    def get_time_ago(self):
        """Возвращает время в формате 'X д. назад'"""
        delta = timezone.now() - self.published_date
        days = delta.days
        if days == 0:
            return "Сегодня"
        elif days == 1:
            return "Вчера"
        else:
            return f"{days} д. назад"
