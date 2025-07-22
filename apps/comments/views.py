from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from .models import Comment
from .serializers import CommentSerializer

from ..articles.models import Article


# Create your views here.
class CommentViewset(ModelViewSet):
    """
    A viewset for CRUD operations on comments.
    """

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = []
    pagination_class = None

    def get_queryset(self):
        article_slug = self.kwargs.get("article_slug")
        if article_slug:
            comments = Comment.objects.filter(article__slug=article_slug)
            return comments.order_by("-created_at")
        return super().get_queryset()

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def perform_create(self, serializer):
        user = self.request.user
        article_slug = self.kwargs.get("article_slug")
        article = get_object_or_404(Article, slug=article_slug)
        serializer.save(author=getattr(user, "profile"), article=article)
