from django.test import TestCase
from django.urls import reverse

from blog.factories import CategoryFactory, CommentFactory, PostFactory
from blog.models import Comment, Post
from user.factories import UserFactory


# Create your tests here.
class TestPostCategories(TestCase):
    def test_list_post_categories(self):
        categories = CategoryFactory.create_batch(2)
        url = reverse("blog:categories_list")
        response = self.client.get(url)
        response_data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data["count"], len(categories))


class TestPosts(TestCase):
    def test_list_post(self):
        # categories = CategoryFactory.create_batch(2)
        posts = PostFactory.create_batch(2, published=True)
        url = reverse("blog:post_list_create")
        response = self.client.get(url)
        response_data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data["count"], len(posts))

    def test_list_post_by_authenticated_user(self):
        posts = PostFactory.create_batch(2, published=True)
        user = posts[0].owner
        self.client.force_login(user)
        url = reverse("blog:post_list_create")
        response = self.client.get(url)
        response_data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data["count"], 1)

    def test_retrieve_post(self):
        # categories = CategoryFactory.create_batch(2)
        posts = PostFactory.create_batch(2, published=True)
        url = reverse("blog:post_detail", kwargs={"pk": posts[0].id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_create_post(self):
        categories = CategoryFactory.create_batch(2)
        user = UserFactory()
        url = reverse("blog:post_list_create")
        category_ids = [category.id for category in categories]
        self.client.force_login(user)
        data = {"categories": category_ids, "title": "Paracetamol", "body": "100"}
        response = self.client.post(url, data)
        post = Post.objects.first()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(post.owner, user)
        self.assertEqual(post.categories.count(), len(categories))


class TestComment(TestCase):
    def test_list_comment(self):
        post = PostFactory()
        comments = CommentFactory.create_batch(2, post=post)
        url = reverse("blog:comment_list_create", kwargs={"pk": post.id})
        response = self.client.get(url)
        response_data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data["count"], len(comments))

    def test_retrieve_comment(self):
        comments = CommentFactory.create_batch(2)
        url = reverse("blog:comment_detail", kwargs={"pk": comments[0].id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)

    def test_update_comment(self):
        comment = CommentFactory()
        self.client.force_login(comment.user)
        url = reverse("blog:comment_detail", kwargs={"pk": comment.id})
        data = {"content": "The new comment was created"}
        response = self.client.patch(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        comment.refresh_from_db()
        self.assertEqual(comment.content, data["content"])

    def test_update_comment_unwant_user(self):
        user = UserFactory()
        comment = CommentFactory()
        self.client.force_login(user)
        url = reverse("blog:comment_detail", kwargs={"pk": comment.id})
        data = {"content": "The new comment was created"}
        response = self.client.patch(url, data, content_type="application/json")
        self.assertEqual(response.status_code, 403)

    def test_retrieve_comment_authenticated_user(self):
        comment = CommentFactory()
        self.client.force_login(comment.user)
        url = reverse("blog:comment_detail", kwargs={"pk": comment.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_create_comment(self):
        post = PostFactory()
        user = UserFactory()
        url = reverse("blog:comment_list_create", kwargs={"pk": post.id})
        self.client.force_login(user)
        data = {"content": "This is a new comment on this post"}
        response = self.client.post(url, data)
        response_data = response.json()
        self.assertEqual(response_data["post"], str(post.id))
        comments = Comment.objects.all()
        self.assertEqual(response.status_code, 201)
        post.refresh_from_db()
        self.assertEqual(comments.count(), 1)
