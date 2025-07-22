from typing import cast
from django.db.models import Count
from rest_framework import status
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action

from .models import Article, Tag
from .serializers import ArticleSerializer

from ..authentication.models import User


class FlexiblePagination(PageNumberPagination):
    """
    Supports both page/limit and limit/offset pagination styles
    """

    page_size = 20
    page_size_query_param = "limit"
    max_page_size = 100

    def paginate_queryset(self, queryset, request, view=None):
        # Check if offset is provided (LimitOffset style)
        offset = request.query_params.get("offset")
        limit = request.query_params.get("limit", self.page_size)

        if offset is not None:
            # Use limit/offset pagination
            try:
                offset = int(offset)
                limit = int(limit)
                limit = min(limit, self.max_page_size)  # Respect max limit

                self.limit = limit
                self.offset = offset
                self.count = queryset.count()
                self.request = request

                return list(queryset[offset : offset + limit])
            except (ValueError, TypeError):
                pass

        # Fall back to page/page_size pagination
        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        # If we used offset/limit style
        if hasattr(self, "offset"):
            return Response(
                {
                    "count": self.count,
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                    "results": data,
                }
            )

        # Otherwise use standard page response
        return super().get_paginated_response(data)

    def get_next_link(self):
        if hasattr(self, "offset"):
            if self.offset + self.limit >= self.count:
                return None

            url = self.request.build_absolute_uri()
            offset = self.offset + self.limit
            return f"{url.split('?')[0]}?limit={self.limit}&offset={offset}"

        return super().get_next_link()

    def get_previous_link(self):
        if hasattr(self, "offset"):
            if self.offset <= 0:
                return None

            url = self.request.build_absolute_uri()
            offset = max(0, self.offset - self.limit)
            return f"{url.split('?')[0]}?limit={self.limit}&offset={offset}"

        return super().get_previous_link()


# Create your views here.
class ArticleViewSet(ModelViewSet):
    """
    A simple ViewSet for viewing, editing, and deleting articles.
    """

    queryset = Article.objects.select_related("author").prefetch_related(
        "tags", "favorited_by"
    )
    serializer_class = ArticleSerializer
    pagination_class = FlexiblePagination
    # pagination_class = None
    lookup_field = "slug"

    def get_queryset(self):
        queryset = (
            super()
            .get_queryset()
            .annotate(favorites_count=Count("favorited_by"))
            .order_by("-created_at")
        )

        tags = self.request.GET.getlist("tag")
        if tags:
            queryset = queryset.filter(tags__name__in=tags).distinct()

        author = self.request.GET.get("author")
        if author:
            queryset = queryset.filter(author__user__username=author).distinct()

        favorited = self.request.GET.get("favorited")
        if favorited:
            queryset = queryset.filter(
                favorited_by__user__username=favorited
            ).distinct()

        return queryset

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def perform_create(self, serializer):
        """Create a new article with the current user's profile as author"""
        return serializer.save(author=getattr(self.request.user, "profile"))

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def feed(self, request):
        """Get articles from followed users"""
        user = cast(User, request.user)
        queryset = (
            self.get_queryset()
            .filter(author__followers=getattr(user, "profile"))
            .distinct()
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, slug=None):
        """Favorite or unfavorite an article"""
        # return Response(
        #     {"detail": "Error favoriting article"},
        #     status=status.HTTP_400_BAD_REQUEST,
        # )

        # get the article first based on the slug
        article = self.get_object()
        user = cast(User, self.request.user)
        profile = getattr(user, "profile")

        # add/remove current user to the favorited_by of the article
        if request.method == "POST":
            article.favorited_by.add(profile)
        elif request.method == "DELETE":
            article.favorited_by.remove(profile)

        # return the updated article data
        serializer = self.get_serializer(article)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TagViewSet(GenericViewSet):
    """
    A simple ViewSet for listing all tags.
    """

    queryset = Tag.objects.annotate(articles_count=Count("articles")).order_by(
        "-articles_count"
    )
    pagination_class = None

    def list(self, request, *args, **kwargs):
        """Override the list method to customize the response"""
        queryset = self.get_queryset()
        tag_names = list(queryset.values_list("name", flat=True))
        return Response({"tags": tag_names})
