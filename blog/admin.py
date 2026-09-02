from django.contrib import admin

from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "status",
        "is_featured",
        "feature_priority",
        "published_at",
    ]
    list_display_links = ["title"]
    list_editable = ["is_featured", "feature_priority"]
    list_filter = ["status", "is_featured"]
    search_fields = ["title", "summary", "tags"]
    ordering = ["-published_at", "title"]
    fieldsets = [
        (
            None,
            {
                "fields": [
                    "title",
                    "slug",
                    "markdown_body",
                    "status",
                    "published_at",
                ]
            },
        ),
        (
            "Homepage and article presentation",
            {
                "fields": [
                    "is_featured",
                    "feature_priority",
                    "summary",
                    "tags",
                ]
            },
        ),
    ]
