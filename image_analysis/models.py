from django.db import models


class TumorImage(models.Model):
    patient_id = models.CharField(max_length=100)
    image = models.ImageField(upload_to='tumor_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    diagnosis = models.TextField(blank=True, null=True)  # Resultado da IA
    metadata = models.JSONField(blank=True, null=True)  # Ex: dimensões, origem

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


class AnalyzerSettings(models.Model):
    name = models.CharField(max_length=100, default="OncoBrain")
    endpoint_url = models.CharField(
        max_length=255,
        default="http://127.0.0.1:8000/analyze/",
        help_text="URL of the OncoBrain analyze endpoint (http://hostname:port/analyze/)"
    )
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} Settings"

    class Meta:
        verbose_name = "OncoBrain Setting"
        verbose_name_plural = "OncoBrain Settings"


class TrainingVisualization(models.Model):
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Training Chart"
        verbose_name_plural = "Training Charts"
