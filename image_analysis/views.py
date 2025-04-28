from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import TumorImageForm
from .models import TumorImage, ImageUploadSettings
from .services.analyze import analyze_image


def upload_image(request):
    if request.method == 'POST':
        form = TumorImageForm(request.POST, request.FILES)
        files = request.FILES.getlist('image')

        settings = ImageUploadSettings.objects.first()
        allowed_extensions = settings.get_allowed_extensions_list() if settings else ['jpg', 'jpeg', 'png']

        if form.is_valid():
            patient_id = form.cleaned_data['patient_id']

            for file in files:
                tumor_image = TumorImage.objects.create(
                    patient_id=patient_id,
                    image=file
                )

                try:
                    analyze_image(tumor_image)
                    messages.success(request, f"Image {tumor_image.id} analyzed successfully!")

                except Exception as e:
                    messages.error(request, f"Error analyzing image {tumor_image.id}: {str(e)}")

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
