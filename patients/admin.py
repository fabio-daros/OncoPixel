from django.contrib import admin
from .models import Patients

@admin.register(Patients)
class PatientsAdmin(admin.ModelAdmin):
    list_display = ("cns", "surname", "name", "sex", "age", "birth", "email", "phone", "is_active", "submitted_at")
    search_fields = ("cns", "name", "surname", "document", "email", "phone", "zipcode")
    list_filter = ("sex", "weight_unit", "pregnant", "is_active", "submitted_at")
    ordering = ("-submitted_at",)
