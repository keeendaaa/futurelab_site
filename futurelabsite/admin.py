from django.contrib import admin
from .models import Product, Characteristic, CharacteristicSection, ProductImage

# Register your models here.
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class CharacteristicInline(admin.TabularInline):
    model = Characteristic
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline, CharacteristicInline]
    list_display = ("name", "category")
    prepopulated_fields = {"slug": ("name",)}

@admin.register(CharacteristicSection)
class CharacteristicSectionAdmin(admin.ModelAdmin):
    list_display = ("name",)

@admin.register(Characteristic)
class CharacteristicAdmin(admin.ModelAdmin):
    list_display = ("product", "section", "name", "value")

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "image", "order")
