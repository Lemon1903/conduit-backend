from django.db import models
from django.utils.text import slugify


# Create your models here.
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class Article(models.Model):
    slug = models.SlugField(unique=True, max_length=200, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(
        "users.Profile",
        on_delete=models.CASCADE,
        related_name="articles",
    )
    favorited_by = models.ManyToManyField(
        "users.Profile",
        related_name="favorited_articles",
        blank=True,
    )
    tags = models.ManyToManyField(Tag, related_name="articles", blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        title_changed = True

        if self.pk:
            # Needed to wrap in try except to avoid errors in case
            # the article was removed before the save operation
            try:
                original = Article.objects.get(pk=self.pk)
                title_changed = original.title != self.title
            except Article.DoesNotExist:
                pass

        # Always regenerate slug from current title
        if not self.slug or title_changed:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1

            def slug_exists(slug):
                # Exclude current instance from slug check (for updates)
                queryset = Article.objects.filter(slug=slug)
                return queryset.exists()

            while slug_exists(slug):
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)
