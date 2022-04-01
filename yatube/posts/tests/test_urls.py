from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus

from ..models import Post, Group

User = get_user_model()


class StaticURLTests(TestCase):
    def test_homepage(self):
        guest_client = Client()
        response = guest_client.get('/')
        self.assertEqual(response.status_code, 200)


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title="Заголовок тестовой задачи",
            slug="the_group",
        )
        cls.post = Post.objects.create(
            text="Описание тестового поста",
            author=User.objects.create_user(username='test_name_2'),
        )
        cls.urls = [
            '/profile/test_name_1/',
            '/group/the_group/',
            '/',
            '/posts/1/',
        ]

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем авторизованый клиент
        self.user1 = User.objects.create_user(username='test_name_1')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user1)
        # Создаем автора
        self.user2 = User.objects.get(username='test_name_2')
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.user2)

    def test_pages_urls_for_guest_users(self):
        """Тест доступности страниц guest пользователям"""
        for address in PostsURLTests.urls:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_urls_for_auth_users(self):
        """Тест доступности страниц auth пользователям"""
        for address in PostsURLTests.urls:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_url_for_auth_users(self):
        """Тест доступности create auth пользователям"""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_page_for_auth_users(self):
        """Тест доступности unexisting auth пользователям"""
        response = self.authorized_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_unexisting_page_for_guest_users(self):
        """Тест доступности unexisting guest пользователям"""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_edit(self):
        """Тест доступности редактирования Автору поста"""
        response = self.authorized_client_author.get('/posts/1/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    # Проверяем редиректы для неавторизованного пользователя

    def test_create_url_redirect_anonymous_on_auth_login(self):
        """Страница по адресу /create/ перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_edit_url_redirect_anonymous_on_posts_login(self):
        """Страница по адресу /posts/1/edit/ перенаправит анонимного
        пользователя на страницу поста.
        """
        response = self.guest_client.get('/posts/1/edit/', follow=True)
        self.assertRedirects(response, ('/auth/login/?next=/posts/1/edit/'))

    # Проверяем редиректы для аторизованного пользователя
    def test_edit_url_redirect_auth_not_author_on_posts_login(self):
        """Страница по адресу /posts/1/edit/ перенаправит
        не автора поста на страницу поста.
        """
        response = self.authorized_client.get('/posts/1/edit/', follow=True)
        self.assertRedirects(response, ('/posts/1/'))

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': '/group/the_group/',
            'posts/profile.html': '/profile/test_name_1/',
            'posts/post_detail.html': '/posts/1/',
            'posts/create_post.html': '/create/',
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
