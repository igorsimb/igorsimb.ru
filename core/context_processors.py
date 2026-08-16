from django.conf import settings


def seo(request):
    canonical_origin = settings.CANONICAL_ORIGIN.rstrip("/")
    return {"canonical_url": f"{canonical_origin}{request.path}"}
