from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns

# URLs that should NOT be translated
urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),  # Language switch URL
    path("__debug__/", include("debug_toolbar.urls")),
    # Django admin
    path("admin/", admin.site.urls),
    path("store/", include("store.urls")),
    path("", include("store_users.urls")),
    # change {% if request.path == "/my/blog/" ... %} in blog/templates/puput/base.html and header.html
    path("my/", include("puput.urls")),

]

# URLs that should be translated
urlpatterns += i18n_patterns(
    # User management
    path("accounts/", include("allauth.urls")),
    # Local apps
    path("", include("core.urls")),
    prefix_default_language=True,
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "Админ-панель"
admin.site.index_title = "Администрирование сайта"
