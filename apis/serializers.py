from rest_framework import serializers
from store.models import Product
from .models import Review


class ReviewSerializer(serializers.Serializer):
    text = serializers.CharField()
    rating = serializers.IntegerField()
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user  # authenticated user

        return Review.objects.create(user=user, **validated_data)

    def update(self, instance, validated_data):
        instance.text = validated_data.get("text", instance.text)
        instance.rating = validated_data.get("rating", instance.rating)
        instance.save()
        return instance
