from django.test import TestCase

from ..models import Post, User, Group, Comment


class ModelTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username="Author")
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=ModelTests.author
        )
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовое описание',
            slug='group-slug'
        )
        cls.comment = Comment.objects.create(
            post=ModelTests.post,
            author=ModelTests.author,
            text='Текст комментария'
        )

    def test_str_function(self):
        object_names = [
            (self.post, self.post.text, 15),
            (self.group, self.group.title, 20),
            (self.comment, self.comment.text, 20)
        ]
        for task, text, cut in object_names:
            with self.subTest(text=text):
                self.assertEqual(text[:cut], str(task))
