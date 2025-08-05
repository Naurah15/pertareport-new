from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class ReviewEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Menggunakan User bawaan Django
    time = models.DateTimeField(default=timezone.now)
    review_text = models.TextField()

    def __str__(self):
        return f"{self.user.username} - {self.product.nama}"