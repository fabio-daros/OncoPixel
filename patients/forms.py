from django import forms
from .models import Patients

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patients
        fields = [
            "name","surname","age","birth","sex","pregnant","ethnicity",
            "weight","weight_unit","email","phone","country","state","county",
            "address","number","zipcode","mother_name","document","cns","notes","is_active"
        ]
        widgets = {
            "birth": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        base = "w-full rounded-xl border border-gray-700 bg-gray-900 text-gray-100 px-3 py-2 focus:outline-none focus:ring"
        for field in self.fields.values():
            from django.forms import CheckboxInput
            if not isinstance(field.widget, CheckboxInput):
                field.widget.attrs.setdefault("class", base)
