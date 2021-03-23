from os import terminal_size

from django.db.models.aggregates import Count
from posts.views import new_post
import shutil
import tempfile
import json

from datetime import datetime
from typing import Text
from django.contrib.auth import get_user_model
from django.forms.fields import SlugField
from django.http import request, response
from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from ..models import Post, Group, User, Follow
from posts.forms import PostForm


USERNAME_1 = 'Mihail'
USERNAME_2 = 'Paginator'
USERNAME_3 = 'TestUser'
USERNAME_4 = 'Subscriber'
INDEX_URL = reverse('index')
INDEX_PAGE_2_URL = reverse('index') + ('?page=2')
SLUG_0 = 'test-slug'
SLUG_1 = 'test-slug_1'
SLUG_2 = 'slug'
GROUP_0_URL = reverse('group_posts', args=[SLUG_0])
GROUP_1_URL = reverse('group_posts', args=[SLUG_1])
GROUP_2_URL = reverse('group_posts', args=[SLUG_2])
NEW_POST_URL = reverse('new_post')
PROFILE_URL = reverse('profile', args=[USERNAME_1])
PROFILE_URL_1 = reverse('profile', args=[USERNAME_3])
PROFILE_FOLLOW_URL = reverse('profile_follow', args=[
            USERNAME_4
        ])
PROFILE_UNFOLLOW_URL = reverse('profile_unfollow', args=[
    USERNAME_4
])
FOLLOW_URL = reverse('follow_index')
SMALL_GIF = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
                         b'\x01\x00\x80\x00\x00\x00\x00\x00'
                         b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                         b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                         b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                         b'\x0A\x00\x3B'
                         )


class PostPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User = get_user_model()

        cls.user = User.objects.create(username=USERNAME_1)
        cls.user_0 = User.objects.create(username=USERNAME_4)

        cls.group_0 = Group.objects.create(
            title='Заголовок',
            description='Текст',
            slug=SLUG_0,
        )

        cls.post = Post.objects.create(
            text='Test text',
            author=PostPagesTest.user,
            group=cls.group_0,
            pub_date=datetime.now,
        )

        cls.group_1 = Group.objects.create(
            title='Заголовок2',
            description='Текст',
            slug=SLUG_1,
        )

        cls.post_0 = Post.objects.create(
            text='Test text 0',
            author=PostPagesTest.user,
            group=cls.group_1,
            pub_date=datetime.now,
        )

        cls.POST_VIEW_URL = reverse('post', args=[
            USERNAME_1, '1'
        ])

        cls.POST_EDIT_URL = reverse('post_edit', args=[
            USERNAME_1, '1'
        ])

    def setUp(self):
        super().setUp()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.subscriber_client = Client()
        self.subscriber_client.force_login(self.user_0)

    def test_post_pages_uses_correct_template(self):
        template_pages_names = {
            'group.html': GROUP_0_URL,
            'index.html': INDEX_URL,
            'new_post.html': NEW_POST_URL,
        }
        for template, reverse_name in template_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_new_post_page_show_correct_context_index(self):
        response = self.authorized_client.get(NEW_POST_URL)
        form_fields = {
            'text': forms.CharField,
            'group': forms.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_group_page_show_correct_context(self):
        response = self.authorized_client.get(GROUP_0_URL)
        self.assertEqual(response.context.get('group').title, 'Заголовок')
        self.assertEqual(response.context.get('group').description, 'Текст')
        self.assertEqual(response.context.get('group').slug, 'test-slug')

    def test_index_page_show_correct_context(self):
        response = self.authorized_client.get(INDEX_URL)
        post_text_0 = response.context.get('page')[1].text
        post_author_0 = response.context.get('page')[1].author.username
        self.assertEqual(post_text_0, 'Test text')
        self.assertEqual(post_author_0, 'Mihail')

    def test_post_added_in_the_right_group(self):
        response_1 = self.authorized_client.get(INDEX_URL)
        response_2 = self.authorized_client.get(GROUP_1_URL)
        post_in_first_group = response_1.context.get('posts')
        post_in_second_group = response_2.context.get('posts')
        self.assertNotEqual(post_in_first_group, post_in_second_group)

    def test_edit_page_show_correct_fields_context(self):
        response = self.authorized_client.get(self.POST_EDIT_URL)
        form_fields = {
            'text': forms.CharField,
            'group': forms.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_profile_page_show_correct_context(self):
        response = self.authorized_client.get(PROFILE_URL)
        posts_count = response.context.get('posts_count')
        author = response.context.get('author').username
        self.assertEqual(author, 'Mihail')
        self.assertEqual(posts_count, 2)

    def test_post_view_page_show_correct_context(self):
        response = self.authorized_client.get(self.POST_VIEW_URL)
        text = response.context.get('post_id')
        posts_count = response.context.get('posts_count')
        author = response.context.get('author').username
        post = response.context.get('post').text
        self.assertEqual(text, 1)
        self.assertEqual(posts_count, 2)
        self.assertEqual(author, 'Mihail')
        self.assertEqual(post, 'Test text')

    def test_cache_works_correctly(self):
        request_1 = self.authorized_client.get(INDEX_URL)
        Post.objects.create(
            text='Cache works!',
            author=PostPagesTest.user,
            pub_date=datetime.now,
        )
        request_2 = self.authorized_client.get(INDEX_URL)
        self.assertHTMLEqual(
            str(request_1.content), 
            str(request_2.content)
            )
        
    def test_authorizied_user_can_subscribe(self):
        amount_subsrcibers_0 = Follow.objects.filter().aggregate(Count('user'))
        self.authorized_client.get(PROFILE_FOLLOW_URL)
        amount_subsrcibers_1 = Follow.objects.filter().aggregate(Count('user'))
        self.authorized_client.get(PROFILE_UNFOLLOW_URL)
        amount_subsrcibers_3 = Follow.objects.filter().aggregate(Count('user'))
        self.assertNotEqual(amount_subsrcibers_0, amount_subsrcibers_1)
        self.assertEqual(amount_subsrcibers_0, amount_subsrcibers_3)

    def test_new_post_dont_show_to_unsubscribed_and_vice_versa(self):
        self.authorized_client.get(PROFILE_FOLLOW_URL)
        new_post = Post.objects.create(
            text='test text',
            author=User.objects.create(
                username='onemoretestuser'
            )
        )
        response = self.authorized_client.get(FOLLOW_URL)
        expected_post = new_post
        actual_post = response.context.get('page')
        self.assertNotEqual(actual_post, expected_post)



class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = get_user_model().objects.create(username=USERNAME_2)

        cls.post = Post.objects.create(
            text='Test 1',
            author=PaginatorViewsTest.user,
            pub_date=datetime.now,
        )
        cls.post = Post.objects.create(
            text='Test 2',
            author=PaginatorViewsTest.user,
            pub_date=datetime.now,
        )
        cls.post = Post.objects.create(
            text='Test 3',
            author=PaginatorViewsTest.user,
            pub_date=datetime.now,
        )
        cls.post = Post.objects.create(
            text='Test 4',
            author=PaginatorViewsTest.user,
            pub_date=datetime.now,
        )
        cls.post = Post.objects.create(
            text='Test 5',
            author=PaginatorViewsTest.user,
            pub_date=datetime.now,
            id=5,
        )
        cls.post = Post.objects.create(
            text='Test 6',
            author=PaginatorViewsTest.user,
            pub_date=datetime.now,
        )
        cls.post = Post.objects.create(
            text='Test 7',
            author=PaginatorViewsTest.user,
            pub_date=datetime.now,
        )
        cls.post = Post.objects.create(
            text='Test 8',
            author=PaginatorViewsTest.user,
            pub_date=datetime.now,
        )
        cls.post = Post.objects.create(
            text='Test 9',
            author=PaginatorViewsTest.user,
            pub_date=datetime.now,
        )
        cls.post = Post.objects.create(
            text='Test 10',
            author=PaginatorViewsTest.user,
            pub_date=datetime.now,
        )
        cls.post = Post.objects.create(
            text='Test 11',
            author=PaginatorViewsTest.user,
            pub_date=datetime.now,
        )
        cls.post = Post.objects.create(
            text='Test 12',
            author=PaginatorViewsTest.user,
            pub_date=datetime.now,
        )
        cls.post = Post.objects.create(
            text='Test 13',
            author=PaginatorViewsTest.user,
            pub_date=datetime.now,
        )

    def setUp(self):
        super().setUp()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_containse_ten_records(self):
        response = self.client.get(INDEX_URL) 
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_second_page_containse_three_records(self):
        response = self.client.get(INDEX_PAGE_2_URL)
        self.assertEqual(len(response.context.get('page').object_list), 3)


class PostImageTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )

        cls.user = get_user_model().objects.create(username=USERNAME_3)

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug=SLUG_2,
        )
        Post.objects.create(text='Тестовая запись',
                            group=cls.group,
                            id=0,
                            author=cls.user,
                            image=cls.uploaded)

        cls.POST_VIEW_0_URL = reverse('post', args=[
            USERNAME_3, '0'
        ])                 

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()

    def test_index_page_context(self):
        response = self.guest_client.get(INDEX_URL)
        expected_data = {
            'Тестовая запись': response.context.get('page')[0].text,
            'Тестовая группа': response.context.get('page')[0].group.title,
            'TestUser': response.context.get('page')[0].author.username,
            'posts/small.gif': response.context.get('page')[0].image
        }
        for value, expected in expected_data.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected)

    def test_profile_page_context(self):
        response = self.guest_client.get(PROFILE_URL_1)
        value = response.context.get('page')[0].image
        expected = ('posts/small.gif')
        self.assertEqual(value, expected)

    def test_group_page_context(self):
        response = self.guest_client.get(GROUP_2_URL)
        value = response.context.get('posts')[0].image
        expected = 'posts/small.gif'
        self.assertEqual(value, expected)

    def test_post_page_context(self):
        response =self.guest_client.get(self.POST_VIEW_0_URL)
        value = response.context.get('post').image
        expected = 'posts/small.gif'
        self.assertEqual(value, expected)
