from django.urls import path
from .views import profile_buyer, profile_seller, profile_buyer_edit, profile_seller_edit, api_profile_buyer, api_profile_seller, api_get_choices

app_name = 'user_profile'

urlpatterns = [
    path('buyer/', profile_buyer, name='profile_buyer'),
    path('seller/', profile_seller, name='profile_seller'),
    path('buyer/edit', profile_buyer_edit, name='profile_buyer_edit'),
    path('seller/edit', profile_seller_edit, name='profile_seller_edit'),

    path('api/buyer/', api_profile_buyer, name='api_profile_buyer'),
    path('api/seller/', api_profile_seller, name='api_profile_seller'),
    path('api/edit/choices/', api_get_choices, name='api_get_choices'),
]