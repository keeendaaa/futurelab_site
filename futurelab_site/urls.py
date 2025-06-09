"""
URL configuration for futurelab_site project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from futurelabsite import views
from django.conf import settings
from django.conf.urls.static import static
import os
from futurelabsite.views import send_telegram, products_list, load_more_news

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', views.index, name='index'),
    path('send_telegram/', send_telegram, name='send_telegram'),
    path('products/', products_list, name='products'),
    path('about/', views.about, name='about'),
    path('search/', views.search_products, name='search_products'),
    path('autocomplete_products/', views.autocomplete_products, name='autocomplete_products'),
    path('load_more_news/', load_more_news, name='load_more_news'),
    path('services/security/', views.security, name='security'),
    path('services/industry/', views.industry, name='industry'),
    path('services/excursion/', views.excursion, name='excursion'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=os.path.join(settings.BASE_DIR, 'futurelab/static'))
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
