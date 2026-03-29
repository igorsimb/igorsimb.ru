import json
import os
import shutil
import tempfile

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.db import OperationalError
from django.core.files.uploadedfile import SimpleUploadedFile
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


class MarkdownRenderingTests(TestCase):
    def test_render_markdown_supports_common_elements(self):
        html = render_markdown("# Heading\n\nA [link](https://example.com) and `code`.")

        self.assertIn("<h1>Heading</h1>", html)
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

    def test_detail_shows_published_post(self):
        response = self.client.get(
            reverse("blog:detail", kwargs={"slug": self.published_post.slug})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.published_post.title)
        self.assertContains(response, "Visible body")

    def test_detail_hides_draft_post(self):
        response = self.client.get(
            reverse("blog:detail", kwargs={"slug": self.draft_post.slug})
        )

        self.assertEqual(response.status_code, 404)

    def test_index_handles_missing_blog_table(self):
        with patch("blog.views.Post.objects.filter", side_effect=OperationalError):
            response = self.client.get(reverse("blog:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No published posts yet.")
        self.assertContains(response, "Nothing is live yet.")

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
        self.assertIn("<h1>Heading</h1>", response.json()["previewHtml"])

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
