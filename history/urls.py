from django.urls import path
from . import views

app_name = 'history'

urlpatterns = [
    path('', views.history_list, name='history_list'),
    path('download/excel/<int:pk>/', views.download_laporan_excel, name='download_excel'),
    path('download/pdf/<int:pk>/', views.download_laporan_pdf, name='download_pdf'),
]
