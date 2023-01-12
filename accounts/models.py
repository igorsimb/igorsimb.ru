from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth import get_user_model


class CustomUser(AbstractUser):
    pass


class Customer(models.Model):
    User = get_user_model()
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField("Имя", max_length=200, null=True, blank=True)
    email = models.EmailField(max_length=200, null=True)
    phone_number = models.CharField("Телефон", max_length=15, null=True, blank=True)
    address = models.CharField("Адрес", max_length=255, null=True, blank=True)
    city = models.CharField("Город", max_length=15, null=True, blank=True)
    zipcode = models.IntegerField("Индекс", null=True, blank=True)

    # USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f'{self.name}' if self.name else f'{self.user}'

    class Meta:
        verbose_name = "Покупатель"
        verbose_name_plural = "Покупатели"