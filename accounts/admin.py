from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from allauth.account.models import EmailAddress

from accounts.models import CustomUser


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['email', 'username', 'is_superuser']


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.unregister(EmailAddress)
