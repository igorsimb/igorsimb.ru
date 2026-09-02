from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.db import OperationalError, ProgrammingError
from django.urls import reverse
from django.utils import translation

from blog.models import Post


class CanonicalSitemap(Sitemap):
    protocol = "https"


class CoreSitemap(CanonicalSitemap):
    changefreq = "monthly"

    view_names = (
        "core:main",
        "core:mp_monitor",
        "core:ez2task",
        "core:store_project",
    )

    def items(self):
        return [
            (language_code, view_name)
            for language_code, _language_name in settings.LANGUAGES
            for view_name in self.view_names
        ]

    def location(self, item):
        language_code, view_name = item
        with translation.override(language_code):
            return reverse(view_name)

    def priority(self, item):
        _language_code, view_name = item
        return 1.0 if view_name == "core:main" else 0.6


class BlogIndexSitemap(CanonicalSitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return ["blog:index"]

    def location(self, item):
        return reverse(item)


class BlogPostSitemap(CanonicalSitemap):
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        try:
            return list(
                Post.objects.filter(status=Post.Status.PUBLISHED).order_by("pk")
            )
        except (OperationalError, ProgrammingError):
            return []

    def location(self, post):
        return reverse("blog:detail", kwargs={"slug": post.slug})

    def lastmod(self, post):
        return post.updated_at
