from unittest.mock import patch

from bs4 import BeautifulSoup
from django.db import OperationalError
from django.test import TestCase
from django.urls import reverse, resolve

from blog.models import Post

from .views import IndexView


class IndexPageTests(TestCase):
    def setUp(self):
        self.response = self.client.get("/en/")

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
        document = BeautifulSoup(self.response.content, "html.parser")
        next_paths = [field["value"] for field in document.select('input[name="next"]')]

        self.assertEqual(next_paths, ["/en/", "/ru/"])

    def test_language_switch_redirects_to_selected_core_route(self):
        response = self.client.post(
            reverse("set_language"),
            {"language": "ru", "next": "/ru/"},
        )

        self.assertRedirects(
            response,
            "/ru/",
            fetch_redirect_response=False,
        )
        self.assertEqual(response.cookies["django_language"].value, "ru")

    def test_index_page_uses_canonical_production_url(self):
        self.assertContains(
            self.response,
            '<link rel="canonical" href="https://igorsimb.ru/en/">',
            html=True,
        )

    def test_index_context_contains_at_most_three_featured_posts(self):
        for number in range(4):
            Post.objects.create(
                title=f"Post {number}",
                slug=f"post-{number}",
                markdown_body="Body",
                status=Post.Status.PUBLISHED,
                is_featured=True,
                feature_priority=number,
            )

        response = self.client.get(reverse("core:main"))

        self.assertEqual(len(response.context["featured_posts"]), 3)
        self.assertEqual(response.context["latest_posts"], [])

    def test_index_handles_unavailable_blog_table(self):
        with patch(
            "core.views.Post.objects.for_homepage", side_effect=OperationalError
        ):
            response = self.client.get(reverse("core:main"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["featured_posts"], [])
        self.assertEqual(response.context["latest_posts"], [])

    def test_public_shell_renders_one_header_and_footer(self):
        document = BeautifulSoup(self.response.content, "html.parser")

        self.assertEqual(len(document.select("[data-site-header]")), 1)
        self.assertEqual(len(document.select("[data-site-footer]")), 1)
        self.assertEqual(len(document.find_all("h1")), 1)

    def test_public_shell_uses_native_mobile_navigation(self):
        document = BeautifulSoup(self.response.content, "html.parser")
        mobile_menu = document.select_one("details.site-mobile-menu")

        self.assertIsNotNone(mobile_menu)
        self.assertIsNotNone(mobile_menu.find("summary"))
        self.assertIsNotNone(mobile_menu.find("nav"))
        self.assertIsNotNone(document.select_one('script[src$="/core/js/public-site.js"]'))

    def test_resume_matches_interface_language(self):
        english_document = BeautifulSoup(self.response.content, "html.parser")
        russian_response = self.client.get("/ru/")
        russian_document = BeautifulSoup(russian_response.content, "html.parser")

        self.assertEqual(english_document.html["lang"], "en")
        self.assertIn(
            "resume_igor_simbirtsev(ENG).pdf",
            english_document.select_one("a[download]")["href"],
        )
        self.assertEqual(russian_document.html["lang"], "ru")
        self.assertIn("Избранное", russian_document.get_text(" ", strip=True))
        self.assertIn("Резюме", russian_document.get_text(" ", strip=True))
        self.assertIn(
            "resume_igor_simbirtsev(RUS).pdf",
            russian_document.select_one("a[download]")["href"],
        )

    def test_missing_resume_hides_download_actions(self):
        with patch("core.context_processors.finders.find", return_value=None):
            response = self.client.get(reverse("core:main"))

        document = BeautifulSoup(response.content, "html.parser")
        self.assertEqual(document.select("a[download]"), [])

    def test_homepage_uses_approved_section_order(self):
        content = self.response.content.decode()
        markers = [
            'data-home-section="hero"',
            'id="work"',
            "02 / Working with AI",
            'id="blog"',
            'id="about"',
            'id="contact"',
        ]

        positions = [content.index(marker) for marker in markers]

        self.assertEqual(positions, sorted(positions))

    def test_homepage_uses_approved_metrics_and_featured_article_cards(self):
        for number in range(3):
            Post.objects.create(
                title=f"Featured article {number}",
                slug=f"featured-article-{number}",
                markdown_body=f"Featured body {number}",
                status=Post.Status.PUBLISHED,
                is_featured=True,
                feature_priority=number,
            )

        response = self.client.get(reverse("core:main"))
        document = BeautifulSoup(response.content, "html.parser")
        cards = document.select("a.homepage-case-card")

        self.assertEqual(len(cards), 3)
        self.assertContains(response, "10M+")
        self.assertContains(response, "~3.6 TB")
        self.assertContains(response, "~15")
        self.assertEqual(
            [card.select_one("h3").get_text(strip=True) for card in cards],
            [f"Featured article {number}" for number in range(3)],
        )
        self.assertTrue(all(card["href"].startswith("/blog/") for card in cards))

    def test_homepage_has_no_placeholder_or_dead_links(self):
        content = self.response.content.decode()

        self.assertNotIn("I Wanted a Flexible SQL Agent", content)
        self.assertNotIn('href="#"', content)

    def test_homepage_uses_email_contact_without_form(self):
        document = BeautifulSoup(self.response.content, "html.parser")
        contact = document.select_one("#contact")

        self.assertIsNotNone(contact)
        self.assertIsNone(contact.find("form"))
        self.assertEqual(
            contact.select_one('a[href^="mailto:"]')["href"],
            "mailto:igor.simbirtsev@gmail.com",
        )

    def test_homepage_core_copy_is_translated_to_russian(self):
        response = self.client.get("/ru/")

        self.assertContains(response, "Старший backend- и data-инженер")
        self.assertContains(response, "Избранные статьи")
        self.assertContains(response, "Как я работаю с агентами для программирования")
        self.assertContains(response, "Последние статьи")
        self.assertContains(response, "Если мой опыт подходит вашей команде")

    def test_homepage_rejects_contact_form_posts(self):
        response = self.client.post(reverse("core:main"), {"message": "Hello"})

        self.assertEqual(response.status_code, 405)

    def test_homepage_renders_zero_to_three_latest_article_rows(self):
        for post_count in range(5):
            with self.subTest(post_count=post_count):
                Post.objects.all().delete()
                for number in range(post_count):
                    Post.objects.create(
                        title=f"Database article {number}",
                        slug=f"database-article-{post_count}-{number}",
                        markdown_body=f"Article body {number}",
                        status=Post.Status.PUBLISHED,
                    )

                response = self.client.get(reverse("core:main"))
                document = BeautifulSoup(response.content, "html.parser")

                self.assertEqual(len(document.select('#blog a[href^="/blog/"]')), min(post_count, 3))

    def test_homepage_featured_cards_and_latest_rows_do_not_duplicate_posts(self):
        latest_post = Post.objects.create(
            title="Latest article",
            slug="latest-article",
            markdown_body="Fallback body text for the automatic excerpt.",
            tags="Django, Data",
            status=Post.Status.PUBLISHED,
        )
        lower_priority = Post.objects.create(
            title="Lower priority",
            slug="lower-priority",
            markdown_body="Ignored fallback body.",
            summary="Explicit summary copy.",
            status=Post.Status.PUBLISHED,
            is_featured=True,
            feature_priority=2,
        )
        higher_priority = Post.objects.create(
            title="Higher priority",
            slug="higher-priority",
            markdown_body="Higher priority body.",
            status=Post.Status.PUBLISHED,
            is_featured=True,
            feature_priority=1,
        )

        response = self.client.get(reverse("core:main"))
        document = BeautifulSoup(response.content, "html.parser")
        cards = document.select("a.homepage-case-card")
        rows = document.select('#blog a[href^="/blog/"]')

        self.assertEqual(
            [card.select_one("h3").get_text(strip=True) for card in cards],
            [higher_priority.title, lower_priority.title],
        )
        self.assertEqual(
            [row.select_one(".text-2xl").get_text(strip=True) for row in rows],
            [latest_post.title],
        )
        self.assertContains(response, "Explicit summary copy.")
        self.assertContains(response, "Fallback body text for the automatic excerpt.")
        self.assertContains(response, "Django / Data")

    def test_homepage_marks_article_data_as_english_and_wrap_safe(self):
        long_title = "T" * 200
        long_tag = "G" * 255
        Post.objects.create(
            title=long_title,
            slug="long-featured-article",
            markdown_body="Featured summary body.",
            tags=long_tag,
            status=Post.Status.PUBLISHED,
            is_featured=True,
        )
        Post.objects.create(
            title="Latest English article",
            slug="latest-english-article",
            markdown_body="Latest summary body.",
            tags="Data",
            status=Post.Status.PUBLISHED,
        )

        response = self.client.get("/ru/")
        document = BeautifulSoup(response.content, "html.parser")
        featured_card = document.select_one("a.homepage-case-card")
        latest_row = document.select_one('#blog a[href="/blog/latest-english-article/"]')

        for element in (
            featured_card.select_one("h3"),
            featured_card.select_one("p"),
            featured_card.select_one(".article-tag"),
            latest_row.select_one(".article-data-text"),
            latest_row.select_one(".article-tag"),
        ):
            self.assertEqual(element["lang"], "en")
        self.assertIn("article-data-text", featured_card.select_one("h3")["class"])
        self.assertIn("article-tag", featured_card.select_one(".article-tag")["class"])


class RobotsTxtTests(TestCase):
    def test_robots_txt_allows_public_pages_and_advertises_sitemap(self):
        response = self.client.get(reverse("robots_txt"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Content-Type"], "text/plain")
        self.assertContains(response, "User-agent: *")
        self.assertContains(response, "Allow: /")
        self.assertContains(response, "Disallow: /blog/write/")
        self.assertContains(response, "Disallow: /en/accounts/")
        self.assertContains(response, "Disallow: /ru/accounts/")
        self.assertContains(response, "Sitemap: https://igorsimb.ru/sitemap.xml")
