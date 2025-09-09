from .models import AnalyzerSettings

def get_confidence_threshold():
    config = AnalyzerSettings.objects.filter(active=True).first()
    return config.confidence_threshold if config else 50.0
