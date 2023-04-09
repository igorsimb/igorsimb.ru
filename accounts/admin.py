from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from allauth.account.models import EmailAddress

from accounts.models import CustomUser


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['email', 'username', 'is_superuser']

    # Don't show superuser to non-superusers
    def get_queryset(self, request):
        qs = super(UserAdmin, self).get_queryset(request)
        return qs if request.user.is_superuser else qs.filter(is_superuser=False)


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.unregister(EmailAddress)
