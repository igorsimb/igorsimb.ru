from django.test import TestCase
from django.urls import reverse, resolve

from .views import IndexView


class IndexPageTests(TestCase):
    def setUp(self):
        url = reverse("core:main")
        self.response = self.client.get(url)

    def test_url_exists_at_correct_location(self):
        self.assertEqual(self.response.status_code, 200)

    def test_index_template(self):
        self.assertTemplateUsed(self.response, "core/index.html")

    def test_index_page_contains_correct_html(self):
        self.assertContains(self.response, "Igor Simbirtsev")

    def test_index_page_does_not_contain_incorrect_html(self):
        self.assertNotContains(self.response, "Hi! I should not be on the page.")

    def test_index_page_url_resolves_index_view(self):
        view = resolve(reverse("core:main"))
        self.assertEqual(view.func.__name__, IndexView.as_view().__name__)

    def test_language_switcher_keeps_current_page_for_i18n_routes(self):
        self.assertContains(self.response, 'name="next" type="hidden" value="/"')

    def test_index_page_uses_canonical_production_url(self):
        self.assertContains(
            self.response,
            '<link rel="canonical" href="https://igorsimb.ru/en/">',
            html=True,
        )


class RobotsTxtTests(TestCase):
    def test_robots_txt_allows_public_pages_and_advertises_sitemap(self):
        response = self.client.get(reverse("robots_txt"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Content-Type"], "text/plain")
        self.assertContains(response, "User-agent: *")
        self.assertContains(response, "Allow: /")
        self.assertContains(response, "Disallow: /blog/write/")
        self.assertContains(response, "Sitemap: https://igorsimb.ru/sitemap.xml")
