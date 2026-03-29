from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag(takes_context=True)
def language_switch_path(context):
    request = context.get("request")
    if request is None:
        return "/"

    full_path = request.get_full_path()
    for language_code, _ in settings.LANGUAGES:
        prefix = f"/{language_code}/"
        if full_path.startswith(prefix):
            return full_path[len(language_code) + 1 :]

        exact_prefix = f"/{language_code}"
        if full_path == exact_prefix:
            return "/"

    return full_path
