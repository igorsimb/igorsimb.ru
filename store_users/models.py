# # Custom User, register with email
# # https://www.fomfus.com/articles/how-to-use-email-as-username-for-django-authentication-removing-the-username/
#
# from django.contrib.auth.models import AbstractUser, BaseUserManager
# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from django.contrib.auth import get_user_model
#
#
# class UserManager(BaseUserManager):
#     """Define a model manager for User model with no username field."""
#
#     use_in_migrations = True
#
#     def _create_user(self, email, password, **extra_fields):
#         """Create and save a User with the given email and password."""
#         if not email:
#             raise ValueError('The given email must be set')
#         email = self.normalize_email(email)
#         user = self.model(email=email, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user
#
#     def create_user(self, email, password=None, **extra_fields):
#         """Create and save a regular User with the given email and password."""
#         extra_fields.setdefault('is_staff', False)
#         extra_fields.setdefault('is_superuser', False)
#         return self._create_user(email, password, **extra_fields)
#
#     def create_superuser(self, email, password, **extra_fields):
#         """Create and save a SuperUser with the given email and password."""
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)
#
#         if extra_fields.get('is_staff') is not True:
#             raise ValueError('Superuser must have is_staff=True.')
#         if extra_fields.get('is_superuser') is not True:
#             raise ValueError('Superuser must have is_superuser=True.')
#
#         return self._create_user(email, password, **extra_fields)
#
#
# class User(AbstractUser):
#     """User model."""
#
#     username = None
#     email = models.EmailField(_('Email'), unique=True)
#     name = models.CharField("Имя", max_length=255, null=True, blank=True,
#                             help_text="Может отличаться от имени в разделе 'Клиенты'")
#     phone_number = models.CharField("Телефон", max_length=15, null=True, blank=True)
#
#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = []
#
#     objects = UserManager()
#
#     def __str__(self):
#         return f'{self.name}' if self.name else f'{self.email}'
#
#
# class Customer(models.Model):
#     User = get_user_model()
#     user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
#     name = models.CharField("Имя", max_length=200, null=True, blank=True)
#     email = models.EmailField(max_length=200, null=True)
#     phone_number = models.CharField("Телефон", max_length=15, null=True, blank=True)
#     address = models.CharField("Адрес", max_length=255, null=True, blank=True)
#     city = models.CharField("Город", max_length=15, null=True, blank=True)
#     zipcode = models.IntegerField("Индекс", null=True, blank=True)
#
#     # USERNAME_FIELD = 'email'
#     # REQUIRED_FIELDS = ['username']
#
#     def __str__(self):
#         return f'{self.name}' if self.name else f'{self.user}'
#
#     class Meta:
#         verbose_name = "Покупатель"
#         verbose_name_plural = "Покупатели"
