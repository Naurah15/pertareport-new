
from django.contrib import admin
from django.urls import path
from katalog.views import get_products_json, main_view

app_name= 'katalog'

urlpatterns = [
    path('main-view/', main_view, name='main_view'),
    path('view_json/', get_products_json, name='view_json'),
  
]