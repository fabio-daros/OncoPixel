from django.shortcuts import render, redirect
from .forms import TumorImageForm
from .models import TumorImage, ImageUploadSettings


def upload_image(request):
    if request.method == 'POST':
        form = TumorImageForm(request.POST, request.FILES)
        files = request.FILES.getlist('image')

        settings = ImageUploadSettings.objects.first()
        allowed_extensions = settings.get_allowed_extensions_list() if settings else ['jpg', 'jpeg', 'png']

        if form.is_valid():
            patient_id = form.cleaned_data['patient_id']

            for file in files:
                TumorImage.objects.create(
                    patient_id=patient_id,
                    image=file
                )

            return redirect('upload_success')

    else:
        form = TumorImageForm()
        settings = ImageUploadSettings.objects.first()
        allowed_extensions = settings.get_allowed_extensions_list() if settings else ['jpg', 'jpeg', 'png']

    return render(request, 'image_analysis/upload.html', {
        'form': form,
        'allowed_extensions': allowed_extensions
    })


def upload_success(request):
    return render(request, 'image_analysis/upload_success.html')
