from django.db import models
from django.contrib.auth.models import User

class Size(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Размер")
    slug = models.SlugField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Размер'
        verbose_name_plural = 'Размеры'


class Material(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Материал")
    slug = models.SlugField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Материал'
        verbose_name_plural = 'Материалы'


class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(verbose_name="Описание", blank=True, null=True)
    slug = models.SlugField(max_length=200)

    current_price = models.DecimalField(max_digits=4, decimal_places=2, verbose_name='Текущая стоимость')
    discount_price = models.DecimalField(max_digits=4, decimal_places=2, default=0, verbose_name='Стоимость со скидкой')
    discount_percentage = models.IntegerField(default=0, verbose_name='Процент скидки')

    purchases_count = models.PositiveIntegerField(default=0, verbose_name='Количество покупок')

    size = models.ForeignKey(Size, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Размер")
    material = models.ForeignKey(Material, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Материал")

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"

    def __str__(self):
        return self.name

    def get_first_photo_url(self):
        if self.products_photo.exists():
            return self.products_photo.first().photo.url
        return '/static/images/placeholder.png'

    def get_actual_price(self):
        if self.discount_percentage > 0:
            return self.discount_price
        return self.current_price

class GalleryProducts(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='products_photo')
    photo = models.ImageField(upload_to='images/', verbose_name='Фотография')

class Comments(models.Model):
    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Товар'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    text = models.TextField(verbose_name='Текст комментария')
    created_date = models.DateField(auto_now_add=True, verbose_name='Дата создания')

    def __str__(self):
        return f'Комментарий от {self.user.username} на {self.product.name}'

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-created_date']

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo_user = models.ImageField(upload_to='photo/users/', blank=True, null=True,
                                   verbose_name='Аватарка пользователя')
    bio = models.TextField(blank=True, null=True, verbose_name='BIO пользователя')
    age = models.IntegerField(blank=True, null=True, verbose_name='Возраст')
    register_data = models.DateField(auto_now_add=True, verbose_name='Дата создания профиля')

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

class ContactMessage(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя")
    email = models.EmailField(verbose_name="Электронная почта")
    message = models.TextField(verbose_name="Сообщение")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата отправки")

    class Meta:
        verbose_name = 'Сообщение с формы'
        verbose_name_plural = 'Сообщения с формы'
        ordering = ['-created_at']

    def __str__(self):
        return f'Сообщение от {self.name} ({self.email})'


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Корзина пользователя {self.user.username}'

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.product.name} (в корзине {self.cart.user.username})'

    def get_total_price(self):
        price = self.product.discount_price if self.product.discount_price > 0 else self.product.current_price
        return price * self.quantity

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    full_name = models.CharField(max_length=100, verbose_name="Полное имя")
    email = models.EmailField(verbose_name="Электронная почта")
    shipping_address = models.CharField(max_length=255, verbose_name="Адрес доставки")
    phone_number = models.CharField(max_length=20, verbose_name="Номер телефона")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    paid = models.BooleanField(default=False, verbose_name="Оплачен")

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

    def __str__(self):
        return f'Заказ {self.pk} от {self.full_name}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.product.name} ({self.quantity})'