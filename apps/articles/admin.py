from django.contrib import admin

from .models import Article, Tag


# Register your models here.
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "get_tags", "author", "created_at",)
    search_fields = ("title", "description")
    list_filter = ("created_at", "updated_at")
    filter_horizontal = ("tags",)

    def get_tags(self, obj):
        """Display comma-separated list of tags for the article"""
        return ", ".join([tag.name for tag in obj.tags.all()])
    
    get_tags.short_description = "Tags"

    def get_queryset(self, request):
        """Optimize queries by prefetching tags"""
        queryset = super().get_queryset(request)
        return queryset.prefetch_related("tags")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "get_article_count",)
    search_fields = ("name",)
    ordering = ("name",)

    def get_article_count(self, obj):
        """Display the number of articles associated with this tag"""
        return obj.articles.count()

    get_article_count.short_description = "Article Count"

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.prefetch_related("articles")
