from django.urls import path

from .views import (
    CategoryListView,
    CommentDetailView,
    CommentListCreateView,
    PostDetailView,
    PostListCreateView,
)

urlpatterns = [
    # code omitted for brevity
    path("posts/", PostListCreateView.as_view(), name="post_list_create"),
    path("categoriess/", CategoryListView.as_view(), name="categories_list"),
    path("posts/<uuid:pk>/", PostDetailView.as_view(), name="post_detail"),
    path(
        "posts/comment/<uuid:pk>/",
        CommentListCreateView.as_view(),
        name="comment_list_create",
    ),
    path(
        "posts/comment/<uuid:pk>/detail",
        CommentDetailView.as_view(),
        name="comment_detail",
    ),
]
