from django.test import TestCase
from django.urls import reverse

SLUG = 'group-slug'
USERNAME = 'Author'
POST_ID = 1
PATHS = [
    ('index', '/', None),
    ('post_create', '/create/', None),
    ('group_posts', f'/group/{SLUG}/', [SLUG]),
    ('profile', f'/profile/{USERNAME}/', [USERNAME]),
    ('post_edit', f'/posts/{POST_ID}/edit/', [POST_ID]),
    ('post_detail', f'/posts/{POST_ID}/', [POST_ID])
]


class RoutesTests(TestCase):
    def test_routes(self):
        for url, path, args in PATHS:
            with self.subTest(path=path):
                response = reverse(f'posts:{url}', args=args)
                self.assertEqual(response, path)
