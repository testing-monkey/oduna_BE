from rest_framework import serializers

from .models import Category, Comment, Post


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        # fields = ["name", "id", "created_at", "updated_at"]
        exclude = Category.get_hidden_fields()
        read_only_fields = Category.read_only_fields()



class PostSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.full_name")

    class Meta:
        model = Post
        exclude = Post.get_hidden_fields()
        read_only_fields = Post.read_only_fields()


class CommentSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="user.full_name")

    class Meta:
        model = Comment
        exclude = Comment.get_hidden_fields()
        read_only_fields = Comment.read_only_fields()
