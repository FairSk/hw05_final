from django.test import TestCase, Client


class CoreTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_templates(self):
        TEMPLATES = {
            'error/404/': 'core/404.html',
            'error/403/': 'core/404.html',
            'error/500/': 'core/404.html'
        }
        for request, expected_template in TEMPLATES.items():
            with self.subTest(request=request):
                self.assertTemplateUsed(self.guest_client.get(request),
                                        expected_template)
