from django.shortcuts import render, redirect
import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import threading
from .models import Product, News, CharacteristicSection
from django.db.models import Q
from django.db.models.functions import Lower
from django.core import serializers
from django.template.loader import render_to_string

# Create your views here.

def index(request):
    products = Product.objects.all()
    latest_news = News.objects.filter(is_active=True).order_by('-published_date')[:3]  # Изменено с 2 на 3
    return render(request, 'index.html', {
        'products': products,
        'latest_news': latest_news,
    })

def about(request):
    return render(request, 'about.html')

def security(request):
    return render(request, 'security.html')

def industry(request):
    return render(request, 'industry.html')

def excursion(request):
    return render(request, 'excursion.html')

def education(request):
    return render(request, 'education.html')

TELEGRAM_TOKEN = '8154636602:AAELY7GSm_66sOk1CPPqIEXqBA-M1aNM9SU'
TELEGRAM_CHAT_ID = '1267841885'  

def send_telegram_message(data, url):
    try:
        requests.post(url, data=data, timeout=5)
    except Exception as e:
        print('TELEGRAM ERROR:', e)

@csrf_exempt
def send_telegram(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        message = request.POST.get('message')
        text = f"Новая заявка с сайта:\nИмя: {name}\nТелефон: {phone}\nСообщение: {message}"
        print('TELEGRAM SEND:', text)
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {'chat_id': TELEGRAM_CHAT_ID, 'text': text}
        threading.Thread(target=send_telegram_message, args=(data, url)).start()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)

def products_list(request):
    products = Product.objects.all()
    categories = [
        ("kanatohod", "Комплексы канатоход"),
        ("bas", "Многофункциональные БАС"),
        ("fpv", "FPV-Дроны"),
        ("cargo", "Грузовые дроны"),
        ("software", "Программное обеспечение"),
        ("champ", "Оборудование для чемпионатов"),
    ]
    products_by_category = []
    for cat_key, cat_verbose in categories:
        cat_products = [p for p in products if (p.category or "") == cat_key]
        products_by_category.append((cat_key, cat_verbose, cat_products))
    return render(request, 'products.html', {
        'products_by_category': products_by_category
    })

def search_products(request):
    query = request.GET.get('q', '').strip()
    products = []
    if query:
        products = Product.objects.filter(name__icontains=query)
        if products.count() == 1:
            return redirect('product_detail', slug=products.first().slug)
    return render(request, 'search_results.html', {'query': query, 'products': products})

def autocomplete_products(request):
    q = request.GET.get('q', '').strip().lower()
    results = []
    if q:
        words = q.split()
        products = Product.objects.all()
        filtered = []
        for p in products:
            name = (p.name or '').lower()
            desc = (p.description or '').lower()
            slug = (p.slug or '').lower()
            if all(any(word in field for field in [name, desc, slug]) for word in words):
                filtered.append(p)
        for p in filtered[:15]:
            results.append({
                'name': p.name,
                'url': f'/products/{p.slug}/',
                'id': p.id
            })
    return JsonResponse({'results': results})

def load_more_news(request):
    if request.method == 'GET' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        offset = int(request.GET.get('offset', 0))
        limit = 3
        news_qs = News.objects.filter(is_active=True).order_by('-published_date')[offset:offset+limit]
        html = render_to_string('news_cards.html', {'news_list': news_qs})
        return JsonResponse({'html': html, 'count': news_qs.count()})
    return JsonResponse({'error': 'Invalid request'}, status=400)

def product_detail(request, slug):
    product = Product.objects.get(slug=slug)
    sections = CharacteristicSection.objects.all()
    characteristics_by_section = []
    for section in sections:
        chars = product.characteristics.filter(section=section)
        if chars.exists():
            characteristics_by_section.append((section, chars))
    return render(request, 'product_detail.html', {
        'product': product,
        'characteristics_by_section': characteristics_by_section,
    })
