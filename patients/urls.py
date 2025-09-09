from django.urls import path
from . import views

app_name = "patients"
urlpatterns = [
    path("", views.patient_form, name="patients"),
    path("new/", views.patient_create, name="create"),
    path("search/", views.patient_search, name="search"),
    path("<int:patient_id>/", views.patient_detail, name="detail"),
    path("<int:pk>/edit/", views.patient_update, name="update"),
    path("<int:pk>/delete/", views.patient_delete, name="delete"),
]
