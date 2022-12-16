from django.test import TestCase

from ..models import Post, User, Group, Comment, Follow


class ModelTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username="Author")
        cls.another_author = User.objects.create(username="AnotherAuthor")
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
        cls.subscription = Follow.objects.create(
            user=ModelTests.author,
            author=ModelTests.another_author
        )

    def test_str_function(self):
        object_names = [
            (self.post, self.post.text, 15),
            (self.group, self.group.title, None),
            (self.comment, self.comment.text, 20)
        ]
        for task, text, cut in object_names:
            with self.subTest(text=text):
                self.assertEqual(text[:cut], str(task))

    def test_follow_str(self):
        self.assertEqual(str(self.subscription),
                         f'{self.subscription.user.username} -> '
                         f'{self.subscription.author.username}')
