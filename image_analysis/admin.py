from django.contrib import admin
from .models import TumorImage, ImageUploadSettings, AnalyzerSettings
from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import TrainingVisualization


@admin.register(TumorImage)
class TumorImageAdmin(admin.ModelAdmin):
    list_display = ("id", "patient_id", "uploaded_at", "diagnosis", "confidence_display")
    search_fields = ("patient_id", "diagnosis")
    list_filter = ("uploaded_at",)

    def confidence_display(self, obj):
        try:
            return f'{obj.metadata.get("prediction", {}).get("confidence", 0)}%'
        except Exception:
            return "N/A"

    confidence_display.short_description = "Confidence (%)"


@admin.register(ImageUploadSettings)
class ImageUploadSettingsAdmin(admin.ModelAdmin):
    list_display = ("id", "allowed_extensions")


@admin.register(AnalyzerSettings)
class AnalyzerSettingsAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "endpoint_url", "active")
    list_editable = ("active",)
    search_fields = ("name", "endpoint_url")


@admin.register(TrainingVisualization)
class TrainingVisualizationAdmin(admin.ModelAdmin):
    readonly_fields = ['training_chart']

    def training_chart(self, obj):
        return mark_safe('<img src="/media/training/training_metrics.png" width="100%" style="max-width:800px;" />')

    training_chart.short_description = "Training Metrics"
