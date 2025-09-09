from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import TumorImageForm
from .models import TumorImage, ImageUploadSettings, KFoldTrainingVisualization, KFoldHeatmap, KFoldReport, \
    TrainingVisualization
from image_analysis.services.analyze import analyze_image, analyze_detection
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from image_analysis.models import AnalyzerSettings
from django.http import JsonResponse
import requests
import json
from types import SimpleNamespace


def upload_image(request):
    if request.method == 'POST':
        form = TumorImageForm(request.POST, request.FILES)
        files = request.FILES.getlist('image')

        # Verificar se o usuário marcou o checkbox para rodar detecção
        run_detection = request.POST.get('run_detection') == 'on'

        settings = ImageUploadSettings.objects.first()
        allowed_extensions = settings.get_allowed_extensions_list() if settings else ['jpg', 'jpeg', 'png']

        if form.is_valid():
            patient_id = form.cleaned_data['patient_id']
            image_ids = []

            for file in files:
                tumor_image = TumorImage.objects.create(
                    patient_id=patient_id,
                    image=file
                )
                image_ids.append(tumor_image.id)

                try:
                    # Rodar apenas a detecção Faster R-CNN
                    analyze_detection(tumor_image)

                    msg = f"Image #{tumor_image.id} detection completed."
                    messages.success(request, msg)

                except Exception as e:
                    messages.error(request, f"Error analyzing image {tumor_image.id}: {str(e)}")

            request.session['last_image_ids'] = image_ids
            return redirect('image_analysis:upload_success')

    else:
        form = TumorImageForm()
        settings = ImageUploadSettings.objects.first()
        allowed_extensions = settings.get_allowed_extensions_list() if settings else ['jpg', 'jpeg', 'png']

    return render(request, 'image_analysis/upload.html', {
        'form': form,
        'allowed_extensions': allowed_extensions
    })


def upload_success(request):
    image_data = []
    summary_messages = []
    image_ids = request.session.pop('last_image_ids', [])

    for image_id in image_ids:
        tumor_image = TumorImage.objects.filter(id=image_id).first()
        if tumor_image:
            # Converter metadata se vier como string JSON
            metadata = tumor_image.metadata or {}
            if isinstance(metadata, str):
                try:
                    metadata = json.loads(metadata)
                except json.JSONDecodeError:
                    metadata = {}

            prediction = metadata.get("prediction")
            confidence = prediction.get("confidence") if isinstance(prediction, dict) else None

            if prediction:
                status_message = f"Image #{tumor_image.id} analyzed successfully!"
                status_tag = 'success'
            elif confidence is not None:
                status_message = f"Low confidence in image #{tumor_image.id}. No diagnosis returned."
                status_tag = 'warning'
            else:
                status_message = f"Error analyzing image #{tumor_image.id}"
                status_tag = 'error'

            summary_messages.append({
                'id': tumor_image.id,
                'message': status_message,
                'tag': status_tag,
            })

            image_entry = {
                'id': tumor_image.id,
                'url': tumor_image.image.url,
                'filename': tumor_image.image.name.split('/')[-1],
                'diagnosis': tumor_image.diagnosis,
                'patient_id': tumor_image.patient_id,
                'uploaded_at': tumor_image.uploaded_at.strftime("%Y-%m-%d %H:%M"),
                'status_message': status_message,
                'status_tag': status_tag,
                'confidence': confidence,
                'metadata': metadata,
            }

            image_data.append(image_entry)

    return render(request, 'image_analysis/upload_success.html', {
        'image_data': image_data,
        'summary_messages': summary_messages
    })


@csrf_protect
def add_comment(request, image_id):
    if request.method == 'POST':
        try:
            image = TumorImage.objects.get(pk=image_id)
            comment = request.POST.get('comment', '')
            image.comment = comment
            image.save()
            return JsonResponse({'status': 'success'})
        except TumorImage.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Image not found'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)


@csrf_protect
def edit_comment(request, image_id):
    if request.method == 'POST':
        try:
            image = TumorImage.objects.get(pk=image_id)
            comment = request.POST.get('comment', '')
            image.comment = comment
            image.save()
            return JsonResponse({'status': 'success'})
        except TumorImage.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Image not found'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)


def search_patient(request):
    query = request.GET.get('patient_id')
    results = None

    if query:
        images = TumorImage.objects.filter(patient_id__iexact=query)
        results = []

        for img in images:
            metadata = img.metadata or {}
            prediction = metadata.get("prediction")
            confidence = prediction.get("confidence") if prediction else None

            results.append({
                'id': img.id,
                'image_url': img.image.url,
                'patient_id': img.patient_id,
                'diagnosis': img.diagnosis,
                'confidence': confidence,
                'uploaded_at': img.uploaded_at,
                'comment': img.comment,
                'filename': f"#{img.id} - {img.image.name.split('/')[-1]}",
            })

    all_ids = TumorImage.objects.exclude(patient_id__isnull=True) \
        .values_list('patient_id', flat=True) \
        .distinct().order_by('patient_id')

    return render(request, 'image_analysis/search_patient.html', {
        'query': query,
        'results': results,
        'all_ids': all_ids,
    })


@csrf_exempt
def upload_training_summary(request):
    if request.method == 'POST':
        chart = request.FILES.get('chart')
        heatmap = request.FILES.get('heatmap')
        report = request.FILES.get('report')

        if not any([chart, heatmap, report]):
            return JsonResponse({'error': 'No files provided.'}, status=400)

        # Usar ou criar um unico registro (id=1)
        visualization, created = TrainingVisualization.objects.get_or_create(id=1)

        if chart:
            visualization.chart = chart
        if heatmap:
            visualization.heatmap = heatmap
        if report:
            visualization.report_txt = report

        visualization.save()

        return JsonResponse({'success': True, 'id': visualization.id, 'created': created})

    return JsonResponse({'error': 'Invalid method.'}, status=405)


@csrf_exempt
def upload_kfold_training_summary(request):
    if request.method == 'POST':
        num_folds = request.POST.get('num_folds')
        if not num_folds:
            return JsonResponse({'error': 'num_folds not provided'}, status=400)

        # Criar o registro pai
        visualization = KFoldTrainingVisualization.objects.create()

        # Chart geral
        chart_file = request.FILES.get('chart')
        if chart_file:
            visualization.chart.save(chart_file.name, chart_file)

        # Por fold
        for fold_num in range(1, int(num_folds) + 1):
            heatmap_file = request.FILES.get(f'heatmap_{fold_num}')
            report_file = request.FILES.get(f'report_{fold_num}')

            if heatmap_file:
                KFoldHeatmap.objects.create(kfold_visualization=visualization, file=heatmap_file)

            if report_file:
                KFoldReport.objects.create(kfold_visualization=visualization, file=report_file)

        visualization.save()

        return JsonResponse({'success': True, 'id': visualization.id})

    return JsonResponse({'error': 'Invalid method'}, status=405)


def oncobrain_heartbeat(request):
    try:
        settings = AnalyzerSettings.objects.filter(active=True).first()
        if settings and settings.endpoint_url:
            base_url = settings.endpoint_url.replace('/analyze/', '/heartbeat/')
            print("Consulting OncoBrain at:", base_url)
            response = requests.get(base_url, timeout=2)
            if response.status_code == 200:
                print("OncoBrain is alive!")
                return JsonResponse({'status': 'online'})
    except Exception as e:
        print("Error when consulting OncoBrain:", e)
    return JsonResponse({'status': 'offline'})


def run_detection(request, image_id):
    image = get_object_or_404(TumorImage, id=image_id)

    try:
        analyze_detection(image)
        messages.success(request, _("Detection completed successfully for this image."))
    except Exception as e:
        messages.error(request, _("Detection failed: ") + str(e))

    return redirect('image_analysis:upload_success')


def image_detail(request, image_id):
    image = get_object_or_404(TumorImage, id=image_id)

    metadata = image.metadata or {}
    if isinstance(metadata, str):
        try:
            metadata = json.loads(metadata)
        except json.JSONDecodeError:
            metadata = {}

    detections = metadata.get("detections", [])

    image_entry = SimpleNamespace(
        id=image.id,
        url=image.image.url,
        filename=image.image.name.split('/')[-1],
        diagnosis=image.diagnosis,
        patient_id=image.patient_id,
        uploaded_at=image.uploaded_at.strftime("%Y-%m-%d %H:%M"),
        confidence=metadata.get("prediction", {}).get("confidence"),
        status_message="Analysis details",
        status_tag="success",
        metadata=metadata,
        detections_json=json.dumps(detections)
    )

    return render(request, 'image_analysis/image_detail.html', {
        'image': image_entry
    })


@csrf_exempt
def analyze_single_cell(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            image_id = data.get("image_id")
            box = data.get("box")  # [xMin, yMin, xMax, yMax]

            if not image_id or not box:
                return JsonResponse({'error': 'Missing image_id or box'}, status=400)

            image = get_object_or_404(TumorImage, id=image_id)

            # Verifica se já existe um resultado para este box
            from image_analysis.models import CellAnalysisResult
            existing_result = CellAnalysisResult.objects.filter(
                tumor_image=image,
                bounding_box=box
            ).first()

            if existing_result:
                # Retorna o resultado já salvo
                result = {
                    "classification": existing_result.classification,
                    "cropped_image": existing_result.cropped_image.url  # URL para exibir no frontend
                }
            else:
                # Rodar o ViT e salvar novo resultado
                from image_analysis.services.analyze import run_vit_on_crop
                result = run_vit_on_crop(image.image.path, box, tumor_image_id=image.id)

            return JsonResponse({'result': result}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid method'}, status=405)
