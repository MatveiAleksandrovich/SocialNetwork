from os import terminal_size
import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import response
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from posts.forms import PostForm
from posts.models import Post, Group, User


USERNAME_1 = 'testname'
NEW_POST_URL = reverse('new_post')
INDEX_URL = reverse('index')
SMALL_GIF = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
                b'\x01\x00\x80\x00\x00\x00\x00\x00'
                b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                b'\x0A\x00\x3B'
        )


class PostCreationForm(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        User = get_user_model()

        cls.user = User.objects.create(username=USERNAME_1)

        cls.post = Post.objects.create(
            text='Correct this tekst',
            author=cls.user,
        )
        cls.POST_VIEW_URL = reverse(
            'post_edit', args=[USERNAME_1, '1'])

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        super().setUp()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Заголовок'
        }
        response = self.authorized_client.post(
            NEW_POST_URL,
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, INDEX_URL)
        self.assertEqual(Post.objects.count(), posts_count+1)

    def test_edit_post(self):
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        form_data = {
            'text': 'correct text!',
            'post_id': 1,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            self.POST_VIEW_URL,
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, '/testname/1/')
        self.assertTrue(Post.objects.filter(id='1').exists())
        self.assertEqual(Post.objects.first().text, form_data['text'])
        self.assertTrue(Post.objects.filter(image='posts/small.gif').exists())
