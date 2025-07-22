from rest_framework import serializers

from .models import Article, Tag
from ..users.serializers import ProfileViewSerializer

# how serializers handle serialization:
# - `to_representation`: Converts model instance to a data type suitable for output (e.g., JSON).
# - `to_internal_value`: Converts input data (e.g., JSON) to a format suitable for creating/updating model instances.
# API JSON (response) ←-- to_representation() ←-- Database Objects
# API JSON (request)  --→ to_internal_value() --→ Database Objects


class TagsField(serializers.Field):
    """Custom field to handle tags for both reading and writing"""

    def to_representation(self, value):
        """Convert Tag objects to list of tag names for output"""
        return [tag.name for tag in value.all()]

    def to_internal_value(self, data):
        """Convert list of tag names to list of strings for processing"""
        if not isinstance(data, list):
            raise serializers.ValidationError("Tags must be a list.")

        tag_names = []
        for tag_name in data:
            if not isinstance(tag_name, str):
                raise serializers.ValidationError("Each tag must be a string.")
            if len(tag_name.strip()) == 0:
                raise serializers.ValidationError("Tag names cannot be empty.")
            tag_names.append(tag_name.strip())

        return tag_names


class ArticleSerializer(serializers.ModelSerializer):
    author = ProfileViewSerializer(read_only=True)
    tags = TagsField(required=False)
    favorites_count = serializers.ReadOnlyField()

    class Meta:
        model = Article
        exclude = ("id", "favorited_by")
        read_only_fields = (
            "author",
            "slug",
            "favorites_count",
            "created_at",
            "updated_at",
        )

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        request = self.context.get("request")

        rep["favorited"] = False
        if request and request.user.is_authenticated:
            user_who_favorited = instance.favorited_by.filter(user=request.user)
            rep["favorited"] = user_who_favorited.exists()

        return rep

    def create(self, validated_data):
        tags = validated_data.pop("tags", [])

        article = Article.objects.create(**validated_data)

        for tag in tags:
            tag_instance, _ = Tag.objects.get_or_create(name=tag)
            article.tags.add(tag_instance)

        return article

    def update(self, instance, validated_data):
        tags = validated_data.pop("tags", None)

        if tags is not None:
            instance.tags.clear()
            for tag in tags:
                tag_instance, _ = Tag.objects.get_or_create(name=tag)
                instance.tags.add(tag_instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance
