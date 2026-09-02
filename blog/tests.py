import json
import os
import shutil
import tempfile

from datetime import timedelta
from unittest.mock import patch

from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import OperationalError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from PIL.Image import DecompressionBombError

from .forms import RESERVED_SLUGS
from .models import Post
from .rendering import render_markdown

User = get_user_model()

PNG_IMAGE_BYTES = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00"
    b"\x1f\x15\xc4\x89\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00\x00\x03\x01\x01\x00\xc9\xfe"
    b"\x92\xef\x00\x00\x00\x00IEND\xaeB`\x82"
)


class FakeImage:
    def __init__(self, image_format):
        self.format = image_format

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def verify(self):
        return None


class PostModelTests(TestCase):
    def test_draft_post_clears_published_at(self):
        post = Post.objects.create(
            title="Draft post",
            slug="draft-post",
            markdown_body="Hello world",
            status=Post.Status.DRAFT,
            published_at=timezone.now(),
        )

        self.assertIsNone(post.published_at)
        self.assertEqual(post.rendered_html, "<p>Hello world</p>")

    def test_published_post_sets_published_at_once(self):
        post = Post.objects.create(
            title="Published post",
            slug="published-post",
            markdown_body="Hello world",
            status=Post.Status.PUBLISHED,
        )

        self.assertIsNotNone(post.published_at)
        first_published_at = post.published_at

        post.title = "Updated title"
        post.save()

        self.assertEqual(post.published_at, first_published_at)
        self.assertTrue(post.is_published)

    def test_explicit_summary_is_trimmed_and_preferred(self):
        post = Post.objects.create(
            title="Summarized post",
            slug="summarized-post",
            markdown_body="Markdown fallback",
            summary="  Editorial summary.  ",
        )

        self.assertEqual(post.display_summary, "Editorial summary.")

    def test_blank_summary_uses_plain_text_from_rendered_html(self):
        words = " ".join(f"word-{number}" for number in range(40))
        post = Post.objects.create(
            title="Generated summary",
            slug="generated-summary",
            markdown_body=f"# Heading & detail\n\n{words}",
        )

        self.assertIn("Heading & detail", post.display_summary)
        self.assertNotIn("<h1>", post.display_summary)
        self.assertNotIn("&amp;", post.display_summary)
        self.assertLess(len(post.display_summary.split()), 40)

    def test_display_tags_trims_values_and_omits_blanks(self):
        post = Post(tags=" Django, data engineering, ,AI ,")

        self.assertEqual(
            post.display_tags,
            ["Django", "data engineering", "AI"],
        )

    def test_blank_tags_have_no_display_values(self):
        self.assertEqual(Post(tags="  ").display_tags, [])


class PostQuerySetTests(TestCase):
    def create_published_post(
        self,
        title,
        published_at,
        *,
        is_featured=False,
        feature_priority=0,
    ):
        post = Post.objects.create(
            title=title,
            slug=title.lower().replace(" ", "-"),
            markdown_body=title,
            status=Post.Status.PUBLISHED,
            is_featured=is_featured,
            feature_priority=feature_priority,
        )
        Post.objects.filter(pk=post.pk).update(published_at=published_at)
        post.published_at = published_at
        return post

    def test_featured_posts_order_by_priority_then_publication_date(self):
        now = timezone.now()
        later_priority = self.create_published_post(
            "Later priority",
            now,
            is_featured=True,
            feature_priority=2,
        )
        older_first_priority = self.create_published_post(
            "Older first priority",
            now - timedelta(days=2),
            is_featured=True,
            feature_priority=1,
        )
        newer_first_priority = self.create_published_post(
            "Newer first priority",
            now - timedelta(days=1),
            is_featured=True,
            feature_priority=1,
        )

        self.assertEqual(
            list(Post.objects.featured()),
            [newer_first_priority, older_first_priority, later_priority],
        )

    def test_featured_priority_ties_use_primary_key_deterministically(self):
        published_at = timezone.now()
        first = self.create_published_post(
            "First tie",
            published_at,
            is_featured=True,
            feature_priority=1,
        )
        second = self.create_published_post(
            "Second tie",
            published_at,
            is_featured=True,
            feature_priority=1,
        )

        self.assertEqual(list(Post.objects.featured()), [first, second])

    def test_homepage_uses_only_explicitly_featured_posts(self):
        now = timezone.now()
        featured = self.create_published_post(
            "Featured",
            now - timedelta(days=3),
            is_featured=True,
            feature_priority=1,
        )
        newest = self.create_published_post("Newest", now)
        second_newest = self.create_published_post(
            "Second newest", now - timedelta(days=1)
        )
        older = self.create_published_post("Older", now - timedelta(days=2))

        self.assertEqual(Post.objects.for_homepage(), [featured])
        self.assertEqual(
            Post.objects.latest_for_homepage(),
            [newest, second_newest, older],
        )

    def test_latest_homepage_posts_exclude_displayed_featured_posts(self):
        now = timezone.now()
        first_featured = self.create_published_post(
            "First featured",
            now - timedelta(days=2),
            is_featured=True,
            feature_priority=1,
        )
        second_featured = self.create_published_post(
            "Second featured",
            now - timedelta(days=3),
            is_featured=True,
            feature_priority=2,
        )
        recent = self.create_published_post("Recent", now)
        older = self.create_published_post("Older", now - timedelta(days=4))

        self.assertEqual(
            Post.objects.latest_for_homepage(),
            [recent, older],
        )

    def test_homepage_has_no_featured_posts_when_nothing_is_selected(self):
        now = timezone.now()
        self.create_published_post("Newest", now)

        self.assertEqual(Post.objects.for_homepage(), [])

    def test_homepage_uses_only_three_featured_posts(self):
        published_at = timezone.now()
        posts = [
            self.create_published_post(
                f"Featured {priority}",
                published_at,
                is_featured=True,
                feature_priority=priority,
            )
            for priority in range(1, 5)
        ]

        self.assertEqual(Post.objects.for_homepage(), posts[:3])

    def test_homepage_excludes_drafts_even_when_featured(self):
        draft = Post.objects.create(
            title="Featured draft",
            slug="featured-draft",
            markdown_body="Hidden",
            status=Post.Status.DRAFT,
            is_featured=True,
            feature_priority=0,
        )

        self.assertNotIn(draft, Post.objects.for_homepage())

    def test_index_pins_featured_posts_without_duplicates(self):
        now = timezone.now()
        recent = self.create_published_post("Recent", now)
        featured = self.create_published_post(
            "Featured",
            now - timedelta(days=1),
            is_featured=True,
            feature_priority=1,
        )
        older = self.create_published_post("Older", now - timedelta(days=2))

        self.assertEqual(
            list(Post.objects.ordered_for_index()),
            [featured, recent, older],
        )

    def test_next_post_follows_publication_order(self):
        now = timezone.now()
        newest = self.create_published_post("Newest", now)
        next_post = self.create_published_post("Next", now - timedelta(days=1))
        self.create_published_post("Oldest", now - timedelta(days=2))

        self.assertEqual(Post.objects.next_after(newest), next_post)


class PostAdminTests(TestCase):
    def test_post_admin_exposes_feature_controls(self):
        post_admin = admin.site._registry[Post]

        self.assertEqual(
            post_admin.list_display,
            [
                "title",
                "status",
                "is_featured",
                "feature_priority",
                "published_at",
            ],
        )
        self.assertEqual(
            post_admin.list_editable,
            ["is_featured", "feature_priority"],
        )
        self.assertIn("summary", post_admin.get_fields(request=None))
        self.assertIn("tags", post_admin.get_fields(request=None))


class MarkdownRenderingTests(TestCase):
    def test_render_markdown_supports_common_elements(self):
        html = render_markdown("# Heading\n\nA [link](https://example.com) and `code`.")

        self.assertIn("<h2>Heading</h2>", html)
        self.assertNotIn("<h1>", html)
        self.assertIn('<a href="https://example.com">link</a>', html)
        self.assertIn("<code>code</code>", html)

    def test_render_markdown_sanitizes_raw_html(self):
        html = render_markdown("Before<script>alert('xss')</script><b>after</b>")

        self.assertNotIn("<script>", html)
        self.assertIn("&lt;script&gt;", html)
        self.assertIn("&lt;b&gt;after&lt;/b&gt;", html)

    def test_render_markdown_supports_fenced_code_blocks(self):
        html = render_markdown("```python\nprint('hello')\n```")

        self.assertIn('class="codehilite"', html)
        self.assertIn("print", html)
        self.assertIn("<span", html)

    def test_render_markdown_keeps_markdown_images(self):
        html = render_markdown("![Preview image](/media/blog/images/example.png)")

        self.assertIn(
            '<img alt="Preview image" src="/media/blog/images/example.png">', html
        )

    def test_render_markdown_keeps_table_structure(self):
        html = render_markdown("| Name | Value |\n| --- | --- |\n| Rows | 10M |")

        self.assertIn("<table>", html)
        self.assertIn("<thead>", html)
        self.assertIn("<tbody>", html)
        self.assertIn("<th>Name</th>", html)
        self.assertIn("<td>10M</td>", html)


class BlogPublicViewTests(TestCase):
    def setUp(self):
        self.published_post = Post.objects.create(
            title="Published post",
            slug="published-post",
            markdown_body="# Published\n\nVisible body.",
            status=Post.Status.PUBLISHED,
        )
        self.draft_post = Post.objects.create(
            title="Draft post",
            slug="draft-post",
            markdown_body="# Draft\n\nHidden body.",
            status=Post.Status.DRAFT,
        )

    def test_index_shows_only_published_posts(self):
        response = self.client.get(reverse("blog:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.published_post.title)
        self.assertNotContains(response, self.draft_post.title)

    def test_index_renders_one_ordered_ledger_with_featured_marker_once(self):
        featured_post = Post.objects.create(
            title="Featured post",
            slug="featured-post",
            markdown_body="Featured body.",
            status=Post.Status.PUBLISHED,
            is_featured=True,
            feature_priority=1,
        )
        recent_post = Post.objects.create(
            title="Recent post",
            slug="recent-post",
            markdown_body="Recent body.",
            status=Post.Status.PUBLISHED,
        )

        response = self.client.get(reverse("blog:index"))
        document = BeautifulSoup(response.content, "html.parser")
        ledgers = document.select("[data-article-ledger]")
        rows = document.select('[data-article-ledger] > a[href^="/blog/"]')

        self.assertEqual(len(ledgers), 1)
        self.assertEqual(
            [row.select_one("h3").get_text(strip=True) for row in rows],
            [featured_post.title, recent_post.title, self.published_post.title],
        )
        self.assertEqual(len(document.select("[data-featured-marker]")), 1)
        self.assertEqual(len({row["href"] for row in rows}), 3)

    def test_index_uses_summary_and_omits_blank_tag_group(self):
        self.published_post.summary = "Editorial summary."
        self.published_post.tags = ""
        self.published_post.save()

        tagged_post = Post.objects.create(
            title="Tagged post",
            slug="tagged-post",
            markdown_body="Tagged body.",
            summary="Tagged summary.",
            tags="Django, Data",
            status=Post.Status.PUBLISHED,
        )

        response = self.client.get(reverse("blog:index"))
        document = BeautifulSoup(response.content, "html.parser")
        untagged_row = document.select_one('a[href="/blog/published-post/"]')
        tagged_row = document.select_one('a[href="/blog/tagged-post/"]')

        self.assertIn("Editorial summary.", untagged_row.get_text(" ", strip=True))
        self.assertIsNone(untagged_row.select_one("[data-article-tags]"))
        self.assertEqual(
            [tag.get_text(strip=True) for tag in tagged_row.select("[data-article-tags] span")],
            ["Django", "Data"],
        )

    def test_index_marks_article_data_as_english_and_wrap_safe(self):
        self.published_post.title = "T" * 200
        self.published_post.summary = "English summary"
        self.published_post.tags = "G" * 255
        self.published_post.save()
        self.client.cookies[settings.LANGUAGE_COOKIE_NAME] = "ru"

        response = self.client.get(reverse("blog:index"))
        document = BeautifulSoup(response.content, "html.parser")
        row = document.select_one(f'a[href="/blog/{self.published_post.slug}/"]')

        for element in (row.select_one("h3"), row.select_one("p"), row.select_one(".article-tag")):
            self.assertEqual(element["lang"], "en")
        self.assertIn("article-data-text", row.select_one("h3")["class"])
        self.assertIn("article-data-text", row.select_one("p")["class"])
        self.assertIn("article-tag", row.select_one(".article-tag")["class"])

    def test_index_empty_state_keeps_single_ledger(self):
        Post.objects.filter(status=Post.Status.PUBLISHED).delete()

        response = self.client.get(reverse("blog:index"))
        document = BeautifulSoup(response.content, "html.parser")

        self.assertEqual(len(document.select("[data-article-ledger]")), 1)
        self.assertEqual(len(document.select("[data-blog-empty]")), 1)
        self.assertContains(response, "No published posts yet")
        self.assertContains(response, "Technical notes and field reports will appear here once published.")

    def test_index_author_tools_are_superuser_only(self):
        superuser = User.objects.create_superuser(
            username="author",
            email="author@example.com",
            password="password123",
        )

        anonymous_response = self.client.get(reverse("blog:index"))
        self.client.force_login(superuser)
        author_response = self.client.get(reverse("blog:index"))

        self.assertNotContains(anonymous_response, reverse("blog:editor_create"))
        self.assertContains(author_response, reverse("blog:editor_create"))
        self.assertContains(author_response, reverse("blog:dashboard"))

    def test_index_preserves_canonical_url(self):
        response = self.client.get(reverse("blog:index"))
        document = BeautifulSoup(response.content, "html.parser")

        self.assertEqual(
            document.find("link", rel="canonical")["href"],
            "https://igorsimb.ru/blog/",
        )

    def test_index_has_one_page_heading_and_russian_interface_copy(self):
        self.client.cookies[settings.LANGUAGE_COOKIE_NAME] = "ru"

        response = self.client.get(reverse("blog:index"))
        document = BeautifulSoup(response.content, "html.parser")

        self.assertEqual(document.html["lang"], "ru")
        self.assertEqual(len(document.find_all("h1")), 1)
        self.assertContains(response, "Технические заметки")
        self.assertContains(response, "Избранное и новое")

    def test_detail_shows_published_post(self):
        response = self.client.get(
            reverse("blog:detail", kwargs={"slug": self.published_post.slug})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.published_post.title)
        self.assertContains(response, "Visible body")

    def test_detail_renders_article_structure_and_optional_metadata_once(self):
        self.published_post.summary = "  Editorial summary copy.  "
        self.published_post.tags = "Django, Data"
        self.published_post.save()

        response = self.client.get(
            reverse("blog:detail", kwargs={"slug": self.published_post.slug})
        )
        document = BeautifulSoup(response.content, "html.parser")

        self.assertEqual(len(document.select("[data-article-detail]")), 1)
        self.assertEqual(len(document.select("[data-article-metadata]")), 1)
        metadata_tags = document.select("[data-article-metadata] span")
        self.assertEqual(
            [tag.get_text(strip=True) for tag in metadata_tags if tag.get_text(strip=True)],
            ["Django", "Data"],
        )
        self.assertEqual(
            document.select_one("[data-article-summary]").get_text(" ", strip=True),
            "Editorial summary copy.",
        )
        self.assertNotContains(response, "TL;DR")

    def test_detail_blank_summary_omits_highlighted_summary(self):
        self.published_post.summary = "   "
        self.published_post.save()

        response = self.client.get(
            reverse("blog:detail", kwargs={"slug": self.published_post.slug})
        )
        document = BeautifulSoup(response.content, "html.parser")

        self.assertIsNone(document.select_one("[data-article-summary]"))
        self.assertNotContains(response, "TL;DR")

    def test_detail_keeps_supported_markdown_inside_article_body(self):
        self.published_post.markdown_body = """## Section

A [safe link](https://example.com) with `inline_code`.

- One
- Two

1. First
2. Second

```python
print("hello")
```

![Preview](/media/blog/images/example.png)

| Name | Value |
| --- | --- |
| Rows | 10M |
"""
        self.published_post.save()

        response = self.client.get(
            reverse("blog:detail", kwargs={"slug": self.published_post.slug})
        )
        document = BeautifulSoup(response.content, "html.parser")
        body = document.select_one("[data-article-body]")

        self.assertIsNotNone(body.find("h2"))
        self.assertIsNotNone(body.find("ul"))
        self.assertIsNotNone(body.find("ol"))
        self.assertIsNotNone(body.find("pre"))
        self.assertEqual(body.find("a")["href"], "https://example.com")
        self.assertEqual(body.find("img")["alt"], "Preview")
        self.assertIsNotNone(body.find("table"))

    def test_detail_normalizes_legacy_body_heading_to_keep_one_page_h1(self):
        Post.objects.filter(pk=self.published_post.pk).update(
            rendered_html="<h1>Legacy body heading</h1><p>Body</p>"
        )

        response = self.client.get(
            reverse("blog:detail", kwargs={"slug": self.published_post.slug})
        )
        document = BeautifulSoup(response.content, "html.parser")

        self.assertEqual(len(document.find_all("h1")), 1)
        self.assertEqual(
            document.select_one("[data-article-body] h2").get_text(strip=True),
            "Legacy body heading",
        )

    def test_detail_renders_one_article_navigation_and_one_site_footer(self):
        response = self.client.get(
            reverse("blog:detail", kwargs={"slug": self.published_post.slug})
        )
        document = BeautifulSoup(response.content, "html.parser")

        self.assertEqual(len(document.select("[data-article-navigation]")), 1)
        self.assertEqual(len(document.select("[data-site-footer]")), 1)
        self.assertNotContains(response, "Next article")

    def test_detail_renders_next_article_link_when_available(self):
        older_post = Post.objects.create(
            title="Older article",
            slug="older-article",
            markdown_body="Older body",
            status=Post.Status.PUBLISHED,
        )
        Post.objects.filter(pk=self.published_post.pk).update(
            published_at=timezone.now() + timedelta(days=1)
        )

        response = self.client.get(
            reverse("blog:detail", kwargs={"slug": self.published_post.slug})
        )
        document = BeautifulSoup(response.content, "html.parser")
        next_link = document.select_one(
            f'[data-article-navigation] a[href="/blog/{older_post.slug}/"]'
        )

        self.assertIsNotNone(next_link)
        self.assertIn("Next article", next_link.get_text(" ", strip=True))

    def test_detail_keeps_english_article_under_russian_interface(self):
        self.client.cookies[settings.LANGUAGE_COOKIE_NAME] = "ru"

        response = self.client.get(
            reverse("blog:detail", kwargs={"slug": self.published_post.slug})
        )
        document = BeautifulSoup(response.content, "html.parser")

        self.assertEqual(document.html["lang"], "ru")
        self.assertEqual(document.select_one("h1")["lang"], "en")
        self.assertEqual(document.select_one("[data-article-body]")["lang"], "en")
        self.assertContains(response, self.published_post.title)
        self.assertContains(response, "Visible body")
        self.assertContains(response, "Все статьи")

    def test_detail_context_exposes_next_published_post(self):
        next_post = Post.objects.create(
            title="Next post",
            slug="next-post",
            markdown_body="Next body",
            status=Post.Status.PUBLISHED,
        )
        Post.objects.filter(pk=self.published_post.pk).update(
            published_at=timezone.now() + timedelta(days=1)
        )

        response = self.client.get(
            reverse("blog:detail", kwargs={"slug": self.published_post.slug})
        )

        self.assertEqual(response.context["next_post"], next_post)

    def test_detail_hides_draft_post(self):
        response = self.client.get(
            reverse("blog:detail", kwargs={"slug": self.draft_post.slug})
        )

        self.assertEqual(response.status_code, 404)

    def test_index_handles_missing_blog_table(self):
        with patch(
            "blog.views.Post.objects.ordered_for_index", side_effect=OperationalError
        ):
            response = self.client.get(reverse("blog:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No published posts yet")
        self.assertContains(
            response,
            "Technical notes and field reports will appear here once published.",
        )

    def test_detail_handles_missing_blog_table(self):
        with patch("blog.views.Post.objects.get", side_effect=OperationalError):
            response = self.client.get(
                reverse("blog:detail", kwargs={"slug": "missing-post"})
            )

        self.assertEqual(response.status_code, 404)

    def test_blog_language_switcher_keeps_unprefixed_blog_path(self):
        response = self.client.get(reverse("blog:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="next" type="hidden" value="/blog/"')

    def test_blog_public_shell_renders_once_with_section_wordmark(self):
        urls = [
            reverse("blog:index"),
            reverse("blog:detail", kwargs={"slug": self.published_post.slug}),
        ]

        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                document = BeautifulSoup(response.content, "html.parser")

                self.assertEqual(len(document.select("[data-site-header]")), 1)
                self.assertEqual(len(document.select("[data-site-footer]")), 1)
                self.assertIn(
                    "IGOR SIMBIRTSEV / BLOG",
                    document.get_text(" ", strip=True),
                )

    def test_blog_language_switch_does_not_create_translated_article_url(self):
        response = self.client.get(
            reverse("blog:detail", kwargs={"slug": self.published_post.slug})
        )
        document = BeautifulSoup(response.content, "html.parser")
        next_paths = [field["value"] for field in document.select('input[name="next"]')]

        self.assertEqual(
            next_paths,
            [
                f"/blog/{self.published_post.slug}/",
                f"/blog/{self.published_post.slug}/",
            ],
        )

    def test_detail_has_canonical_url_and_description(self):
        response = self.client.get(
            reverse("blog:detail", kwargs={"slug": self.published_post.slug})
        )
        document = BeautifulSoup(response.content, "html.parser")

        self.assertEqual(
            document.find("link", rel="canonical")["href"],
            "https://igorsimb.ru/blog/published-post/",
        )
        self.assertTrue(document.find("meta", attrs={"name": "description"})["content"])

    def test_detail_uses_title_when_article_has_no_description_copy(self):
        self.published_post.summary = ""
        self.published_post.markdown_body = ""
        self.published_post.save()

        response = self.client.get(
            reverse("blog:detail", kwargs={"slug": self.published_post.slug})
        )
        document = BeautifulSoup(response.content, "html.parser")

        self.assertEqual(
            document.find("meta", attrs={"name": "description"})["content"].strip(),
            self.published_post.title,
        )

    def test_sitemap_tracks_published_status_dynamically(self):
        sitemap_url = reverse("sitemap")

        response = self.client.get(sitemap_url)
        self.assertContains(
            response,
            "https://igorsimb.ru/blog/published-post/",
        )
        self.assertNotContains(response, "https://igorsimb.ru/blog/draft-post/")

        self.draft_post.status = Post.Status.PUBLISHED
        self.draft_post.save()

        response = self.client.get(sitemap_url)
        self.assertContains(response, "https://igorsimb.ru/blog/draft-post/")
        self.assertContains(response, self.draft_post.updated_at.date().isoformat())

    def test_sitemap_handles_unavailable_blog_table(self):
        with patch("igorsimb.sitemaps.Post.objects.filter", side_effect=OperationalError):
            response = self.client.get(reverse("sitemap"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.published_post.slug)

    def test_legacy_blog_urls_redirect_permanently(self):
        for prefix in ("my", "read"):
            with self.subTest(prefix=prefix, page="index"):
                response = self.client.get(f"/{prefix}/blog/")
                self.assertRedirects(
                    response,
                    reverse("blog:index"),
                    status_code=301,
                    fetch_redirect_response=False,
                )

            with self.subTest(prefix=prefix, page="detail"):
                response = self.client.get(
                    f"/{prefix}/blog/{self.published_post.slug}/"
                )
                self.assertRedirects(
                    response,
                    reverse(
                        "blog:detail", kwargs={"slug": self.published_post.slug}
                    ),
                    status_code=301,
                    fetch_redirect_response=False,
                )


class BlogAuthoringViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.superuser = User.objects.create_superuser(
            username="admin@example.com",
            email="admin@example.com",
            password="password123",
        )
        cls.user = User.objects.create_user(
            username="user@example.com",
            email="user@example.com",
            password="password123",
        )
        cls.post = Post.objects.create(
            title="Existing post",
            slug="existing-post",
            markdown_body="Existing body",
            status=Post.Status.DRAFT,
        )

    def setUp(self):
        self.post = Post.objects.get(pk=self.post.pk)

    def test_dashboard_redirects_anonymous_user_to_login(self):
        response = self.client.get(reverse("blog:dashboard"))

        self.assertEqual(response.status_code, 302)

    def test_dashboard_allows_superuser(self):
        self.client.force_login(self.superuser)

        response = self.client.get(reverse("blog:dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Blog dashboard")
        self.assertContains(response, self.post.title)

        soup = BeautifulSoup(response.content, "html.parser")
        self.assertEqual(len(soup.select("[data-site-header]")), 1)
        self.assertEqual(len(soup.select("[data-site-footer]")), 1)
        self.assertIsNotNone(soup.select_one("main#main-content.blog-workspace"))
        self.assertEqual(soup.select("a[aria-current='page']"), [])
        self.assertEqual(
            soup.find("meta", attrs={"name": "robots"})["content"],
            "noindex, nofollow",
        )

    def test_dashboard_phase_six_copy_is_translated_to_russian(self):
        self.client.force_login(self.superuser)
        self.client.cookies[settings.LANGUAGE_COOKIE_NAME] = "ru"

        response = self.client.get(reverse("blog:dashboard"))

        self.assertContains(response, "Навигация автора")
        self.assertContains(response, "Публичный блог")
        self.assertContains(response, "Посты по статусу")
        self.assertContains(response, "Опубликованные материалы")

    def test_dashboard_renders_empty_draft_and_published_groups(self):
        self.client.force_login(self.superuser)
        Post.objects.all().delete()

        response = self.client.get(reverse("blog:dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No drafts waiting.")
        self.assertContains(response, "Nothing published yet.")

    def test_dashboard_keeps_draft_and_published_posts_in_their_groups(self):
        self.client.force_login(self.superuser)
        published_post = Post.objects.create(
            title="Published dashboard post",
            slug="published-dashboard-post",
            markdown_body="Published body",
            status=Post.Status.PUBLISHED,
        )

        response = self.client.get(reverse("blog:dashboard"))

        soup = BeautifulSoup(response.content, "html.parser")
        draft_panel = soup.select_one("[aria-labelledby='draft-posts-heading']")
        published_panel = soup.select_one("[aria-labelledby='published-posts-heading']")
        self.assertIn(self.post.title, draft_panel.get_text(" ", strip=True))
        self.assertNotIn(published_post.title, draft_panel.get_text(" ", strip=True))
        self.assertIn(published_post.title, published_panel.get_text(" ", strip=True))
        self.assertNotIn(self.post.title, published_panel.get_text(" ", strip=True))

    def test_dashboard_forbids_non_superuser(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("blog:dashboard"))

        self.assertEqual(response.status_code, 403)

    def test_dashboard_handles_missing_blog_table(self):
        self.client.force_login(self.superuser)

        with patch("blog.views.is_blog_table_ready", return_value=False):
            response = self.client.get(reverse("blog:dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "The blog table is not available in this database yet."
        )
        self.assertNotContains(response, "No drafts waiting.")
        self.assertNotContains(response, "Nothing published yet.")
        self.assertNotContains(response, "New post")
        self.assertContains(response, "Published posts will appear here")

    def test_editor_redirects_anonymous_user_to_login(self):
        response = self.client.get(reverse("blog:editor_create"))

        self.assertEqual(response.status_code, 302)

    def test_editor_create_post_redirects_anonymous_user_to_login(self):
        response = self.client.post(
            reverse("blog:editor_create"),
            {"title": "Anonymous create", "markdown_body": "Body", "action": "save"},
        )

        self.assertEqual(response.status_code, 302)

    def test_editor_create_forbids_non_superuser(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("blog:editor_create"))

        self.assertEqual(response.status_code, 403)

    def test_editor_create_post_forbids_non_superuser(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("blog:editor_create"),
            {"title": "Blocked create", "markdown_body": "Nope", "action": "save"},
        )

        self.assertEqual(response.status_code, 403)

    def test_editor_existing_post_redirects_anonymous_user_to_login(self):
        response = self.client.get(reverse("blog:editor", kwargs={"pk": self.post.pk}))

        self.assertEqual(response.status_code, 302)

    def test_editor_existing_post_post_redirects_anonymous_user_to_login(self):
        response = self.client.post(
            reverse("blog:editor", kwargs={"pk": self.post.pk}),
            {"title": "Anonymous edit", "markdown_body": "Body", "action": "save"},
        )

        self.assertEqual(response.status_code, 302)

    def test_editor_existing_post_forbids_non_superuser(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("blog:editor", kwargs={"pk": self.post.pk}))

        self.assertEqual(response.status_code, 403)

    def test_editor_existing_post_post_forbids_non_superuser(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("blog:editor", kwargs={"pk": self.post.pk}),
            {"title": "Blocked update", "markdown_body": "Nope", "action": "save"},
        )

        self.assertEqual(response.status_code, 403)

    def test_editor_shows_existing_post_to_superuser(self):
        self.client.force_login(self.superuser)

        response = self.client.get(reverse("blog:editor", kwargs={"pk": self.post.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post.title)

    def test_editor_preserves_interactive_workflow_contracts(self):
        self.client.force_login(self.superuser)

        response = self.client.get(reverse("blog:editor", kwargs={"pk": self.post.pk}))

        soup = BeautifulSoup(response.content, "html.parser")
        form = soup.select_one("form#blog-editor-form")
        self.assertEqual(len(soup.select("[data-site-header]")), 1)
        self.assertEqual(len(soup.select("[data-site-footer]")), 1)
        self.assertIsNotNone(soup.select_one("main#main-content.blog-workspace--editor"))
        self.assertEqual(
            soup.find("meta", attrs={"name": "robots"})["content"],
            "noindex, nofollow",
        )
        self.assertEqual(form["data-upload-url"], reverse("blog:editor_upload_image"))
        self.assertIn(reverse("blog:editor_save"), form["data-on:submit__prevent"])
        self.assertIn("action: 'autosave'", form["data-on:input__debounce.1200ms"])
        self.assertIsNotNone(form.select_one("#id_markdown_body"))
        self.assertIsNotNone(soup.select_one("#blog-editor-upload-flash"))
        self.assertIsNotNone(soup.select_one("[data-sync-scroll='preview']"))
        self.assertEqual(
            {button.get("value") for button in form.select("button[name='action']")},
            {"save", "publish", "unpublish"},
        )
        self.assertEqual(len(soup.select(".blog-mode-switch__button")), 3)

    def test_editor_localizes_image_upload_feedback(self):
        self.client.force_login(self.superuser)
        self.client.cookies[settings.LANGUAGE_COOKIE_NAME] = "ru"

        response = self.client.get(reverse("blog:editor_create"))
        form = BeautifulSoup(response.content, "html.parser").select_one("#blog-editor-form")

        self.assertEqual(form["data-upload-one-working"], "Загрузка изображения...")
        self.assertEqual(form["data-upload-many-working"], "Загрузка изображений...")
        self.assertEqual(form["data-upload-one-success"], "Изображение вставлено.")
        self.assertEqual(form["data-upload-many-success"], "Изображения вставлены.")
        self.assertEqual(
            form["data-upload-failed"],
            "Не удалось загрузить изображение. Обновите страницу и повторите попытку.",
        )

    def test_invalid_editor_form_remains_visible_without_changing_post(self):
        self.client.force_login(self.superuser)

        response = self.client.post(
            reverse("blog:editor", kwargs={"pk": self.post.pk}),
            {"title": "", "markdown_body": "Unsaved replacement", "action": "save"},
        )

        self.post.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")
        self.assertContains(response, "Unsaved replacement")
        self.assertEqual(self.post.title, "Existing post")
        self.assertEqual(self.post.markdown_body, "Existing body")

    def test_editor_handles_missing_blog_table_on_get(self):
        self.client.force_login(self.superuser)

        with patch("blog.views.is_blog_table_ready", return_value=False):
            response = self.client.get(reverse("blog:editor_create"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Run migrations for the current blog app before saving or publishing.",
        )

    def test_existing_editor_handles_missing_blog_table_on_get(self):
        self.client.force_login(self.superuser)

        with patch("blog.views.is_blog_table_ready", return_value=False):
            response = self.client.get(
                reverse("blog:editor", kwargs={"pk": self.post.pk})
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Run migrations for the current blog app before saving or publishing.",
        )

    def test_editor_handles_missing_blog_table_on_post(self):
        self.client.force_login(self.superuser)

        with patch("blog.views.is_blog_table_ready", return_value=False):
            response = self.client.post(
                reverse("blog:editor_create"),
                {
                    "title": "Blocked by setup",
                    "markdown_body": "Body",
                    "action": "save",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "Run migrations for the current blog app before saving posts."
        )
        self.assertFalse(Post.objects.filter(title="Blocked by setup").exists())

    def test_existing_editor_handles_missing_blog_table_on_post(self):
        self.client.force_login(self.superuser)

        with patch("blog.views.is_blog_table_ready", return_value=False):
            response = self.client.post(
                reverse("blog:editor", kwargs={"pk": self.post.pk}),
                {
                    "title": self.post.title,
                    "markdown_body": self.post.markdown_body,
                    "action": "save",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "Run migrations for the current blog app before saving posts."
        )

    def test_preview_endpoint_returns_rendered_preview_html(self):
        self.client.force_login(self.superuser)

        response = self.client.post(
            reverse("blog:editor_preview"),
            data=json.dumps({"title": "Draft", "markdownBody": "# Heading\n\nBody"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("<h2>Heading</h2>", response.json()["previewHtml"])

    def test_save_endpoint_autosaves_draft_and_returns_editor_state(self):
        self.client.force_login(self.superuser)

        response = self.client.post(
            reverse("blog:editor_save"),
            data=json.dumps(
                {"title": "Autosaved", "markdownBody": "Body", "action": "autosave"}
            ),
            content_type="application/json",
        )

        post = Post.objects.get(title="Autosaved")
        payload = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(post.status, Post.Status.DRAFT)
        self.assertEqual(payload["postId"], post.pk)
        self.assertEqual(payload["saveMessage"], "Draft autosaved.")

    def test_save_endpoint_publishes_post(self):
        self.client.force_login(self.superuser)

        response = self.client.post(
            reverse("blog:editor_save"),
            data=json.dumps(
                {
                    "postId": self.post.pk,
                    "title": self.post.title,
                    "markdownBody": self.post.markdown_body,
                    "action": "publish",
                }
            ),
            content_type="application/json",
        )

        self.post.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.post.status, Post.Status.PUBLISHED)
        self.assertTrue(response.json()["isPublished"])

    def test_editor_save_preserves_admin_managed_presentation_fields(self):
        self.client.force_login(self.superuser)
        self.post.summary = "Admin summary"
        self.post.tags = "Django, AI"
        self.post.is_featured = True
        self.post.feature_priority = 3
        self.post.save()

        response = self.client.post(
            reverse("blog:editor", kwargs={"pk": self.post.pk}),
            {
                "title": "Edited title",
                "markdown_body": "Edited body",
                "action": "save",
            },
        )

        self.post.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.post.summary, "Admin summary")
        self.assertEqual(self.post.tags, "Django, AI")
        self.assertTrue(self.post.is_featured)
        self.assertEqual(self.post.feature_priority, 3)

    def test_save_endpoint_unpublishes_post(self):
        self.client.force_login(self.superuser)
        self.post.status = Post.Status.PUBLISHED
        self.post.save()

        response = self.client.post(
            reverse("blog:editor_save"),
            data=json.dumps(
                {
                    "postId": self.post.pk,
                    "title": self.post.title,
                    "markdownBody": self.post.markdown_body,
                    "action": "unpublish",
                }
            ),
            content_type="application/json",
        )

        self.post.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.post.status, Post.Status.DRAFT)
        self.assertFalse(response.json()["isPublished"])

    def test_save_endpoint_forbids_non_superuser(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("blog:editor_save"),
            data=json.dumps(
                {"title": "Blocked", "markdownBody": "Body", "action": "save"}
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 403)

    def test_preview_endpoint_redirects_anonymous_user_to_login(self):
        response = self.client.post(
            reverse("blog:editor_preview"),
            data=json.dumps({"title": "Draft", "markdownBody": "Body"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 302)

    def test_editor_nonexistent_post_redirects_anonymous_user_to_login(self):
        response = self.client.get(reverse("blog:editor", kwargs={"pk": 99999}))

        self.assertEqual(response.status_code, 302)

    def test_editor_allows_superuser_to_create_draft(self):
        self.client.force_login(self.superuser)

        response = self.client.post(
            reverse("blog:editor_create"),
            {"title": "New draft", "markdown_body": "Draft body", "action": "save"},
            follow=True,
        )

        post = Post.objects.get(title="New draft")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(post.status, Post.Status.DRAFT)
        self.assertContains(response, "Draft saved.")
        self.assertNotIn(post.slug, RESERVED_SLUGS)

    def test_editor_allows_superuser_to_publish_post(self):
        self.client.force_login(self.superuser)

        response = self.client.post(
            reverse("blog:editor_create"),
            {
                "title": "Published from editor",
                "markdown_body": "Body",
                "action": "publish",
            },
            follow=True,
        )

        post = Post.objects.get(title="Published from editor")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(post.status, Post.Status.PUBLISHED)
        self.assertIsNotNone(post.published_at)
        self.assertContains(response, "Post published.")

    def test_editor_allows_superuser_to_unpublish_post(self):
        self.client.force_login(self.superuser)
        self.post.status = Post.Status.PUBLISHED
        self.post.save()

        response = self.client.post(
            reverse("blog:editor", kwargs={"pk": self.post.pk}),
            {
                "title": self.post.title,
                "markdown_body": self.post.markdown_body,
                "action": "unpublish",
            },
            follow=True,
        )

        self.post.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.post.status, Post.Status.DRAFT)
        self.assertIsNone(self.post.published_at)
        self.assertContains(response, "Post moved back to draft.")

    def test_editor_reserves_workspace_slug_values(self):
        self.client.force_login(self.superuser)

        response = self.client.post(
            reverse("blog:editor_create"),
            {"title": "Dashboard", "markdown_body": "Body", "action": "publish"},
            follow=True,
        )

        post = Post.objects.get(title="Dashboard")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(post.slug, "dashboard-2")


class BlogImageUploadTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.superuser = User.objects.create_superuser(
            username="image-admin@example.com",
            email="image-admin@example.com",
            password="password123",
        )
        cls.user = User.objects.create_user(
            username="image-user@example.com",
            email="image-user@example.com",
            password="password123",
        )

    def setUp(self):
        self.media_root = tempfile.mkdtemp()
        self.settings_context = self.settings(MEDIA_ROOT=self.media_root)
        self.settings_context.enable()
        self.addCleanup(self.settings_context.disable)
        self.addCleanup(shutil.rmtree, self.media_root, True)

    def test_upload_image_returns_media_url_for_superuser(self):
        self.client.force_login(self.superuser)

        response = self.client.post(
            reverse("blog:editor_upload_image"),
            {
                "image": SimpleUploadedFile(
                    "inline-shot.png", PNG_IMAGE_BYTES, content_type="image/png"
                )
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["imageUrl"].startswith("/media/blog/images/"))

        saved_files = []
        for root, _, files in os.walk(self.media_root):
            for filename in files:
                saved_files.append(os.path.join(root, filename))

        self.assertEqual(len(saved_files), 1)

    def test_upload_image_redirects_anonymous_user_to_login(self):
        response = self.client.post(
            reverse("blog:editor_upload_image"),
            {
                "image": SimpleUploadedFile(
                    "inline-shot.png", PNG_IMAGE_BYTES, content_type="image/png"
                )
            },
        )

        self.assertEqual(response.status_code, 302)

    def test_upload_image_forbids_non_superuser(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("blog:editor_upload_image"),
            {
                "image": SimpleUploadedFile(
                    "inline-shot.png", PNG_IMAGE_BYTES, content_type="image/png"
                )
            },
        )

        self.assertEqual(response.status_code, 403)

    def test_upload_image_rejects_invalid_content_type(self):
        self.client.force_login(self.superuser)

        response = self.client.post(
            reverse("blog:editor_upload_image"),
            {
                "image": SimpleUploadedFile(
                    "notes.txt", b"not an image", content_type="text/plain"
                )
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error"], "Upload a PNG, JPEG, GIF, or WebP image."
        )

    @patch("blog.views.MAX_BLOG_IMAGE_SIZE", 10)
    def test_upload_image_rejects_oversized_file(self):
        self.client.force_login(self.superuser)

        response = self.client.post(
            reverse("blog:editor_upload_image"),
            {
                "image": SimpleUploadedFile(
                    "large.png", PNG_IMAGE_BYTES, content_type="image/png"
                )
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "Upload an image smaller than 5 MB.")

    def test_upload_image_rejects_invalid_image_bytes(self):
        self.client.force_login(self.superuser)

        response = self.client.post(
            reverse("blog:editor_upload_image"),
            {
                "image": SimpleUploadedFile(
                    "broken.png", b"broken image data", content_type="image/png"
                )
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "That file is not a valid image.")

    @patch("blog.views.Image.open", return_value=FakeImage("BMP"))
    def test_upload_image_rejects_mismatched_decoded_format(self, _image_open):
        self.client.force_login(self.superuser)

        response = self.client.post(
            reverse("blog:editor_upload_image"),
            {
                "image": SimpleUploadedFile(
                    "mismatch.png", PNG_IMAGE_BYTES, content_type="image/png"
                )
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error"],
            "The uploaded image format does not match the file type.",
        )

    @patch("blog.views.Image.open", side_effect=DecompressionBombError("bomb"))
    def test_upload_image_rejects_decompression_bomb(self, _image_open):
        self.client.force_login(self.superuser)

        response = self.client.post(
            reverse("blog:editor_upload_image"),
            {
                "image": SimpleUploadedFile(
                    "bomb.png", PNG_IMAGE_BYTES, content_type="image/png"
                )
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "That file is not a valid image.")
