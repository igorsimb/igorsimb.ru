from django.conf import settings
from django.contrib.staticfiles import finders
from django.templatetags.static import static


RESUME_ASSETS = {
    "en": "core/img/resume_igor_simbirtsev(ENG).pdf",
    "ru": "core/img/resume_igor_simbirtsev(RUS).pdf",
}


def seo(request):
    canonical_origin = settings.CANONICAL_ORIGIN.rstrip("/")
    language_code = getattr(request, "LANGUAGE_CODE", settings.LANGUAGE_CODE)
    resume_path = RESUME_ASSETS.get(language_code, RESUME_ASSETS["en"])
    resume_url = static(resume_path) if finders.find(resume_path) else ""

    return {
        "canonical_url": f"{canonical_origin}{request.path}",
        "resume_url": resume_url,
    }
