from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache


from ..models import Group, Post, User

SLUG = 'group-slug'
USERNAME = 'Author'
INDEX_URL = reverse('posts:index')
CREATE_URL = reverse('posts:post_create')
GROUP_POST_URL = reverse('posts:group_posts', args=[SLUG])
PROFILE_ULR = reverse('posts:profile', args=[USERNAME])
LOGIN_URL = reverse('users:login')
CREATE_FOR_GUESTS_URL = f"{LOGIN_URL}?next={CREATE_URL}"
FOLLOW_INDEX_URL = reverse('posts:follow_index')
PROFILE_FOLLOW_URL = reverse('posts:profile_follow', args=[USERNAME])
PROFILE_UNFOLLOW_URL = reverse('posts:profile_unfollow', args=[USERNAME])
FOLLOW_INDEX_GUESTS_URL = f"{LOGIN_URL}?next={FOLLOW_INDEX_URL}"
PROFILE_FOLLOW_GUESTS_URL = f"{LOGIN_URL}?next={PROFILE_FOLLOW_URL}"
PROFILE_UNFOLLOW_GUESTS_URL = f"{LOGIN_URL}?next={PROFILE_UNFOLLOW_URL}"


class URLSTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author_user = User.objects.create(username=USERNAME)
        cls.no_author = User.objects.create(username='NotAuthor')
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.author_user
        )
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовое описание',
            slug='group-slug'
        )
        cls.EDIT_URL = reverse('posts:post_edit', args=[URLSTests.post.id])
        cls.DETAIL_URL = reverse('posts:post_detail', args=[URLSTests.post.id])
        cls.DETAIL_FOR_GUESTS_URL = (f"{LOGIN_URL}?next={cls.EDIT_URL}")
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.not_author = Client()
        cls.authorized_client.force_login(URLSTests.author_user)
        cls.not_author.force_login(URLSTests.no_author)

    def setUp(self):
        cache.clear()

    def test_pages_access(self):
        ACCESSES = [
            (INDEX_URL, self.guest_client, 200),
            (GROUP_POST_URL, self.guest_client, 200),
            (PROFILE_ULR, self.guest_client, 200),
            (self.DETAIL_URL, self.guest_client, 200),
            (CREATE_URL, self.guest_client, 302),
            (self.EDIT_URL, self.guest_client, 302),
            (PROFILE_FOLLOW_URL, self.guest_client, 302),
            (PROFILE_UNFOLLOW_URL, self.guest_client, 302),
            (FOLLOW_INDEX_URL, self.guest_client, 302),
            (CREATE_URL, self.authorized_client, 200),
            (self.EDIT_URL, self.authorized_client, 200),
            (FOLLOW_INDEX_URL, self.authorized_client, 200),
            ('/404/', self.authorized_client, 404),
            (PROFILE_FOLLOW_URL, self.not_author, 302),
            (PROFILE_UNFOLLOW_URL, self.not_author, 302),
            (FOLLOW_INDEX_URL, self.not_author, 200),
            (self.EDIT_URL, self.not_author, 302)
        ]
        for url, user, expected_code in ACCESSES:
            with self.subTest(url=url, user=user):
                self.assertEqual(user.get(url).status_code, expected_code)

    def test_redirects(self):
        REDIRECTS = [
            (PROFILE_FOLLOW_URL, self.not_author, PROFILE_ULR),
            (PROFILE_UNFOLLOW_URL, self.not_author, PROFILE_ULR),
            (self.EDIT_URL, self.not_author, self.DETAIL_URL),
            (CREATE_URL, self.guest_client, CREATE_FOR_GUESTS_URL),
            (self.EDIT_URL, self.guest_client, self.DETAIL_FOR_GUESTS_URL),
            (FOLLOW_INDEX_URL, self.guest_client, FOLLOW_INDEX_GUESTS_URL),
            (PROFILE_FOLLOW_URL, self.guest_client, PROFILE_FOLLOW_GUESTS_URL),
            (PROFILE_UNFOLLOW_URL, self.guest_client,
             PROFILE_UNFOLLOW_GUESTS_URL),
            (PROFILE_FOLLOW_URL, self.authorized_client, PROFILE_ULR),
        ]
        for url, client, redirect_page in REDIRECTS:
            with self.subTest(url=url, client=client):
                self.assertRedirects(client.get(url), redirect_page)

    def test_templates(self):
        TEMPLATES = {
            INDEX_URL: 'posts/index.html',
            GROUP_POST_URL: 'posts/group_list.html',
            PROFILE_ULR: 'posts/profile.html',
            CREATE_URL: 'posts/post_create.html',
            self.DETAIL_URL: 'posts/post_detail.html',
            self.EDIT_URL: 'posts/post_create.html',
            FOLLOW_INDEX_URL: 'posts/follow.html'
        }
        for url, expected_template in TEMPLATES.items():
            with self.subTest(url=url):
                self.assertTemplateUsed(self.authorized_client.get(url),
                                        expected_template)
