from django.urls import path
from . import views

app_name = 'report'

urlpatterns = [
    path('laporan/', views.laporan_form_view, name='laporan_form'),
    path('laporan/success/', views.laporan_success_view, name='laporan_success'),
]