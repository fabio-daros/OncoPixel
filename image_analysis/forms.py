from django import forms
from django.utils.translation import gettext_lazy as _
from .models import TumorImage, ImageUploadSettings

class TumorImageForm(forms.ModelForm):
    class Meta:
        model = TumorImage
        fields = ['patient_id', 'image']
        labels = {
            'patient_id': _('Patient ID'),
            'image': _('Tumor Image'),
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')

        settings = ImageUploadSettings.objects.first()
        allowed_extensions = settings.get_allowed_extensions_list() if settings else ['jpg', 'jpeg', 'png']

        ext = image.name.split('.')[-1].lower()
        if ext not in allowed_extensions:
            raise forms.ValidationError(
                _("Unsupported file extension. Allowed formats: ") + ', '.join(allowed_extensions)
            )

        return image

