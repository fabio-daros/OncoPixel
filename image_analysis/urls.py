from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_image, name='upload_image'),
    path('upload-success/', views.upload_success, name='upload_success'),  # <- ADICIONA ISSO
]
