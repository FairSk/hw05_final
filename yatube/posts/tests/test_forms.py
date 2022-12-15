from django.test import TestCase, Client
from django.test import TestCase
from django.urls import reverse

from ..models import Group, Post, User, Comment

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
        cls.COMMENT_URL = reverse('posts:add_comment',
                                  args=[FormsTest.post.id])
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.not_author = Client()
        cls.authorized_client.force_login(FormsTest.author)
        cls.not_author.force_login(FormsTest.no_author)

    def test_create_post_form(self):
        form_data = {
            'text': 'Текст для нового поста',
            'group': self.group.id,
            # без понятия как сюда передать картинку
            'image': ''
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
        self.assertEqual(post.image, form_data['image'])
        self.assertRedirects(response, PROFILE_ULR)

    def test_edit_post_form(self):
        form_data = {
            'text': 'Текст для измененного поста',
            'group': self.another_group.id,
            'image': ''
        }
        response = self.authorized_client.post(self.EDIT_URL,
                                               data=form_data, follow=True)
        post = Post.objects.get(id=self.post.id)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(post.image, form_data['image'])
        self.assertRedirects(response, self.DETAIL_URL)

    def test_create_commment_form(self):
        form_data = {
            'text': 'Текст для комментария'
        }

        before_creating = set(Comment.objects.all())
        self.authorized_client.post(self.COMMENT_URL,
                                    data=form_data, follow=True)
        after_creating = set(Comment.objects.all())
        differences_of_sets = after_creating.difference(before_creating)
        self.assertEqual(len(differences_of_sets), 1)
        comment = differences_of_sets.pop()
        self.assertEqual(comment.text, form_data['text'])

    def test_guest_add_comment(self):
        form_data = {
            'text': 'Текст для комментария'
        }
        before_creating = set(Comment.objects.all())
        self.guest_client.post(self.COMMENT_URL,
                               data=form_data, follow=True)
        after_creating = set(Comment.objects.all())
        differences_of_sets = after_creating.difference(before_creating)
        self.assertEqual(len(differences_of_sets), 0)

    def test_create_post_form(self):
        form_data = {
            'text': 'Текст для нового поста',
            'group': self.group.id,
            'image': ''
        }
        before_creating = set(Post.objects.all())
        self.guest_client.post(CREATE_URL,
                               data=form_data, follow=True)
        after_creating = set(Post.objects.all())
        differences_of_sets = after_creating.difference(before_creating)
        self.assertEqual(len(differences_of_sets), 0)

    def test_not_author_edit_form(self):
        form_data = {
            'text': 'Текст для измененного поста не автором',
            'group': self.group.id
        }
        self.not_author.post(self.EDIT_URL,
                             data=form_data, follow=True)
        post = Post.objects.get(id=self.post.id)
        self.assertNotEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.group.id, form_data['group'])

    def test_guest_edit_form(self):
        form_data = {
            'text': 'Текст для измененного поста не автором',
            'group': self.group.id
        }
        self.guest_client.post(self.EDIT_URL,
                               data=form_data, follow=True)
        post = Post.objects.get(id=self.post.id)
        self.assertNotEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.group.id, form_data['group'])
