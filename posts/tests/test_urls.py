from django.contrib.auth import get_user_model
from django.forms.widgets import Select
from django.http import response
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Group, Post, User


INDEX_URL = reverse('index')
USERNAME_1 = 'testname1'
USERNAME_2 = 'username'
SLUG = 'testgroup'
GROUP_URL = reverse('group_posts', args=[SLUG])
NEW_POST_URL = reverse('new_post')
PROFILE_URL = reverse('profile', args=[USERNAME_2])
ABOUT_AUTHOR_URL = '/about/author'
ABOUT_TECH_URL = '/about/tech'
NOT_EXISTED_URL = '/abracadabra/'

class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_homepage(self):
        response = self.guest_client.get(INDEX_URL)
        self.assertEqual(response.status_code, 200)

    def test_author(self):
        response = self.guest_client.get(ABOUT_AUTHOR_URL)
        self.assertEqual(response.status_code, 301)

    def test_technologies(self):
        response = self.guest_client.get(ABOUT_TECH_URL)
        self.assertEqual(response.status_code, 301)


class YatubeURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user1 = User.objects.create(username=USERNAME_1)

        cls.post = Post.objects.create(
            text='1'*10,
            author=YatubeURLTests.user1,
            pub_date='2020-12-12',
        )

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug=SLUG,
            description='Эта группа созданна только для теста'
        )

        cls.POST_VIEW_URL = reverse('post', args=[
            USERNAME_1, '1'
        ])

        cls.POST_EDIT_URL = reverse('post_edit', args=[
            USERNAME_1, '1'
        ])

        cls.COMMENT_URL = reverse('add_comment', args=[
            USERNAME_1, '1'
        ])

    def setUp(self):
        User = get_user_model()
        self.guest_client = Client()
        self.user = User.objects.create_user(username=USERNAME_2)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user1)

    def test_guest_leave_comment_redirects_to_login_page(self):
        response = self.guest_client.get(self.COMMENT_URL, follow=True)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_group_url_exists_at_desired_location(self):
        response = self.authorized_client.get(GROUP_URL)
        self.assertEqual(response.status_code, 200)

    def test_new_post_url_exists_at_desired_location(self):
        response = self.authorized_client.get(NEW_POST_URL)
        self.assertEqual(response.status_code, 200)

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            'group.html': GROUP_URL,
            'new_post.html': NEW_POST_URL,
            'index.html': INDEX_URL,
            'new_post.html': self.POST_EDIT_URL
        }
        for template, reverse_name in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_user_url_redirects_at_desired_location(self):
        response = self.authorized_client.get(PROFILE_URL)
        self.assertEqual(response.status_code, 200)

    def test_users_post_url_redirects_at_desired_location(self):
        response = self.authorized_client.get(self.POST_VIEW_URL)
        self.assertEqual(response.status_code, 200)

    def test_anonym_edit_url_redirects_at_desired_location(self):
        response = self.guest_client.get(self.POST_EDIT_URL)
        self.assertEqual(response.status_code, 302)

    def test_guest_user_edit_url_redirects_at_desired_location(self):
        response = self.authorized_client.get(self.POST_EDIT_URL)
        self.assertEqual(response.status_code, 200)

    def test_no_rights_profile_post_edit_template_works_correct(self):
        response = self.guest_client.get(self.POST_EDIT_URL, follow=True)
        self.assertTemplateUsed(response, 'base.html')

    def test_404_if_page_not_found(self):
        response = self.guest_client.get(NOT_EXISTED_URL)
        self.assertEqual(response.status_code, 404)
