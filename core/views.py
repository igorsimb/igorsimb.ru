from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import OperationalError, ProgrammingError
from django.shortcuts import render
from django.views.decorators.http import require_GET
from django.views.generic import TemplateView

from blog.models import Post

User = get_user_model()


@require_GET
def robots_txt(request):
    sitemap_url = f"{settings.CANONICAL_ORIGIN.rstrip('/')}/sitemap.xml"
    return render(
        request,
        "core/robots.txt",
        {"sitemap_url": sitemap_url},
        content_type="text/plain",
    )


class IndexView(TemplateView):
    template_name = "core/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["featured_posts"] = Post.objects.for_homepage()
            context["latest_posts"] = Post.objects.latest_for_homepage()
        except (OperationalError, ProgrammingError):
            context["featured_posts"] = []
            context["latest_posts"] = []

        return context


class MPMonitorView(TemplateView):
    template_name = "core/projects/mp_monitor_project.html"


class Ez2TaskView(TemplateView):
    template_name = "core/projects/ez2task_project.html"


class StoreProjectView(TemplateView):
    template_name = "core/projects/store_project.html"
