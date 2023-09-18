from blog.models import Category, Comment, Post
from core.filters import CoreFilterBackend


class CategoryFilterBackend(CoreFilterBackend):
    class Meta(CoreFilterBackend.Meta):
        model = Category
        exclude = ["is_deleted", "deleted_at"]


class PostFilterBackend(CoreFilterBackend):
    class Meta(CoreFilterBackend.Meta):
        model = Post
        exclude = ["is_deleted", "deleted_at", "image"]


class CommentFilterBackend(CoreFilterBackend):
    class Meta(CoreFilterBackend.Meta):
        model = Comment
        exclude = ["is_deleted", "deleted_at"]
