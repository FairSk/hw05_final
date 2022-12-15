from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache
from django.core.paginator import Page

from ..models import Group, Post, User, Follow

SLUG = 'group-slug'
ANOTHER_SLUG = 'another-group-slug'
USERNAME = 'Author'
INDEX_URL = reverse('posts:index')
INDEX_PAGE_2_URL = reverse('posts:index') + '?page=2'
CREATE_URL = reverse('posts:post_create')
GROUP_POST_URL = reverse('posts:group_posts', args=[SLUG])
GROUP_POST_PAGE_2_URL = reverse('posts:group_posts', args=[SLUG]) + '?page=2'
PROFILE_ULR = reverse('posts:profile', args=[USERNAME])
PROFILE_PAGE_2_ULR = reverse('posts:profile', args=[USERNAME]) + '?page=2'
ANOTHER_GROUP_POST_URL = reverse('posts:group_posts', args=[ANOTHER_SLUG])

ANOTHER_USERNAME = 'Pupsen'
ABSOLUTE_ANOTHER_USER = 'Vupsen'
PROFILE_FOLLOW_URL = reverse('posts:profile_follow', args=[USERNAME])
ANOTHER_PROFILE_FOLLOW_URL = reverse('posts:profile_follow',
                                     args=[ANOTHER_USERNAME])
ABSOLUTE_ANOTHER_PROFILE_FOLLOW_URL = reverse('posts:profile_follow',
                                              args=[ABSOLUTE_ANOTHER_USER])
ABSOLUTE_ANOTHER_PROFILE_UNFOLLOW_URL = reverse('posts:profile_unfollow',
                                                args=[ABSOLUTE_ANOTHER_USER])
FOLLOW_INDEX_URL = reverse('posts:follow_index')


class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username=USERNAME)
        cls.another_author = User.objects.create(username=ANOTHER_USERNAME)
        cls.absolute_another_author = User.objects.create(
            username=ABSOLUTE_ANOTHER_USER)
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовое описание',
            slug=SLUG
        )
        cls.another_group = Group.objects.create(
            title='Другой тестовый заголовок',
            description='Другое тестовое описание',
            slug=ANOTHER_SLUG
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=FollowTest.author,
            group=FollowTest.group
        )
        cls.another_post = Post.objects.create(
            text='Тестовый текст',
            author=FollowTest.another_author,
            group=FollowTest.group
        )
        Follow.objects.create(
            user=FollowTest.author, author=FollowTest.another_author
        )
        cls.EDIT_URL = reverse('posts:post_edit', args=[FollowTest.post.id])
        cls.DETAIL_URL = reverse('posts:post_detail',
                                 args=[FollowTest.post.id])
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(FollowTest.author)

    def setUp(self):
        cache.clear()

    def test_following_ability(self):
        self.authorized_client.get(ABSOLUTE_ANOTHER_PROFILE_FOLLOW_URL)
        subscription = Follow.objects.filter(
            user=self.author, author=self.absolute_another_author).exists()
        self.assertTrue(subscription)

    def test_unfollowing_ability(self):
        self.authorized_client.get(ABSOLUTE_ANOTHER_PROFILE_UNFOLLOW_URL)
        subscription = Follow.objects.filter(
            user=self.author, author=self.absolute_another_author).exists()
        self.assertFalse(subscription)

    def test_following_unability_on_yourself(self):
        follow_obj_before_follow = list(Follow.objects.all())
        self.authorized_client.get(PROFILE_FOLLOW_URL)
        follow_obj_after_follow = list(Follow.objects.all())
        self.assertEqual(follow_obj_before_follow, follow_obj_after_follow)

    def test_follow_only_one_time(self):
        self.authorized_client.get(ABSOLUTE_ANOTHER_PROFILE_FOLLOW_URL)
        follow_obj_before_follow = list(Follow.objects.all())
        self.authorized_client.get(ABSOLUTE_ANOTHER_PROFILE_FOLLOW_URL)
        follow_obj_after_follow = list(Follow.objects.all())
        self.assertEqual(follow_obj_before_follow, follow_obj_after_follow)

    def test_follow_context(self):
        response = self.authorized_client.get(FOLLOW_INDEX_URL)
        self.assertIsInstance(response.context['page_obj'], Page)
