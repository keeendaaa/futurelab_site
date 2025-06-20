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
    video = models.FileField("Видео", upload_to="product_videos/", null=True, blank=True)

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

class BotWhitelist(models.Model):
    chat_id = models.CharField(max_length=32, unique=True)
    first_name = models.CharField(max_length=255, blank=True, null=True, help_text="Имя пользователя (first_name)")
    last_name = models.CharField(max_length=255, blank=True, null=True, help_text="Фамилия пользователя (last_name)")
    username = models.CharField(max_length=255, blank=True, null=True, help_text="Имя пользователя (username)")
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.chat_id

class CharacteristicSection(models.Model):
    name = models.CharField("Название раздела", max_length=200)

    class Meta:
        verbose_name = "Раздел характеристик"
        verbose_name_plural = "Разделы характеристик"

    def __str__(self):
        return self.name

class Characteristic(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="characteristics", verbose_name="Продукт")
    section = models.ForeignKey(CharacteristicSection, on_delete=models.CASCADE, related_name="characteristics", verbose_name="Раздел")
    name = models.CharField("Название характеристики", max_length=200)
    value = models.CharField("Значение", max_length=500)

    class Meta:
        verbose_name = "Характеристика"
        verbose_name_plural = "Характеристики"

    def __str__(self):
        return f"{self.name}: {self.value}"

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images", verbose_name="Продукт")
    image = models.ImageField("Фото продукта", upload_to="product_gallery/")
    order = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        verbose_name = "Фото продукта"
        verbose_name_plural = "Галерея продукта"
        ordering = ["order", "id"]

    def __str__(self):
        return f"Фото для {self.product.name} #{self.id}"
