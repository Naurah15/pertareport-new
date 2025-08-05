# models.py untuk Profile App
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    @property
    def initials(self):
        """Generate initials from username (first 2 characters)"""
        username = self.user.username
        if len(username) >= 2:
            return username[:2].upper()
        else:
            return username[0].upper()

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        # Buat profil baru saat user baru dibuat
        UserProfile.objects.create(user=instance)
    else:
        # Update profil yang sudah ada
        instance.user_profile.save()
