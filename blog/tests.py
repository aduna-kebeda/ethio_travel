from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from .models import BlogPost, BlogComment, SavedPost
from django.urls import reverse
import json

User = get_user_model()

class BlogPostTests(APITestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create test blog post
        self.post = BlogPost.objects.create(
            title='Test Post',
            slug='test-post',
            excerpt='Test excerpt',
            content='Test content',
            tags=['test', 'blog'],
            imageUrl='https://example.com/image.jpg',
            author=self.user,
            authorName=self.user.username,
            status='published',
            readTime='1 min read'
        )

    def test_create_blog_post(self):
        url = reverse('blog:post-list')
        data = {
            'title': 'New Test Post',
            'excerpt': 'New test excerpt',
            'content': 'New test content',
            'tags': ['test', 'new'],
            'imageUrl': 'https://example.com/new-image.jpg',
            'status': 'published'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BlogPost.objects.count(), 2)
        self.assertEqual(BlogPost.objects.get(title='New Test Post').author, self.user)

    def test_list_blog_posts(self):
        url = reverse('blog:post-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_retrieve_blog_post(self):
        url = reverse('blog:post-detail', args=[self.post.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Post')

    def test_update_blog_post(self):
        url = reverse('blog:post-detail', args=[self.post.id])
        data = {
            'title': 'Updated Test Post',
            'content': 'Updated content'
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Updated Test Post')

    def test_delete_blog_post(self):
        url = reverse('blog:post-detail', args=[self.post.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(BlogPost.objects.count(), 0)

    def test_increment_views(self):
        url = reverse('blog:post-view', args=[self.post.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEqual(self.post.views, 1)

class BlogCommentTests(APITestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create test blog post
        self.post = BlogPost.objects.create(
            title='Test Post',
            slug='test-post',
            excerpt='Test excerpt',
            content='Test content',
            tags=['test', 'blog'],
            imageUrl='https://example.com/image.jpg',
            author=self.user,
            authorName=self.user.username,
            status='published',
            readTime='1 min read'
        )

    def test_create_comment(self):
        url = reverse('blog:comment-list')
        data = {
            'post': self.post.id,
            'content': 'Test comment'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BlogComment.objects.count(), 1)
        self.assertEqual(BlogComment.objects.first().content, 'Test comment')

    def test_list_comments(self):
        # Create a test comment
        BlogComment.objects.create(
            post=self.post,
            user=self.user,
            content='Test comment'
        )
        url = reverse('blog:comment-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_update_comment(self):
        comment = BlogComment.objects.create(
            post=self.post,
            user=self.user,
            content='Test comment'
        )
        url = reverse('blog:comment-detail', args=[comment.id])
        data = {'content': 'Updated comment'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        comment.refresh_from_db()
        self.assertEqual(comment.content, 'Updated comment')

    def test_delete_comment(self):
        comment = BlogComment.objects.create(
            post=self.post,
            user=self.user,
            content='Test comment'
        )
        url = reverse('blog:comment-detail', args=[comment.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(BlogComment.objects.count(), 0)

class SavedPostTests(APITestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create test blog post
        self.post = BlogPost.objects.create(
            title='Test Post',
            slug='test-post',
            excerpt='Test excerpt',
            content='Test content',
            tags=['test', 'blog'],
            imageUrl='https://example.com/image.jpg',
            author=self.user,
            authorName=self.user.username,
            status='published',
            readTime='1 min read'
        )

    def test_save_post(self):
        url = reverse('blog:saved-list')
        data = {'post': self.post.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SavedPost.objects.count(), 1)

    def test_list_saved_posts(self):
        # Create a saved post
        SavedPost.objects.create(
            user=self.user,
            post=self.post
        )
        url = reverse('blog:saved-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_unsave_post(self):
        saved_post = SavedPost.objects.create(
            user=self.user,
            post=self.post
        )
        url = reverse('blog:saved-detail', args=[saved_post.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(SavedPost.objects.count(), 0) 