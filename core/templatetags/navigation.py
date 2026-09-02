from django import template
from django.conf import settings
from django.urls import translate_url

register = template.Library()


@register.simple_tag(takes_context=True)
def language_switch_path(context, language_code=None):
    request = context.get("request")
    if request is None:
        return "/"

    if language_code is None:
        full_path = request.get_full_path()
        for current_language_code, _ in settings.LANGUAGES:
            prefix = f"/{current_language_code}/"
            if full_path.startswith(prefix):
                return full_path[len(current_language_code) + 1 :]

            exact_prefix = f"/{current_language_code}"
            if full_path == exact_prefix:
                return "/"

        return full_path

    return translate_url(request.get_full_path(), language_code)
