from rest_framework.routers import SimpleRouter
from rest_framework_nested import routers

from .views import ArticleViewSet, TagViewSet


router = SimpleRouter()
router.register(r"articles", ArticleViewSet, basename="article")
router.register(r"tags", TagViewSet, basename="tag")
urlpatterns = router.urls
