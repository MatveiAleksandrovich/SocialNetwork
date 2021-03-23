from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ..forms import PostForm
from ..models import Post, Group, User


USERNAME_1 = 'testname'


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User = get_user_model()

        cls.user = User.objects.create(username=USERNAME_1)

        cls.post = Post.objects.create(
            text='1'*10,
            author=PostModelTest.user,
            pub_date='2020-12-12'
        )

    def test_verbose_name(self):
        post = PostModelTest.post
        verbose_text = post._meta.get_field('text').verbose_name
        self.assertEqual(verbose_text, 'Текст')
        verbose_group = post._meta.get_field('group').verbose_name
        self.assertEqual(verbose_group, 'Группа')

    def test_help_text(self):
        post = PostModelTest.post
        help_text_text = post._meta.get_field('text').help_text
        self.assertEqual(
            help_text_text, 'Это поле обязательно, пожалуйста заполните его.'
        )
        help_text_group = post._meta.get_field('group').help_text
        self.assertEqual(
            help_text_group, 
            'Это поле необязательно, но оно может помочь Вам'
            ' найти единомышленников.'
        )

    def test_str(self):
        post = PostModelTest.post
        if len(post.text) > 15:
            expected_object_name = post.text[:15] + '..'
        else:
            expected_object_name = post.text
        self.assertEqual(expected_object_name, str(post))


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.group = Group.objects.create(
            title='Это тестовая группа',
            slug='testgroup',
            description='Надеюсь тесты пройдутся с первого раза'
        )

    def test_str(self):
        group = GroupModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))
