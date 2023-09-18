import factory

from blog.models import Category, Comment, Post
from core.factories import CoreFactory
from user.factories import UserFactory


class CategoryFactory(CoreFactory):
    class Meta:
        model = Category

    name = factory.Faker("name")


class PostFactory(CoreFactory):
    class Meta:
        model = Post

    title = factory.Faker("name")
    body = factory.Faker("sentence")
    owner = factory.SubFactory(UserFactory)


class CommentFactory(CoreFactory):
    class Meta:
        model = Comment

    content = factory.Faker("sentence")
    user = factory.SubFactory(UserFactory)
