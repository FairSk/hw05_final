from django.test import TestCase, Client
from django.test import TestCase
from django.urls import reverse

from ..models import Group, Post, User

SLUG = 'group-slug'
USERNAME = 'Author'
INDEX_URL = reverse('posts:index')
CREATE_URL = reverse('posts:post_create')
GROUP_POST_URL = reverse('posts:group_posts', args=[SLUG])
PROFILE_ULR = reverse('posts:profile', args=[USERNAME])


class FormsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовое описание',
            slug=SLUG
        )
        cls.another_group = Group.objects.create(
            title='Другой тестовый заголовок',
            description='Другое тестовое описание',
            slug='another-group-slug'
        )
        cls.author = User.objects.create(username=USERNAME)
        cls.no_author = User.objects.create(username='NotAuthor')
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=FormsTest.author,
            group=FormsTest.group
        )
        cls.EDIT_URL = reverse('posts:post_edit', args=[FormsTest.post.id])
        cls.DETAIL_URL = reverse('posts:post_detail', args=[FormsTest.post.id])

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.not_author = Client()
        self.authorized_client.force_login(self.author)
        self.not_author.force_login(self.no_author)

    def test_create_post_form(self):
        form_data = {
            'text': 'Текст для нового поста',
            'group': self.group.id
        }
        before_creating = set(Post.objects.all())
        response = self.authorized_client.post(CREATE_URL,
                                               data=form_data, follow=True)
        after_creating = set(Post.objects.all())
        differences_of_sets = after_creating.difference(before_creating)
        self.assertEqual(len(differences_of_sets), 1)
        post = differences_of_sets.pop()
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.author)
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, PROFILE_ULR)

    def test_edit_post_form(self):
        form_data = {
            'text': 'Текст для измененного поста',
            'group': self.another_group.id
        }
        response = self.authorized_client.post(self.EDIT_URL,
                                               data=form_data, follow=True)
        post = Post.objects.get(id=self.post.id)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.group.id, form_data['group'])
        self.assertRedirects(response, self.DETAIL_URL)
