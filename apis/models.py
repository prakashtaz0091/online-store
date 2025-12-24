from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class Review(models.Model):
    user = models.ForeignKey("accounts.CustomUser", on_delete=models.CASCADE)
    product = models.ForeignKey("store.Product", on_delete=models.CASCADE)
    text = models.TextField()
    rating = models.IntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.text

    class Meta:
        ordering = ["-created_at"]
