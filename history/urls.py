from django.urls import path
from . import views

app_name = 'history'

urlpatterns = [
    path('', views.history_list_api, name='history_list_api'),  # Changed this line
    path('download/excel/<int:pk>/', views.download_laporan_excel, name='download_excel'),
    path('download/pdf/<int:pk>/', views.download_laporan_pdf, name='download_pdf'),
    path('web/', views.history_list, name='history_list'),  # Moved web view here
]