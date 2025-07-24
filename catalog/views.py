# catalog/views.py
from django.shortcuts import render
from .models import Product
from django.core.paginator import Paginator
from django.db import models

def product_list(request):
    products = Product.objects.all()

    # Поиск
    query = request.GET.get('q')
    if query:
     products = products.filter(models.Q(name__icontains=query) | models.Q(description__icontains=query))
    
    # Сортировка
    sort = request.GET.get('sort')
    if sort in ['name', '-name', 'price', '-price', 'created_at', '-created_at']:
        products = products.order_by(sort)

    # Пагинация
    paginator = Paginator(products, 10)  # 10 товаров на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
        'sort': sort,
    }
    return render(request, 'catalog/product_list.html', context)