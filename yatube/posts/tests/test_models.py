from django.test import TestCase

from ..models import (Post, User, Group, Comment, Follow,
                      OUTPUT_DATA_FOLLOW, OUTPUT_DATA_POST)


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
            (self.post, OUTPUT_DATA_POST.format(
                self.post.text[:15],
                self.post.group,
                self.post.author.username
            )),
            (self.group, self.group.title),
            (self.comment, self.comment.text[:20]),
            (self.subscription, OUTPUT_DATA_FOLLOW.format(
                self.subscription.user.username,
                self.subscription.author.username))
        ]
        for task, expected_output in object_names:
            with self.subTest(task=task):
                self.assertEqual(expected_output, str(task))
