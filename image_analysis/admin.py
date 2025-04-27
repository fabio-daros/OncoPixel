from django.contrib import admin
from .models import TumorImage, ImageUploadSettings, AnalyzerSettings

@admin.register(TumorImage)
class TumorImageAdmin(admin.ModelAdmin):
    list_display = ("id", "patient_id", "uploaded_at", "diagnosis")
    search_fields = ("patient_id", "diagnosis")
    list_filter = ("uploaded_at",)

@admin.register(ImageUploadSettings)
class ImageUploadSettingsAdmin(admin.ModelAdmin):
    list_display = ("id", "allowed_extensions")

@admin.register(AnalyzerSettings)
class AnalyzerSettingsAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "endpoint_url", "active")
    list_editable = ("active",)
    search_fields = ("name", "endpoint_url")
