import requests
from django.utils.translation import gettext as _
from django.utils import translation
from image_analysis.models import AnalyzerSettings


# Função para obter a URL do servidor ativo
def get_analyzer_url():
    settings = AnalyzerSettings.objects.filter(active=True).first()
    if settings and settings.endpoint_url:
        return settings.endpoint_url
    return "http://oncobrain:8000/analyze/"  # Fallback padrão


# Mapeamento das classes para diferentes idiomas
CLASS_NAMES = {
    0: {
        "en": "Normal",
        "pt-br": "Normal"
    },
    1: {
        "en": "Benign",
        "pt-br": "Benigno"
    },
    2: {
        "en": "Malignant",
        "pt-br": "Maligno"
    },
    3: {
        "en": "Carcinoma",
        "pt-br": "Carcinoma"
    }
}


# Função principal para enviar imagem e receber a análise
def analyze_image(tumor_image):
    try:
        url = get_analyzer_url()

        with open(tumor_image.image.path, 'rb') as f:
            files = {'file': f}
            response = requests.post(url, files=files)

        if response.status_code == 200:
            prediction = response.json().get("prediction")

            tumor_image.metadata = {"prediction": prediction}

            current_language = translation.get_language()

            diagnosis = CLASS_NAMES.get(prediction, {}).get(
                current_language,
                CLASS_NAMES.get(prediction, {}).get("en", "Unknown")
            )

            tumor_image.diagnosis = diagnosis
            tumor_image.save()

            return True
        else:
            raise Exception(_("OncoBrain analysis failed: ") + response.text)

    except Exception as e:
        raise Exception(_("Failed to analyze image: ") + str(e))
