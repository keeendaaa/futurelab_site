from django.db import models

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
