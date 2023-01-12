from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),

    # User management
    path('accounts/', include('allauth.urls')),

    # Local apps
    path('', include('core.urls')),
    path('store/', include('store.urls')),

    # Third-party apps
    path('__debug__/', include('debug_toolbar.urls')),
] + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
)
