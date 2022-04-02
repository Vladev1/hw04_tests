import shutil
import tempfile

from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.conf import settings

from ..models import Post, Group, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsFormTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title="Заголовок",
            slug="the_group",
            description="Описание"
        )
        cls.post = Post.objects.create(
            text="Текст",
            pub_date='Дата',
            author=User.objects.create_user(username='test_name_2'),
            group=cls.group,
        )
        cls.urls = [
            '/profile/test_name_1/',
            '/group/the_group/',
            '/',
            '/posts/1/',
        ]

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        # Создаем авторизованый клиент
        self.user1 = User.objects.create_user(username='test_name_1')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user1)
        # Создаем автора
        self.user2 = User.objects.get(username='test_name_2')
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.user2)

    def test_form_create_post(self):
        """Форма create действительно создает новый пост и перенаправляет."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст',
            'group': self.group.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': 'test_name_1'}
        ))
        self.assertNotEqual(Post.objects.count(), posts_count)
        self.assertEqual(response.status_code, 200)

    def test_form_edit_post(self):
        """Форма edit правит пост и перенаправляет."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст',
            'group': self.group.pk
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': '1'}),
            data=form_data,
            follow=True,
            instance=Post.objects.get()
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': '1'}
        ))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                group=self.group.id,
                text=self.post.text,
            ).exists()
        )
