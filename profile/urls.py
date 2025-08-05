# Update urls.py Anda dengan menambahkan import dan path baru

from django.urls import path
from profile.views import (profile_view, update_profile, profile_flutter, update_profile_flutter  # Import baru
)

app_name = 'profile'

urlpatterns = [
    
    # Profile URLs (baru)
    path('', profile_view, name='profile_view'),
    path('update/', update_profile, name='update_profile'),
    path('flutter/', profile_flutter, name='profile_flutter'),
    path('update_flutter/', update_profile_flutter, name='update_profile_flutter'),
]