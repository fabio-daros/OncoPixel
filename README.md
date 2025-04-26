# OncoPixel

Step 1:
---

Allow the oncopixel system to accept upload of images (eg mammograms, resonances) and use a transformer model to identify possible tumors.

Training locally with Pytorch (or tensorflow)
Use libraries such as Hugging Face Transformers, Torchvision, Monai (specific to medical images)

---

    Example of models that can serve as a base:

A. Vit-Base-Patch16-224

B. Medvit (focused on medical data)

---

    Use dataset as:

Breast Cancer Histopathological Database (Breakhis)

Digital Database for Screening Mammography (DDSM)

---

1. Create a separate API (model as microservice)
Separate backend from ml as an API Flask or Fastapapi

2. Django sends the image to this API and receives the answer

3. More scalable, useful if you want to train heavy models separately

---

    Recommended Technologies: Hugging Face Transformers: We need choose

1. Pytorch

2. Torchvision or Pil for Image

3. Monai (if you want to work with dicom and real medical data)

4. Fastapi (optional), if you want to decopulate the model

---

    - Create a simple Vit -based transformer model

    - Adapt a hugging face model to your task

    - Generate a training script and inference

    - Integrate this with your Django project

    - Create a basic pipeline for upload> Analysis> Result

---

    Overview of architecture

[User Upload] -> [Django Backend] -> Sends Image ->
                     [API Fastapi with Transformer] -> Returns result ->
                     [Django displays diagnosis / analysis]

---

     Steps to implement this
 1. Create an API with Fastapi (recommended by performance)
 2. Create the Main.py file with the API
 3. Run API

---
Integration in Django:

When an image is sent, Django makes a post with Requests:

---

Benefits of this architecture:
Scalable (you can host the model on another server or instance EC2)

Keep the django light

Allows you to change the model in the future easily

Can serve multiple models in the same microservice


---

IMAGES:

4. Upload of heavy images: Performance tips
Store images in the file system, not on the bank.

Use media_root + imagefield (as you have already configured).

Valides extensions and sizes in Forms.py to avoid abuse.

Optional: Create a Background Task with Celery or DRF to process images with AI after upload.