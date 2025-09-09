import requests
from django.utils.translation import gettext as _
from image_analysis.models import AnalyzerSettings
from django.core.files.base import ContentFile
from image_analysis.models import CellAnalysisResult, TumorImage
import uuid


# Função para obter a URL do servidor ativo
def get_analyzer_url():
    settings = AnalyzerSettings.objects.filter(active=True).first()
    if settings and settings.endpoint_url:
        return settings.endpoint_url
    return "http://oncobrain:8000/analyze/"  # Fallback padrão


# Mapeamento das classes com base no modelo (Bethesda)
CLASS_NAMES = {
    "hsil": {
        "en": "High-grade Squamous Intraepithelial Lesion (HSIL)",
        "pt-br": "Lesão Intraepitelial Escamosa de Alto Grau (HSIL)"
    },
    "lsil": {
        "en": "Low-grade Squamous Intraepithelial Lesion (LSIL)",
        "pt-br": "Lesão Intraepitelial Escamosa de Baixo Grau (LSIL)"
    },
    "nilm": {
        "en": "Negative for Intraepithelial Lesion or Malignancy (NILM)",
        "pt-br": "Negativo para Lesão Intraepitelial ou Malignidade (NILM)"
    }
}


def analyze_image(tumor_image):
    try:
        url = get_analyzer_url()
        settings = AnalyzerSettings.objects.filter(active=True).first()
        confidence_threshold = settings.min_confidence if settings else 50.0

        with open(tumor_image.image.path, 'rb') as f:
            files = {'file': f}
            data = {'confidence_threshold': str(confidence_threshold)}
            response = requests.post(url, files=files, data=data)

        if response.status_code == 200:
            response_data = response.json()
            prediction = response_data.get("prediction")

            if not prediction or prediction.get("class") is None:
                tumor_image.diagnosis = _("No diagnosis (low confidence or undetermined class).")
            else:
                predicted_class = prediction.get("class")
                confidence = prediction.get("confidence", 0)

                # Tradução baseada no mapeamento
                translated_class = CLASS_NAMES.get(predicted_class.lower(), {}).get("pt-br", predicted_class)

                tumor_image.diagnosis = f"{translated_class} ({confidence:.1f}%)"

                # Armazena o JSON completo
                tumor_image.metadata = {"prediction": prediction}

            tumor_image.save()
            return True

        else:
            raise Exception(_("OncoBrain classification failed: ") + response.text)

    except Exception as e:
        raise Exception(_("Failed to analyze image: ") + str(e))


def analyze_detection(tumor_image):
    try:
        settings = AnalyzerSettings.objects.filter(active=True).first()
        url = settings.endpoint_url.replace('/analyze/',
                                            '/detect/') if settings and settings.endpoint_url else "http://oncobrain:8000/detect/"
        confidence_threshold = 0.2

        with open(tumor_image.image.path, 'rb') as f:
            files = {'file': f}
            data = {'confidence_threshold': str(confidence_threshold)}
            response = requests.post(url, files=files, data=data)

        if response.status_code != 200:
            raise Exception(_("OncoBrain detection failed: ") + response.text)

        response_data = response.json()
        detections = response_data.get("detections", [])

        if not detections:
            tumor_image.diagnosis = _("No detections found above the threshold.")
        else:
            class_counts = {}
            for det in detections:
                label = det.get("label", "Unknown")
                class_counts[label] = class_counts.get(label, 0) + 1

            summary = ", ".join(f"{count}× Class {cls}" for cls, count in class_counts.items())
            tumor_image.diagnosis = _("Detections: ") + summary

        # Salva apenas os dados das detecções (sem URL de imagem)
        tumor_image.metadata = {
            "detections": detections
        }
        tumor_image.save()

        return True

    except Exception as e:
        raise Exception(_("Failed to analyze image (detection mode): ") + str(e))


def expand_box(box, img_width, img_height, padding=0.2):
    """
    Expande a bounding box para incluir as bordas e parte do citoplasma.
    """
    x_min, y_min, x_max, y_max = map(int, box)

    box_width = x_max - x_min
    box_height = y_max - y_min

    # Adicionar padding proporcional
    x_min = max(0, x_min - int(box_width * padding))
    y_min = max(0, y_min - int(box_height * padding))
    x_max = min(img_width, x_max + int(box_width * padding))
    y_max = min(img_height, y_max + int(box_height * padding))

    return [x_min, y_min, x_max, y_max]


def run_vit_on_crop(image_path, box, tumor_image_id=None, context_size=300):
    """
    Recorta uma região ao redor do núcleo detectado com tamanho fixo (contexto) e envia ao ViT.
    Também salva o resultado no banco.
    """
    from PIL import Image
    import io
    import base64
    from django.core.files.base import ContentFile
    from image_analysis.models import TumorImage, CellAnalysisResult

    try:
        # Abrir imagem original
        img = Image.open(image_path).convert("RGB")
        width, height = img.size

        # Calcular centro do box (núcleo detectado)
        x_min, y_min, x_max, y_max = map(int, box)
        center_x = (x_min + x_max) // 2
        center_y = (y_min + y_max) // 2

        # Definir coordenadas da região contexto
        half_size = context_size // 2
        left = max(center_x - half_size, 0)
        upper = max(center_y - half_size, 0)
        right = min(center_x + half_size, width)
        lower = min(center_y + half_size, height)

        # Recortar região contexto
        cropped_img = img.crop((left, upper, right, lower))

        # Salvar recorte em memória
        img_byte_arr = io.BytesIO()
        cropped_img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        # Enviar recorte para o OncoBrain (ViT)
        url = get_analyzer_url()
        files = {'file': ('cropped_cell.png', img_byte_arr, 'image/png')}
        response = requests.post(url, files=files)

        if response.status_code == 200:
            response_data = response.json()
            prediction = response_data.get("prediction")

            if not prediction or prediction.get("class") is None:
                classification = _("No diagnosis (low confidence or undetermined class).")
                confidence = None
            else:
                predicted_class = prediction.get("class")
                confidence = prediction.get("confidence", 0)
                translated_class = CLASS_NAMES.get(predicted_class.lower(), {}).get("pt-br", predicted_class)
                classification = f"{translated_class} ({confidence:.1f}%)"
        else:
            raise Exception(_("OncoBrain classification failed: ") + response.text)

        # Salvar resultado no banco se possível
        if tumor_image_id:
            tumor_image = TumorImage.objects.get(id=tumor_image_id)
            # Criar registro CellAnalysisResult
            cell_result = CellAnalysisResult(
                tumor_image=tumor_image,
                bounding_box=box,
                classification=classification,
                confidence=confidence
            )
            # Salvar cropped image no campo ImageField
            filename = f"cell_{tumor_image_id}_{x_min}_{y_min}.png"
            cell_result.cropped_image.save(filename, ContentFile(img_byte_arr.getvalue()), save=True)

        # Codificar imagem recortada em base64 para frontend
        img_byte_arr.seek(0)
        cropped_base64 = base64.b64encode(img_byte_arr.read()).decode('utf-8')
        cropped_data_uri = f"data:image/png;base64,{cropped_base64}"

        return {
            "classification": classification,
            "cropped_image": cropped_data_uri
        }

    except Exception as e:
        raise Exception(_("Failed to analyze cropped cell: ") + str(e))
