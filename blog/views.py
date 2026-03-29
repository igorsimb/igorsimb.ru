import json
from pathlib import Path

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import redirect_to_login
from django.core.files.storage import default_storage
from django.core.exceptions import PermissionDenied
from django.db import connection
from django.db import OperationalError, ProgrammingError
from django.http import Http404
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext as _
from django.views import View
from django.views.generic import DetailView, TemplateView
from PIL import Image, UnidentifiedImageError
from PIL.Image import DecompressionBombError

from .forms import PostEditorForm
from .models import Post
from .rendering import render_markdown


ALLOWED_BLOG_IMAGE_CONTENT_TYPES = {
    "image/gif",
    "image/jpeg",
    "image/png",
    "image/webp",
}
BLOG_IMAGE_FORMAT_CONTENT_TYPES = {
    "GIF": "image/gif",
    "JPEG": "image/jpeg",
    "PNG": "image/png",
    "WEBP": "image/webp",
}
BLOG_IMAGE_SUFFIXES = {
    "image/gif": ".gif",
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}
MAX_BLOG_IMAGE_SIZE = 5 * 1024 * 1024


def is_blog_table_ready():
    try:
        return Post._meta.db_table in connection.introspection.table_names()
    except (OperationalError, ProgrammingError):
        return False


def parse_json_body(request):
    if not request.body:
        return {}

    try:
        return json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {}


def build_blog_image_upload_path(uploaded_image, content_type):
    stem = slugify(Path(uploaded_image.name).stem) or "image"
    suffix = BLOG_IMAGE_SUFFIXES.get(content_type, ".png")
    timestamp = timezone.now()
    return timestamp.strftime(f"blog/images/%Y/%m/{stem}-%H%M%S{suffix}")


def build_editor_signal_patch(
    post=None, title="", markdown_body="", save_message="", save_tone="idle"
):
    preview_html = post.rendered_html if post else render_markdown(markdown_body)
    editor_url = (
        reverse("blog:editor", kwargs={"pk": post.pk})
        if post
        else reverse("blog:editor_create")
    )
    public_url = (
        reverse("blog:detail", kwargs={"slug": post.slug})
        if post and post.is_published
        else ""
    )
    updated_at_label = ""
    if post:
        updated_at_label = timezone.localtime(post.updated_at).strftime(
            "%b %d, %Y %H:%M"
        )

    return {
        "postId": post.pk if post else None,
        "postSlug": post.slug if post else "",
        "previewHtml": preview_html,
        "saveMessage": save_message,
        "saveTone": save_tone,
        "isPublished": bool(post and post.is_published),
        "statusLabel": _("Published") if post and post.is_published else _("Draft"),
        "updatedAtLabel": updated_at_label,
        "editorUrl": editor_url,
        "publicUrl": public_url,
        "blogTableReady": is_blog_table_ready(),
        "hasPost": bool(post),
        "editorTitle": title,
        "markdownBody": markdown_body,
    }


class BlogIndexView(TemplateView):
    template_name = "blog/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["posts"] = list(Post.objects.filter(status=Post.Status.PUBLISHED))
        except (OperationalError, ProgrammingError):
            context["posts"] = []

        return context


class BlogDetailView(DetailView):
    context_object_name = "post"
    template_name = "blog/detail.html"

    def get_object(self, queryset=None):
        try:
            return Post.objects.get(
                slug=self.kwargs["slug"], status=Post.Status.PUBLISHED
            )
        except Post.DoesNotExist as exc:
            raise Http404 from exc
        except (OperationalError, ProgrammingError) as exc:
            raise Http404 from exc


class BlogAuthorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect_to_login(
                self.request.get_full_path(),
                self.get_login_url(),
                self.get_redirect_field_name(),
            )

        raise PermissionDenied


class BlogDashboardView(BlogAuthorRequiredMixin, TemplateView):
    template_name = "blog/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["blog_table_ready"] = is_blog_table_ready()
        if context["blog_table_ready"]:
            try:
                context["draft_posts"] = list(
                    Post.objects.filter(status=Post.Status.DRAFT).order_by(
                        "-updated_at"
                    )
                )
                context["published_posts"] = list(
                    Post.objects.filter(status=Post.Status.PUBLISHED).order_by(
                        "-published_at", "-updated_at"
                    )
                )
            except (OperationalError, ProgrammingError):
                context["draft_posts"] = []
                context["published_posts"] = []
                context["blog_table_ready"] = False
        else:
            context["draft_posts"] = []
            context["published_posts"] = []

        return context


class BlogEditorView(BlogAuthorRequiredMixin, TemplateView):
    template_name = "blog/editor.html"

    def get_post_instance(self):
        if not is_blog_table_ready():
            return None

        post_pk = self.kwargs.get("pk")
        if post_pk is None:
            return None

        try:
            return get_object_or_404(Post, pk=post_pk)
        except (OperationalError, ProgrammingError) as exc:
            raise Http404 from exc

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = kwargs.get("post")
        if post is None:
            post = self.get_post_instance()

        form = kwargs.get("form") or PostEditorForm(instance=post)
        preview_html = kwargs.get("preview_html")
        if preview_html is None:
            preview_html = post.rendered_html if post else ""

        context["form"] = form
        context["post"] = post
        context["preview_html"] = preview_html
        context["blog_table_ready"] = is_blog_table_ready()

        return context

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        if not is_blog_table_ready():
            form = PostEditorForm(request.POST)
            preview_html = render_markdown(request.POST.get("markdown_body", ""))
            messages.error(
                request,
                _("Run migrations for the current blog app before saving posts."),
            )
            return self.render_to_response(
                self.get_context_data(form=form, post=None, preview_html=preview_html)
            )

        post = self.get_post_instance()
        form = PostEditorForm(request.POST, instance=post)
        preview_html = render_markdown(request.POST.get("markdown_body", ""))

        if not form.is_valid():
            return self.render_to_response(
                self.get_context_data(form=form, post=post, preview_html=preview_html)
            )

        action = request.POST.get("action", "save")
        post = form.save(action=action)

        if action == "publish":
            messages.success(request, _("Post published."))
        elif action == "unpublish":
            messages.success(request, _("Post moved back to draft."))
        else:
            messages.success(request, _("Draft saved."))

        return redirect("blog:editor", pk=post.pk)


class BlogEditorPreviewView(BlogAuthorRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        payload = parse_json_body(request)

        return JsonResponse(
            {"previewHtml": render_markdown(payload.get("markdownBody", ""))}
        )


class BlogEditorSaveView(BlogAuthorRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        payload = parse_json_body(request)
        title = payload.get("title", "")
        markdown_body = payload.get("markdownBody", "")
        action = payload.get("action", "autosave")
        post_id = payload.get("postId")

        if not is_blog_table_ready():
            return JsonResponse(
                build_editor_signal_patch(
                    title=title,
                    markdown_body=markdown_body,
                    save_message=_(
                        "Run migrations for the current blog app before saving posts."
                    ),
                    save_tone="error",
                )
            )

        post = get_object_or_404(Post, pk=post_id) if post_id else None
        form = PostEditorForm(
            {"title": title, "markdown_body": markdown_body}, instance=post
        )
        if not form.is_valid():
            return JsonResponse(
                build_editor_signal_patch(
                    post=post,
                    title=title,
                    markdown_body=markdown_body,
                    save_message=form.errors.get(
                        "title", [_("Add a title before saving.")]
                    )[0],
                    save_tone="error",
                )
            )

        post = form.save(action=action)
        save_message = {
            "autosave": _("Draft autosaved."),
            "save": _("Draft saved."),
            "publish": _("Post published."),
            "unpublish": _("Post moved back to draft."),
        }.get(action, _("Draft saved."))

        return JsonResponse(
            build_editor_signal_patch(
                post=post,
                title=post.title,
                markdown_body=post.markdown_body,
                save_message=save_message,
                save_tone="success",
            )
        )


class BlogImageUploadView(BlogAuthorRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        uploaded_image = request.FILES.get("image")
        if not uploaded_image:
            return JsonResponse({"error": _("Choose an image to upload.")}, status=400)

        if uploaded_image.content_type not in ALLOWED_BLOG_IMAGE_CONTENT_TYPES:
            return JsonResponse(
                {"error": _("Upload a PNG, JPEG, GIF, or WebP image.")},
                status=400,
            )

        if uploaded_image.size > MAX_BLOG_IMAGE_SIZE:
            return JsonResponse(
                {"error": _("Upload an image smaller than 5 MB.")},
                status=400,
            )

        try:
            with Image.open(uploaded_image) as image:
                image_content_type = BLOG_IMAGE_FORMAT_CONTENT_TYPES.get(image.format)
                image.verify()
        except (DecompressionBombError, UnidentifiedImageError, OSError):
            return JsonResponse(
                {"error": _("That file is not a valid image.")}, status=400
            )

        if image_content_type != uploaded_image.content_type:
            return JsonResponse(
                {"error": _("The uploaded image format does not match the file type.")},
                status=400,
            )

        uploaded_image.seek(0)
        image_path = default_storage.save(
            build_blog_image_upload_path(uploaded_image, image_content_type),
            uploaded_image,
        )
        return JsonResponse({"imageUrl": default_storage.url(image_path)})
