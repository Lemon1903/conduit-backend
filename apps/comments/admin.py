from django.contrib import admin

from .models import Comment


# Register your models here.
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "body",
        "id",
        "author",
        "article",
        "created_at",
        "updated_at",
    )
    search_fields = ("body",)
    list_filter = ("created_at", "updated_at")

    def get_queryset(self, request):
        """Optimize queries by prefetching related profiles and articles"""
        queryset = super().get_queryset(request)
        return queryset.select_related("author", "article")
