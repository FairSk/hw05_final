from django.test import TestCase
from django.urls import reverse
from ..urls import app_name

SLUG = 'group-slug'
USERNAME = 'Author'
POST_ID = 1
PATHS = [
    ('index', '/', None),
    ('post_create', '/create/', None),
    ('group_posts', f'/group/{SLUG}/', [SLUG]),
    ('profile', f'/profile/{USERNAME}/', [USERNAME]),
    ('post_edit', f'/posts/{POST_ID}/edit/', [POST_ID]),
    ('post_detail', f'/posts/{POST_ID}/', [POST_ID]),
    ('add_comment', f'/posts/{POST_ID}/comment/', [POST_ID]),
    ('follow_index', '/follow/', None),
    ('profile_follow', f'/profile/{USERNAME}/follow/', [USERNAME]),
    ('profile_unfollow', f'/profile/{USERNAME}/unfollow/', [USERNAME])
]


class RoutesTests(TestCase):
    def test_routes(self):
        for url, path, args in PATHS:
            with self.subTest(path=path):
                self.assertEqual(reverse(f'{app_name}:{url}', args=args), path)
