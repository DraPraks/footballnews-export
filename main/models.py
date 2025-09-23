from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    """Product model for Football Shop assignment (MVT demonstration)."""
    CATEGORY_CHOICES = [
        ("jersey", "Jersey"),
        ("boots", "Boots"),
        ("ball", "Ball"),
        ("accessory", "Accessory"),
        ("training", "Training Gear"),
    ]

    name = models.CharField(max_length=120)
    price = models.IntegerField(help_text="Price in whole currency units (e.g. IDR)")
    description = models.TextField()
    thumbnail = models.URLField(help_text="Image URL of the product")
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    is_featured = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Product"
        verbose_name_plural = "Products"
    