from django.shortcuts import render

def upload_image(request):
    return render(request, 'image_analysis/upload.html')
