import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse


from ..models import Group, Post, User, Comment

LOGIN_URL = reverse('users:login')
SLUG = 'group-slug'
USERNAME = 'Author'
INDEX_URL = reverse('posts:index')
CREATE_URL = reverse('posts:post_create')
GROUP_POST_URL = reverse('posts:group_posts', args=[SLUG])
PROFILE_ULR = reverse('posts:profile', args=[USERNAME])
CREATE_GUEST_URL = f'{LOGIN_URL}?next={CREATE_URL}'

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class FormsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='gif'
        )
        cls.another_uploaded = SimpleUploadedFile(
            name='another_small.gif',
            content=SMALL_GIF,
            content_type='gif'
        )
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
        cls.EDIT_NOT_AUTHOR_URL = f'{LOGIN_URL}?next={cls.EDIT_URL}'
        cls.DETAIL_URL = reverse('posts:post_detail', args=[FormsTest.post.id])
        cls.COMMENT_URL = reverse('posts:add_comment',
                                  args=[FormsTest.post.id])
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.not_author = Client()
        cls.authorized_client.force_login(FormsTest.author)
        cls.not_author.force_login(FormsTest.no_author)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post_form(self):
        form_data = {
            'text': 'Текст для нового поста',
            'group': self.group.id,
            'image': self.uploaded
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
        self.assertEqual(post.image.name, f'posts/{form_data["image"].name}')
        self.assertRedirects(response, PROFILE_ULR)

    def test_edit_post_form(self):
        form_data = {
            'text': 'Текст для измененного поста',
            'group': self.another_group.id,
            'image': self.another_uploaded

        }
        response = self.authorized_client.post(self.EDIT_URL,
                                               data=form_data, follow=True)
        post = Post.objects.get(id=self.post.id)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(post.image.name, f'posts/{form_data["image"].name}')
        self.assertRedirects(response, self.DETAIL_URL)

    def test_create_commment_form(self):
        form_data = {
            'text': 'Текст для комментария'
        }

        before_creating = set(Comment.objects.all())
        response = self.authorized_client.post(self.COMMENT_URL,
                                               data=form_data, follow=True)
        after_creating = set(Comment.objects.all())
        differences_of_sets = after_creating.difference(before_creating)
        self.assertEqual(len(differences_of_sets), 1)
        comment = differences_of_sets.pop()
        self.assertEqual(comment.text, form_data['text'])
        self.assertEqual(comment.author, self.author)
        self.assertEqual(comment.post, self.post)
        self.assertRedirects(response, self.DETAIL_URL)

    def test_guest_add_comment(self):
        form_data = {
            'text': 'Текст для комментария'
        }
        before_creating = set(Comment.objects.all())
        self.guest_client.post(self.COMMENT_URL,
                               data=form_data, follow=True)
        after_creating = set(Comment.objects.all())
        self.assertEqual(after_creating, before_creating)

    def test_guest_create_post_form(self):
        form_data = {
            'text': 'Текст для нового поста',
            'group': self.group.id,
            'image': self.uploaded
        }
        before_creating = set(Post.objects.all())
        response = self.guest_client.post(CREATE_URL,
                                          data=form_data, follow=True)
        after_creating = set(Post.objects.all())
        self.assertEqual(before_creating, after_creating)
        self.assertRedirects(response, CREATE_GUEST_URL)

    def test_not_author_edit_form(self):
        CASES = [
            (self.not_author, self.EDIT_NOT_AUTHOR_URL),
            (self.guest_client, self.EDIT_NOT_AUTHOR_URL)
        ]
        form_data = {
            'text': 'Текст для измененного поста не автором',
            'group': self.another_group.id,
            'image': self.uploaded
        }
        for client, expected_redirect in CASES:
            with self.subTest(client=client):
                response = self.client.post(self.EDIT_URL,
                                            data=form_data, follow=True)
                post = Post.objects.get(id=self.post.id)
                self.assertEqual(post.text, self.post.text)
                self.assertEqual(post.author, self.post.author)
                self.assertEqual(post.group.id, self.post.group.id)
                self.assertRedirects(response, expected_redirect)
