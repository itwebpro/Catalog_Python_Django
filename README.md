# Сatalog_Python_Django
пример веб-приложения на Python + Django для каталога товаров с административной панелью и пользовательским интерфейсом

Задача: создать каталог товаров и админ панель на Python + Django. Админ панель: вход по паролю. Добавление, редактирование, удаление товаров. Форма для товаров: название, описание, цена, категория, фото товара (до 10 штук фото файлов). Пользовательная часть: вывод товаров по-странично, сортировка по дате добавления, названию, цене. Форма поиска по названию и описанию.


### 1. Создание проекта и приложения

```bash
django-admin startproject catalog_project
cd catalog_project
python manage.py startapp catalog
```

---

### 2. Настройка `settings.py`

Добавьте `catalog` в `INSTALLED_APPS`:

```python
# catalog_project/settings.py
INSTALLED_APPS = [
    # ...
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'catalog',  # ваше приложение
]
```

замените ALLOWED_HOSTS = [] на ALLOWED_HOSTS = ['127.0.0.1', 'localhost']


Настройте базу данных и медиа файлы:

```python
# catalog_project/settings.py
import os

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

---

### 3. Модели товаров

Создайте модель `Category` и `Product` в `catalog/models.py`:

```python
# catalog/models.py
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)
    # Для хранения нескольких фото, используем отдельную модель
    # или можно использовать JSONField (но лучше отдельная модель)
    
    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return f"{self.product.name} Image"
```

---

### 4. Миграции

```bash
python manage.py makemigrations
python manage.py migrate
```

---

### 5. Админка

Зарегистрируйте модели в `catalog/admin.py`:

```python
# catalog/admin.py
from django.contrib import admin
from .models import Category, Product, ProductImage

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'created_at')
    list_filter = ('category',)
    search_fields = ('name', 'description')
    inlines = [ProductImageInline]
```

---

### 6. URL конфигурация

Добавьте маршруты в `catalog_project/urls.py`:

```python
# catalog_project/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('catalog.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

Создайте `catalog/urls.py` для пользовательской части:

```python
# catalog/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
]
```

---

### 7. Представления и шаблоны

Создайте `views.py` для отображения товаров с пагинацией, сортировкой и поиском:

```python
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
```

Создайте шаблон `catalog/templates/catalog/product_list.html`:

```html
<!-- catalog/templates/catalog/product_list.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Каталог товаров</title>
</head>
<body>
    <h1>Каталог товаров</h1>

    <form method="get" action="">
        <input type="text" name="q" placeholder="Поиск..." value="{{ query }}">
        <button type="submit">Найти</button>
    </form>

    <p>Сортировать по:
        <a href="?sort=name">Названию</a> |
        <a href="?sort=-name">Названию (убыв.)</a> |
        <a href="?sort=price">Цене</a> |
        <a href="?sort=-price">Цене (убыв.)</a> |
        <a href="?sort=created_at">Дате добавления</a> |
        <a href="?sort=-created_at">Дате (убыв.)</a>
    </p>

    <ul>
        {% for product in page_obj.object_list %}
            <li>
                <h2>{{ product.name }}</h2>
                <p>{{ product.description }}</p>
                <p>Цена: {{ product.price }}</p>
                <p>Категория: {{ product.category.name }}</p>
                <p>Добавлено: {{ product.created_at }}</p>
                {% if product.images.all %}
                    {% for img in product.images.all|slice:":10" %}
                        <img src="{{ img.image.url }}" alt="{{ product.name }}" style="max-width:200px;">
                    {% endfor %}
                {% endif %}
            </li>
        {% endfor %}
    </ul>

    <div>
        {% if page_obj.has_previous %}
            <a href="?page={{ page_obj.previous_page_number }}{% if query %}&q={{ query }}{% endif %}{% if sort %}&sort={{ sort }}{% endif %}">Предыдущая</a>
        {% endif %}

        Страница {{ page_obj.number }} из {{ page_obj.paginator.num_pages }}

        {% if page_obj.has_next %}
            <a href="?page={{ page_obj.next_page_number }}{% if query %}&q={{ query }}{% endif %}{% if sort %}&sort={{ sort }}{% endif %}">Следующая</a>
        {% endif %}
    </div>
</body>
</html>
```

---

### 8. Создание суперпользователя и запуск

Создайте суперпользователя для входа в админку:

```bash
python manage.py createsuperuser
```

Запустите сервер:

```bash
python manage.py runserver
```

Перейдите по адресу `http://127.0.0.1:8000/admin/` и войдите под админом. Там вы можете добавлять, редактировать и удалять товары, категории и изображения.

Пользовательская часть доступна по `http://127.0.0.1:8000/` Админ часть доступна по `http://127.0.0.1:8000/admin/`


если первый раз используете django, нужно будет его сначала установить pip install django , также возможно дополнительно нужно будет установить python -m pip install Pillow

код полность рабочий можете сразу запускать python manage.py runserver  админ логин/пароль - admin admin
снимки экрана примера в папке - _screenshots
