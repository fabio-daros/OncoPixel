from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_http_methods
from .models import Patients
from .forms import PatientForm

def _recent_patients(limit=20):
    return (
        Patients.objects
        .filter(is_active=True)
        .only("id", "name", "surname", "cns", "birth", "sex", "submitted_at")
        .order_by("-submitted_at")[:limit]
    )

@login_required
def patient_form(request):
    patients = _recent_patients()
    return render(request, "patients/patients.html", {"patients": patients})

@login_required
def patient_create(request):
    if request.method == "POST":
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Patient created successfully!")
            return redirect("patients:patients")

        return render(request, "patients/patients.html", {"form": form, "patients": _recent_patients()})
    else:
        form = PatientForm()
    return render(request, "patients/patients.html", {"form": form, "patients": _recent_patients()})

@login_required
@require_POST
def patient_search(request):
    # Campos vindos do form/modal (normalizados)
    patient_id = (request.POST.get("patient_id") or "").strip()
    name       = (request.POST.get("name") or "").strip()
    surname    = (request.POST.get("surname") or "").strip()
    mother_name= (request.POST.get("mother_name") or "").strip()
    document   = (request.POST.get("document") or "").strip()
    cns        = (request.POST.get("cns") or "").strip()

    qs = Patients.objects.filter(is_active=True)

    if patient_id:
        qs = qs.filter(id=patient_id)
    if name:
        qs = qs.filter(name__icontains=name)
    if surname:
        qs = qs.filter(surname__icontains=surname)
    if mother_name:
        qs = qs.filter(mother_name__icontains=mother_name)
    if document:
        qs = qs.filter(document__icontains=document)
    if cns:
        qs = qs.filter(cns__icontains=cns)

    if not (patient_id or name or surname or mother_name or document or cns):
        qs = qs.order_by("-submitted_at")[:5]

    data = [{"id": p.id, "name": p.name, "surname": p.surname, "age": p.age, "cns": p.cns} for p in qs]
    return JsonResponse({"patients": data})

@login_required
@require_http_methods(["GET"])
def patient_detail(request, patient_id):
    p = get_object_or_404(Patients, id=patient_id, is_active=True)
    patient_data = {
        "id": p.id,
        "name": p.name,
        "surname": p.surname,
        "birth": p.birth.strftime("%d/%m/%Y") if p.birth else "",
        "age": p.age,
        "weight": p.weight,
        "weight_unit": p.weight_unit,
        "sex": p.sex,
        "ethnicity": p.ethnicity,
        "pregnant": p.pregnant,
        "email": p.email,
        "phone": p.phone,
        "notes": p.notes,
        "country": p.country,
        "state": p.state,
        "county": p.county,
        "address": p.address,
        "zipcode": p.zipcode,
        "number": p.number,
        "mother_name": p.mother_name,
        "document": p.document,
        "cns": p.cns,
    }
    return JsonResponse(patient_data)

@login_required
def patient_update(request, pk):
    patient = get_object_or_404(Patients, pk=pk)
    if not patient.is_active:
        return redirect("patients:patients")

    if request.method == "POST":
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, "Patient updated successfully.")
            return redirect("patients:patients")
        messages.error(request, "Please correct the errors below.")
        return render(request, "patients/patients.html", {"form": form, "patient": patient, "patients": _recent_patients()})
    else:
        form = PatientForm(instance=patient)
    return render(request, "patients/patients.html", {"form": form, "patient": patient, "patients": _recent_patients()})

@login_required
@require_POST
def patient_delete(request, pk):
    patient = get_object_or_404(Patients, pk=pk, is_active=True)
    patient.is_active = False
    patient.save(update_fields=["is_active"])
    messages.success(request, "Patient deleted (soft delete).")
    return redirect("patients:patients")
