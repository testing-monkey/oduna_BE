from django.db import models

from blog.literals import BLOG_PHOTO_DIRECTORY
from core.models import CoreModel, DeleteModelMixin
from user.models import User

# Create your models here.


class Category(DeleteModelMixin, CoreModel):
    name = models.TextField(help_text="Blog Name")

    def __str__(self) -> str:
        return f"{self.name} ({self.is_deleted})"

    @classmethod
    def read_only_fields(cls):
        return super().read_only_fields()

    @classmethod
    def get_hidden_fields(cls):
        return super().get_hidden_fields()


class Post(DeleteModelMixin, CoreModel):
    categories = models.ManyToManyField(Category, related_name="products")
    title = models.CharField(max_length=100, blank=True, default="")
    body = models.TextField(blank=True, default="")
    owner = models.ForeignKey(
        User, related_name="posts", on_delete=models.CASCADE, blank=True, null=True
    )
    published = models.BooleanField(default=False)
    image = models.ImageField(
        upload_to=BLOG_PHOTO_DIRECTORY,
        blank=True,
        null=True,
    )

    @classmethod
    def read_only_fields(cls):
        return ["owner", "published"]

    class Meta:
        ordering = ["created_at"]


class Comment(CoreModel):
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies"
    )
    user = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="comments", blank=True, null=True
    )
    post = models.ForeignKey(
        Post, related_name="comments", on_delete=models.SET_NULL, blank=True, null=True
    )
    content = models.TextField()

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return str(self.user) + " comment " + str(self.content)

    @property
    def children(self):
        return Comment.objects.filter(parent=self).reverse()

    @property
    def is_parent(self):
        if self.parent is None:
            return True
        return False

    @classmethod
    def read_only_fields(cls):
        return [
            "user",
            "parent",
            "post",
        ]
