import textwrap

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django_quill.fields import QuillField
from accounts.models import Customer

STATUSES = (
    ('new', 'Новый'),
    ('in_progress', 'В работе'),
    ('in_delivery', 'Доставляется'),
    ('complete', 'Завершен'),
)


class Category(models.Model):
    name = models.CharField('Название', max_length=100, null=True, blank=True)
    image = models.ImageField("Изображение", null=True, blank=True)
    short_description = models.CharField('Краткое описание', max_length=140, help_text='Макс. длина: 140 символов. '
                                                                                       'Если не заполнено, то первые 140 символов Полного описания (без обрезания слов)',
                                         null=True, blank=True)
    long_description = models.TextField("Полное описание", null=True, blank=True)
    is_popular = models.BooleanField("Популярно", default=False,
                                     help_text="Будет отображаться в разделе 'Популярные категории' на главной "
                                               "странице")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("category", args=[str(self.id)])

    def save(self, *args, **kwargs):
        if not self.short_description:
            self.short_description = f'{textwrap.shorten(self.long_description, width=137, placeholder="...")}'
        super().save(*args, **kwargs)

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url


class Product(models.Model):
    name = models.CharField("Название", max_length=200, null=True)
    description = QuillField("Описание", null=True, blank=True, help_text=('Разрешено использование HTML-тэгов, напр. '
                                                                           '&#60;br>, &#60;strong>, &#60;i>, '
                                                                           '&#60;u>'))
    category = models.ManyToManyField(Category, verbose_name="категории")
    price = models.DecimalField("Цена", max_digits=7, decimal_places=2)
    image = models.ImageField("Главное Изображение", null=True, blank=True)
    active = models.BooleanField("Опубликовать", default=True,
                                 help_text="Только опубликованные товары будут отображены на сайте")
    is_popular = models.BooleanField("Популярно", default=False,
                                     help_text="Будет отображаться в разделе 'Популярные товары' на главной "
                                               "странице")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("product", args=[str(self.id)])

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"


# in view: image_list = product.images.all()
class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField('Доп. Изображения',
                              help_text="Будут отображены на странице описания товара")

    def __str__(self):
        return self.image.url

    class Meta:
        verbose_name = "Доп. Изображение"
        verbose_name_plural = "Доп. Изображения"


# cart
class Order(models.Model):
    id = models.BigAutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, verbose_name="Покупатель", blank=True, null=True)
    date_ordered = models.DateTimeField("Дата заказа", auto_now=True)
    status = models.CharField("Статус", max_length=12, choices=STATUSES, default='new')
    complete = models.BooleanField("Сделан", default=False, help_text="Кнопка 'Сделать заказ' была нажата")
    is_paid = models.BooleanField("Оплачен", default=False)

    def __str__(self):
        return str(self.id)

    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

    # Категория "Заказы" в админке
    get_cart_total.fget.short_description = 'Сумма (руб.)'

    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total

    @property
    def get_customer_email(self):
        if self.customer.email:
            return self.customer.email
        else:
            return "N/A"

    get_customer_email.fget.short_description = 'Электронная почта'

    @property
    def get_order_items(self):
        orderitems = self.orderitem_set.all()
        items = [f"{item.product} (x{item.quantity})" for item in orderitems]
        return items

    # Категория "Заказы" в админке
    get_order_items.fget.short_description = 'Товары'

    # we'll use it to check if items needs shipping or is digital only
    @property
    def shipping(self):
        shipping = True
        orderitems = self.orderitem_set.all()
        for _ in orderitems:
            shipping = True  # yes, there's an item in the cart that needs to be shipped (aka not-digital item)
        return shipping

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"


# items in the cart (so Cart can have many items)
class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name="Товар")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Заказ")
    quantity = models.IntegerField(default=0, null=True, blank=True, verbose_name="Количество")
    date_added = models.DateTimeField(auto_now_add=True, verbose_name="Дата")

    def __str__(self):
        return f'{self.product.name} (x{self.quantity})'

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total

    class Meta:
        verbose_name = "Заказанный Товар"
        verbose_name_plural = "Заказанные Товары"


class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Покупатель")
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Номер заказа")
    name = models.CharField("Имя", max_length=200, null=True, blank=True)
    phone_number = models.CharField("Телефон", max_length=15, null=True, blank=True)
    address = models.CharField("Адрес", max_length=200, null=True, blank=True)
    city = models.CharField("Город", max_length=200, null=True, blank=True)
    zipcode = models.CharField("Индекс", max_length=200, null=True, blank=True)
    date_added = models.DateTimeField("Дата", auto_now_add=True)

    def __str__(self):
        return str(self.customer)

    class Meta:
        verbose_name = "Адрес Доставки"
        verbose_name_plural = "Адреса Доставки"


class Carousel(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True,
                                 verbose_name="Категория",
                                 help_text="Возможна либо категория, либо товар")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True,
                                verbose_name="Товар",
                                help_text="Возможна либо категория, либо товар")
    banner = models.ImageField("Баннер", blank=True, null=True)
    title = models.CharField("Заголовок", max_length=100)
    description = models.CharField("Краткое описание (необязательно)", max_length=255, blank=True, null=True)
    is_enabled = models.BooleanField("Включено", default=True,
                                     help_text="Отображать ли на сайте")

    class Meta:
        verbose_name = "товар или категорию"
        verbose_name_plural = "Карусель"

    def get_absolute_url(self):
        if self.category is not None and self.product is None:
            return self.category.get_absolute_url()
        elif self.category is None and self.product is not None:
            return self.product.get_absolute_url()

    def __str__(self):
        if self.category is not None and self.product is None:
            return f"{self.category.name} (категория)"
        elif self.category is None and self.product is not None:
            return self.product.name
        else:
            return ""
