from html import unescape

from django.db import models
from django.db.models import Case, F, IntegerField, Q, Value, When
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.text import Truncator

from .rendering import render_markdown


class PostQuerySet(models.QuerySet):
    def published(self):
        return self.filter(status=Post.Status.PUBLISHED)

    def featured(self):
        return self.published().filter(is_featured=True).order_by(
            "feature_priority", "-published_at", "pk"
        )

    def ordered_for_index(self):
        feature_priority = Case(
            When(is_featured=True, then=F("feature_priority")),
            default=Value(32767),
            output_field=IntegerField(),
        )
        return self.published().order_by(
            "-is_featured", feature_priority, "-published_at", "pk"
        )

    def for_homepage(self, limit=3):
        if limit <= 0:
            return []

        return list(self.featured()[:limit])

    def latest_for_homepage(self, limit=3):
        if limit <= 0:
            return []

        return list(
            self.published()
            .filter(is_featured=False)
            .order_by("-published_at", "pk")[:limit]
        )

    def next_after(self, post):
        if post.published_at is None:
            return None

        return (
            self.published()
            .filter(
                Q(published_at__lt=post.published_at)
                | Q(published_at=post.published_at, pk__gt=post.pk)
            )
            .order_by("-published_at", "pk")
            .first()
        )


class Post(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    markdown_body = models.TextField(blank=True)
    rendered_html = models.TextField(blank=True, editable=False)
    summary = models.TextField(blank=True)
    tags = models.CharField(max_length=255, blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT
    )
    is_featured = models.BooleanField(default=False)
    feature_priority = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)

    objects = PostQuerySet.as_manager()

    class Meta:
        ordering = ["-published_at", "-created_at"]

    def __str__(self) -> str:
        return self.title

    @property
    def is_published(self) -> bool:
        return self.status == self.Status.PUBLISHED

    @property
    def display_summary(self) -> str:
        if self.summary.strip():
            return self.summary.strip()

        plain_text = " ".join(unescape(strip_tags(self.rendered_html)).split())
        return Truncator(plain_text).words(32)

    @property
    def display_tags(self) -> list[str]:
        return [tag.strip() for tag in self.tags.split(",") if tag.strip()]

    def save(self, *args, **kwargs):
        self.rendered_html = render_markdown(self.markdown_body)

        if self.status == self.Status.PUBLISHED and self.published_at is None:
            self.published_at = timezone.now()
        elif self.status == self.Status.DRAFT:
            self.published_at = None

        super().save(*args, **kwargs)
