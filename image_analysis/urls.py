from django.urls import path
from . import views

app_name = "image_analysis"

urlpatterns = [
    path('', views.upload_image, name='upload_image'),
    path('upload-success/', views.upload_success, name='upload_success'),
    path('add_comment_ajax/<int:image_id>/', views.add_comment, name='add_comment'),
    path('edit_comment/<int:image_id>/', views.edit_comment, name='edit_comment'),
    path('search/', views.search_patient, name='search_patient'),
    path('upload-training-summary/', views.upload_training_summary, name='upload_training_summary'),
    path('upload_kfold_training_summary/', views.upload_kfold_training_summary, name='upload_kfold_training_summary'),
    path('oncobrain-heartbeat/', views.oncobrain_heartbeat, name='oncobrain_heartbeat'),
    path('image/<int:image_id>/', views.image_detail, name='image_detail'),
    path('run-detection/<int:image_id>/', views.run_detection, name='run_detection'),
    path('analyze-cell/', views.analyze_single_cell, name='analyze_cell'),

]
