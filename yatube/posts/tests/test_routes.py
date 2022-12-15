from django.test import TestCase
from django.urls import reverse

SLUG = 'group-slug'
USERNAME = 'Author'
POST_ID = 1
PATHS = [
    ('posts:index', '/', None),
    ('posts:post_create', '/create/', None),
    ('posts:group_posts', f'/group/{SLUG}/', [SLUG]),
    ('posts:profile', f'/profile/{USERNAME}/', [USERNAME]),
    ('posts:post_edit', f'/posts/{POST_ID}/edit/', [POST_ID]),
    ('posts:post_detail', f'/posts/{POST_ID}/', [POST_ID]),
    ('posts:add_comment', f'/posts/{POST_ID}/comment/', [POST_ID]),
    ('posts:follow_index', '/follow/', None),
    ('posts:profile_follow', f'/profile/{USERNAME}/follow/', [USERNAME]),
    ('posts:profile_unfollow', f'/profile/{USERNAME}/unfollow/', [USERNAME])
]


class RoutesTests(TestCase):
    def test_routes(self):
        for url, path, args in PATHS:
            with self.subTest(path=path):
                response = reverse(url, args=args)
                self.assertEqual(response, path)
