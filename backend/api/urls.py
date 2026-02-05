"""
URL configuration for API endpoints.
"""
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.api_root, name='api-root'),
    path('upload/', views.upload_csv, name='upload-csv'),
    path('history/', views.get_history, name='get-history'),
    path('datasets/<int:dataset_id>/', views.get_dataset, name='get-dataset'),
    path('datasets/<int:dataset_id>/delete/', views.delete_dataset, name='delete-dataset'),
    path('report/<int:dataset_id>/', views.generate_report, name='generate-report'),
    path('latest/', views.get_latest_summary, name='get-latest'),
    
    # Authentication endpoints
    path('auth/', include('api.auth_urls')),
]
