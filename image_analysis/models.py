from django.db import models


class TumorImage(models.Model):
    patient_id = models.CharField(max_length=100)
    image = models.ImageField(upload_to='tumor_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    diagnosis = models.TextField(blank=True, null=True)
    metadata = models.JSONField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Image {self.id} - Patient {self.patient_id}"


class ImageUploadSettings(models.Model):
    allowed_extensions = models.CharField(
        max_length=200,
        default='jpg,jpeg,png',
        help_text="Comma-separated list of allowed extensions (e.g., jpg,jpeg,png)"
    )

    def get_allowed_extensions_list(self):
        return [ext.strip().lower() for ext in self.allowed_extensions.split(',')]

    def __str__(self):
        return "Image Upload Settings"

    class Meta:
        verbose_name = "Image Upload Settings"
        verbose_name_plural = "Upload Settings"


# image_analysis/models.py

class AnalyzerSettings(models.Model):
    name = models.CharField(max_length=100, default="OncoBrain")
    endpoint_url = models.CharField(
        max_length=255,
        default="http://127.0.0.1:8000/analyze/",
        help_text="URL of the OncoBrain analyze endpoint (http://hostname:port/analyze/)"
    )
    active = models.BooleanField(default=True)

    min_confidence = models.FloatField(
        default=50.0,
        help_text="Minimum confidence (%) required to accept a diagnosis"
    )

    def __str__(self):
        return f"{self.name} Settings"

    class Meta:
        verbose_name = "OncoBrain API Setting"
        verbose_name_plural = "OncoBrain API Settings"


class TrainingVisualization(models.Model):
    chart = models.ImageField(upload_to='training/', blank=True, null=True)
    report_txt = models.FileField(upload_to='training/', blank=True, null=True)
    heatmap = models.ImageField(upload_to='training/', blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Training Visualization ({self.updated_at.strftime('%Y-%m-%d %H:%M')})"

    class Meta:
        verbose_name = "OncoBrain API Training Chart"
        verbose_name_plural = "OncoBrain API Training Charts"


class KFoldTrainingVisualization(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    chart = models.ImageField(upload_to='training/kfold/', blank=True, null=True)

    def __str__(self):
        return f"K-Fold Training - {self.date.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        verbose_name = "K-Fold Training Visualization"
        verbose_name_plural = "K-Fold Training Visualizations"


class KFoldHeatmap(models.Model):
    kfold_visualization = models.ForeignKey(KFoldTrainingVisualization, related_name='heatmaps',
                                            on_delete=models.CASCADE)
    file = models.ImageField(upload_to='training/kfold/heatmaps/')

    def __str__(self):
        return f"Heatmap for {self.kfold_visualization}"

    class Meta:
        verbose_name = "OncoBrain K-Fold Heatmap"
        verbose_name_plural = "OncoBrain K-Fold Heatmaps"


class KFoldReport(models.Model):
    kfold_visualization = models.ForeignKey(KFoldTrainingVisualization, related_name='reports',
                                            on_delete=models.CASCADE)
    file = models.FileField(upload_to='training/kfold/reports/')

    def __str__(self):
        return f"Report for {self.kfold_visualization}"


class CellAnalysisResult(models.Model):
    tumor_image = models.ForeignKey(TumorImage, on_delete=models.CASCADE, related_name='cell_results')
    bounding_box = models.JSONField(help_text="Bounding box coordinates [xMin, yMin, xMax, yMax]")
    cropped_image = models.ImageField(upload_to='cell_crops/')
    classification = models.TextField(help_text="Result of the ViT classification")
    confidence = models.FloatField(blank=True, null=True, help_text="Confidence level of the ViT prediction (0-100%)")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        confidence_display = f"{self.confidence:.1f}%" if self.confidence is not None else "N/A"
        return f"CellResult #{self.id} - {self.classification} ({confidence_display})"

    class Meta:
        verbose_name = "Cell Analysis Result"
        verbose_name_plural = "Cell Analysis Results"
