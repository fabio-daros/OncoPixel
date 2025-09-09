from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import CellAnalysisResult

from .models import (
    TumorImage,
    ImageUploadSettings,
    AnalyzerSettings,
    TrainingVisualization,
    KFoldHeatmap,
)

admin.site.site_header = "OncoPixel Admin"
admin.site.site_title = "OncoPixel Admin Portal"
admin.site.index_title = "Welcome to the Oncopixel System"


class CellAnalysisResultInline(admin.TabularInline):
    model = CellAnalysisResult
    extra = 0
    readonly_fields = (
        'cropped_image_preview',
        'bounding_box',
        'classification',
        'confidence',
        'created_at'
    )
    fields = (
        'cropped_image_preview',
        'bounding_box',
        'classification',
        'confidence',
        'created_at'
    )
    can_delete = False
    show_change_link = True

    def cropped_image_preview(self, obj):
        if obj.cropped_image:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit:contain;border:1px solid #ccc;" />',
                obj.cropped_image.url
            )
        return "No Image"

    cropped_image_preview.short_description = "Cropped Cell"


@admin.register(TumorImage)
class TumorImageAdmin(admin.ModelAdmin):
    list_display = ("id", "patient_id", "uploaded_at", "diagnosis", "confidence_display")
    search_fields = ("patient_id", "diagnosis")
    list_filter = ("uploaded_at",)
    inlines = [CellAnalysisResultInline]

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
    readonly_fields = ['training_chart', 'heatmap_preview', 'report_preview']
    fields = ['training_chart', 'heatmap_preview', 'report_preview']
    list_display = ['__str__', 'updated_at']

    def training_chart(self, obj):
        if obj.chart:
            return mark_safe(f'<img src="{obj.chart.url}" width="100%" style="max-width:800px;" />')
        return "No chart available"

    def heatmap_preview(self, obj):
        if obj.heatmap:
            return mark_safe(f'<img src="{obj.heatmap.url}" width="100%" style="max-width:600px;" />')
        return "No heatmap available"

    def report_preview(self, obj):
        if obj.report_txt and obj.report_txt.name.endswith('.txt'):
            try:
                with open(obj.report_txt.path, 'r', encoding='utf-8') as f:
                    content = f.read()
                lines = content.splitlines()[:50]
                content_limited = '\n'.join(lines)
                return mark_safe(
                    f'<pre style="white-space:pre-wrap; max-height:300px; overflow:auto;">{content_limited}</pre>')
            except Exception as e:
                return f"Error reading file: {e}"
        return "No report available"


@admin.register(KFoldHeatmap)
class KFoldHeatmapAdmin(admin.ModelAdmin):
    list_display = ('id', 'kfold_visualization', 'image_preview')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.file:
            return format_html('<img src="{}" width="300" />', obj.file.url)
        return "No Image"

    image_preview.short_description = "Heatmap Preview"

# === Removidos ===
# @admin.register(KFoldTrainingVisualization)
# class KFoldTrainingVisualizationAdmin(admin.ModelAdmin):
#     readonly_fields = ('created_at',)
#     list_display = ('id', 'created_at')

# @admin.register(KFoldReport)
# class KFoldReportAdmin(admin.ModelAdmin):
#     list_display = ('id', 'kfold_visualization', 'report_link')
#     readonly_fields = ('report_link',)

#     def report_link(self, obj):
#         if obj.file:
#             return format_html('<a href="{}" target="_blank">Download Report</a>', obj.file.url)
#         return "No Report"
#     report_link.short_description = "Report File"
