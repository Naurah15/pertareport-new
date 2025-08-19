from django.urls import path
from . import views

app_name = 'report'

urlpatterns = [
    path('laporan/', views.laporan_form_view, name='laporan_form'),
    path('laporan/success/', views.laporan_success_view, name='laporan_success'),
    path('laporan/manage-jenis-kegiatan/', views.manage_jenis_kegiatan, name='manage_jenis_kegiatan'),

    path('api/jenis-kegiatan/', views.get_jenis_kegiatan, name='api_jenis_kegiatan'),
    path('api/laporan/', views.create_laporan, name='api_create_laporan'),
    path('api/laporan-list/', views.get_laporan_list, name='api_laporan_list'),
    path('api/upload-images/', views.upload_laporan_images, name='api_upload_images'),
]