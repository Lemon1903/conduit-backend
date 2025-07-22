from django.db import models


# Create your models here.
class Comment(models.Model):
    author = models.ForeignKey(
        "users.Profile", on_delete=models.CASCADE, related_name="comments"
    )
    article = models.ForeignKey(
        "articles.Article", on_delete=models.CASCADE, related_name="comments"
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Comment by {self.author.user.username} on {self.article.title}: {self.body[:20]}..."
