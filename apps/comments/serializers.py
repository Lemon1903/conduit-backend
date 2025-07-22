from rest_framework.serializers import ModelSerializer

from .models import Comment
from ..users.serializers import ProfileViewSerializer


class CommentSerializer(ModelSerializer):
    author = ProfileViewSerializer(read_only=True)

    class Meta:
        model = Comment
        exclude = ("article",)
        read_only_fields = ("id", "created_at", "updated_at")
