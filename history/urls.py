from django.urls import path
from . import views

app_name = 'history'

urlpatterns = [
    # API endpoint
    path('', views.history_list_api, name='history_list_api'),
    
    # Web view with filtering
    path('web/', views.history_list, name='history_list'),
    
    # Individual laporan downloads (existing functionality)
    path('download/excel/<int:pk>/', views.download_laporan_excel, name='download_excel'),
    path('download/pdf/<int:pk>/', views.download_laporan_pdf, name='download_pdf'),
    
    # New bulk download functionality
    path('bulk/excel/', views.bulk_download_excel, name='bulk_download_excel'),
    path('bulk/pdf/', views.bulk_download_pdf, name='bulk_download_pdf'),
]