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
            (self.post, (f'Text: {self.post.text[:15]}, '
                         f'Group: {self.post.group}, '
                         f'Author: {self.post.author.username}')),
            (self.group, self.group.title),
            (self.comment, self.comment.text[:20]),
            (self.subscription, (f'{self.subscription.user.username} -> '
                                 f'{self.subscription.author.username}'))
        ]
        for task, expected_output in object_names:
            with self.subTest(task=task):
                self.assertEqual(expected_output, str(task))
