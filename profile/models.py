from django.db import models
from django.contrib.auth.models import User
from report.models import Product

class Bookmarks(models.Model):
    bookmarks = models.ManyToManyField(User, related_name='bookmark', default=None, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
