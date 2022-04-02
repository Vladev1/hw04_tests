from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from ..models import Post, Group, User


class PostsViewTest(TestCase):
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
            pub_date='Тестовая дата',
            author=User.objects.create_user(username='test_name_2'),
            group=cls.group,
        )
        cls.urls = [
            '/profile/test_name_1/',
            '/group/the_group/',
            '/',
            '/posts/1/',
        ]

    def setUp(self):
        # Создаем авторизованый клиент
        self.user1 = User.objects.create_user(username='test_name_1')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user1)
        # Создаем автора
        self.user2 = User.objects.get(username='test_name_2')
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.user2)

    def test_posts_view_uses_correct_template(self):
        """URL-адреса используют верные шаблоны, но не от автора"""
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse('posts:group_list',
                                             kwargs={'slug': 'the_group'}),
            'posts/profile.html': reverse('posts:profile',
                                          kwargs={'username': 'test_name_2'}),
            'posts/post_detail.html': reverse(
                'posts:post_detail', kwargs={'post_id': '1'}),
            'posts/create_post.html': reverse('posts:post_create'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_view_edit_use_correct_template(self):
        """Проверка страницы редактирования поста её автором"""
        response = self.authorized_client_author.get(
            reverse('posts:post_edit', kwargs={'post_id': '1'}),
        )
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_post_create_view_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_view_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом"""
        response = self.authorized_client_author.get(reverse(
            'posts:post_edit', kwargs={'post_id': '1'}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        first_object = response.context['post']
        post_detail_0 = first_object.text
        self.assertEqual(post_detail_0, 'Текст')

    def test_index_view_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'].object_list[0]
        posts = Post.objects.get()
        self.assertEqual(first_object, posts)

    def test_group_view_page_show_correct_context(self):
        """Шаблон group сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': 'the_group'}))
        first_object = response.context['group']
        second_object = response.context['page_obj'].object_list[0]
        posts = Post.objects.get()
        post_group_0 = first_object.title
        self.assertEqual(post_group_0, 'Заголовок')
        self.assertEqual(second_object, posts)

    def test_profile_view_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': 'test_name_2'}))
        first_object = response.context['author']
        second_object = response.context['page_obj'].object_list[0]
        posts = Post.objects.get()
        post_profile_0 = first_object.username
        self.assertEqual(post_profile_0, 'test_name_2')
        self.assertEqual(second_object, posts)

    def test_post_detail_view_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': '1'}))
        first_object = response.context['post']
        post_detail_0 = first_object.text
        self.assertEqual(post_detail_0, 'Текст')

    def test_post_index_show_on_template(self):
        """Пост появляется на главной странице."""
        post = Post.objects.filter(group=self.group)[0]
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertTrue(post in response.context['page_obj'].object_list)

    def test_post_group_show_on_template(self):
        """Пост появляется на странице группы."""
        post = Post.objects.filter(group=self.group)[0]
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': 'the_group'}
        ))
        self.assertTrue(post in response.context['page_obj'].object_list)

    def test_post_profile_show_on_template(self):
        """Пост появляется на профиле пользователя."""
        post = Post.objects.filter(group=self.group)[0]
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': 'test_name_2'}
        ))
        self.assertTrue(post in response.context['page_obj'].object_list)


POSTS_ON_FIRST_PAGE = 10
POSTS_ON_SECOND_PAGE = 3


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.group = Group.objects.create(
            title="Заголовок",
            slug="the_group",
            description="Описание"
        )
        cls.post = Post.objects.create(
            text="Текст",
            pub_date='Тестовая дата',
            author=User.objects.create_user(username='test_name_2'),
            group=cls.group,
        )
        cls.urls = [
            '/profile/test_name_1/',
            '/group/the_group/',
            '/',
            '/posts/1/',
        ]

    def setUp(self):
        # Создаем авторизованый клиент
        self.user1 = User.objects.create_user(username='test_name_1')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user1)
        # Создаем автора
        self.user2 = User.objects.get(username='test_name_2')
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.user2)
        # Создаем тестовые посты

        posts_count = Post.objects.count()
        while posts_count < 13:
            self.post1 = Post.objects.create(
                text="Текст",
                author=User.objects.get(username='test_name_2'),
                group=Group.objects.get(slug='the_group'),
            )
            posts_count += 1

    def test_first_page_index_contains_ten_records(self):
        """"index содержить 10 постов на первой странице."""
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(
            response.context['page_obj'].object_list), POSTS_ON_FIRST_PAGE
        )

    def test_second_page_contains_three_records(self):
        """index содержит 3 поста на второй странице."""
        # Проверка: на второй странице должно быть три поста.
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(
            response.context['page_obj'].object_list), POSTS_ON_SECOND_PAGE
        )

    def test_first_page_group_list_contains_ten_records(self):
        """"group_list содержить 10 постов на первой странице"""
        response = self.client.get(reverse(
            'posts:group_list', kwargs={'slug': 'the_group'})
        )
        self.assertEqual(len(
            response.context['page_obj'].object_list), POSTS_ON_FIRST_PAGE
        )

    def test_second_page_contains_three_records(self):
        """group_list содержит 3 поста на второй странице."""
        # Проверка: на второй странице должно быть три поста.
        response = self.client.get(reverse(
            'posts:group_list', kwargs={'slug': 'the_group'}) + '?page=2'
        )
        self.assertEqual(len(
            response.context['page_obj'].object_list), POSTS_ON_SECOND_PAGE
        )

    def test_first_page_group_list_contains_ten_records(self):
        """"group_list содержит 10 постов на первой странице"""
        response = self.client.get(reverse(
            'posts:profile', kwargs={'username': 'test_name_2'})
        )
        self.assertEqual(len(
            response.context['page_obj'].object_list), POSTS_ON_FIRST_PAGE
        )

    def test_second_page_group_list_contains_three_records(self):
        """"group_list содержит 3 поста на второй странице"""
        response = self.client.get(reverse(
            'posts:profile', kwargs={'username': 'test_name_2'}) + '?page=2'
        )
        self.assertEqual(len(
            response.context['page_obj'].object_list), POSTS_ON_SECOND_PAGE
        )
