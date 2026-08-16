from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views.generic import RedirectView

from core.views import robots_txt
from .sitemaps import BlogIndexSitemap, BlogPostSitemap, CoreSitemap


sitemaps = {
    "core": CoreSitemap,
    "blog": BlogIndexSitemap,
    "posts": BlogPostSitemap,
}

# URLs that should NOT be translated
urlpatterns = [
    path("robots.txt", robots_txt, name="robots_txt"),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("i18n/", include("django.conf.urls.i18n")),  # Language switch URL
    path("__debug__/", include("debug_toolbar.urls")),
    # Django admin
    path("admin/", admin.site.urls),
    path(
        "my/blog/",
        RedirectView.as_view(pattern_name="blog:index", permanent=True),
    ),
    path(
        "my/blog/<slug:slug>/",
        RedirectView.as_view(pattern_name="blog:detail", permanent=True),
    ),
    path(
        "read/blog/",
        RedirectView.as_view(pattern_name="blog:index", permanent=True),
    ),
    path(
        "read/blog/<slug:slug>/",
        RedirectView.as_view(pattern_name="blog:detail", permanent=True),
    ),
    path("blog/", include("blog.urls")),
    path("store/", include("store.urls")),
    path("", include("store_users.urls")),
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
