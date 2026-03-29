from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify

from .models import Post

RESERVED_SLUGS = {"dashboard", "write"}


class PostEditorForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "markdown_body"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "blog-editor__input",
                    "placeholder": _("Post title"),
                    "autocomplete": "off",
                }
            ),
            "markdown_body": forms.Textarea(
                attrs={
                    "class": "blog-editor__textarea",
                    "placeholder": _("Write in Markdown..."),
                    "rows": 22,
                    "spellcheck": "false",
                }
            ),
        }

    def save(self, commit=True, action="save"):
        post = super().save(commit=False)

        if not post.slug:
            post.slug = self._generate_unique_slug()

        if action == "publish":
            post.status = Post.Status.PUBLISHED
        elif action == "unpublish":
            post.status = Post.Status.DRAFT
        elif not post.pk:
            post.status = Post.Status.DRAFT

        if commit:
            post.save()

        return post

    def _generate_unique_slug(self):
        base_slug = slugify(self.cleaned_data["title"]) or "post"
        slug = base_slug
        suffix = 2

        while (
            slug in RESERVED_SLUGS
            or Post.objects.filter(slug=slug).exclude(pk=self.instance.pk).exists()
        ):
            slug = f"{base_slug}-{suffix}"
            suffix += 1

        return slug
