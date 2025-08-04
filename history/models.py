from django.db import models
from django.contrib.auth.models import User
import uuid

class ForumEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, default=None)  # Default title
    description = models.TextField(default=None)  # Default description

    def __str__(self):
        return self.title


class Comment(models.Model):
    forum_entry = models.ForeignKey(ForumEntry, on_delete=models.CASCADE, related_name='comments', default=None)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.forum_entry.title}"