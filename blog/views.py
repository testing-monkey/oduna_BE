from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveAPIView,
    RetrieveUpdateDestroyAPIView,
)

from blog.filters import CategoryFilterBackend, CommentFilterBackend, PostFilterBackend
from blog.models import Category, Comment, Post
from core.views import CoreGenericListView
from user.permissions import OwnProfilePermission

from .serializers import CategorySerializer, CommentSerializer, PostSerializer


# Create your views here.
class CategoryListView(CoreGenericListView):
    """
    This API is used to Lists Post (e.g Art, Science, e.t.c) Category.
    """

    schema_dict = {
        "summary": "Lists an new Post (e.g Art, Science, e.t.c) Category",
    }
    permission_classes = []
    serializer_class = CategorySerializer
    filterset_class = CategoryFilterBackend
    queryset = Category.objects.filter()


class PostListCreateView(ListCreateAPIView):
    permission_classes = []
    serializer_class = PostSerializer
    filterset_class = PostFilterBackend

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Post.objects.filter(owner=user)
        return Post.objects.filter(published=True)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class PostDetailView(RetrieveAPIView):
    queryset = Post.objects.filter(published=True)
    serializer_class = PostSerializer
    permission_classes = []


class CommentListCreateView(ListCreateAPIView):
    permission_classes = []
    serializer_class = CommentSerializer
    filterset_class = CommentFilterBackend

    def perform_create(self, serializer):
        request = self.request
        pk = self.kwargs["pk"]
        user = request.user if request.user.is_authenticated else None
        post = Post.objects.get(pk=pk)
        serializer.save(user=user, post=post)

    def get_queryset(self):
        pk = self.kwargs["pk"]
        queryset = Comment.objects.filter(post_id=pk)
        return queryset


class CommentDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.filter()
    serializer_class = CommentSerializer
    permission_classes = [OwnProfilePermission]
