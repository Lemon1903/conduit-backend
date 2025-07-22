from rest_framework_nested.routers import NestedSimpleRouter

from ..articles.urls import router
from .views import CommentViewset

comment_router = NestedSimpleRouter(router, r"articles", lookup="article")
comment_router.register(
    r"comments", CommentViewset, basename="article-comments"
)
urlpatterns = comment_router.urls
