from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.timesince import timesince


class CanonicalProduct(models.Model):
    canonical_name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    # Add more fields as needed (e.g., brand, category, attributes)

    def __str__(self):
        return self.canonical_name

    class Meta:
        ordering = ['canonical_name']


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    canonical = models.ForeignKey(CanonicalProduct, on_delete=models.SET_NULL, null=True, blank=True, related_name='listings')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']


class Comment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.product.name}"

    def get_time_ago(self):
        """Returns relative time like '10 days ago'"""
        return timesince(self.created_at, timezone.now())

    class Meta:
        ordering = ['-created_at']
