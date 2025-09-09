from django.db import models
from django.utils import timezone
from datetime import date

class Patients(models.Model):
    WEIGHT_UNIT_CHOICES = [
        ('kg', 'Kilograms'),
        ('lb', 'Pounds'),
    ]
    SEX_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    PREGNANT_CHOICES = [
        ('unknown', 'Unknown'),
        ('yes', 'Yes'),
        ('no', 'No'),
    ]

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, db_index=True)
    surname = models.CharField(max_length=255, db_index=True)
    age = models.IntegerField()
    birth = models.DateField()
    weight = models.FloatField()
    weight_unit = models.CharField(max_length=2, choices=WEIGHT_UNIT_CHOICES, default='kg')
    sex = models.CharField(max_length=6, choices=SEX_CHOICES)
    ethnicity = models.CharField(max_length=255, blank=True)
    pregnant = models.CharField(max_length=10, choices=PREGNANT_CHOICES, null=True, blank=True)
    email = models.EmailField(max_length=255, blank=True)
    phone = models.CharField(max_length=255, blank=True)
    notes = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, blank=True)
    state = models.CharField(max_length=255, blank=True)
    county = models.CharField(max_length=255, blank=True)
    address = models.CharField(max_length=255, blank=True)
    zipcode = models.CharField(max_length=255, blank=True)
    number = models.IntegerField(null=True, blank=True)
    mother_name = models.CharField(max_length=255, null=True, blank=True)
    document = models.CharField(max_length=255, blank=True)  # RG/Passport/etc.
    cns = models.CharField(max_length=255, unique=True)
    submitted_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-submitted_at', '-id']
        indexes = [
            models.Index(fields=['surname', 'name']),
            models.Index(fields=['document']),
            models.Index(fields=['email']),
            models.Index(fields=['phone']),
        ]

    def __str__(self):
        return f"{self.name} {self.surname}".strip()

    @property
    def full_name(self):
        return f"{self.name} {self.surname}".strip()

    @property
    def age_years(self):
        # calcula idade a partir de birth (confiável mesmo se 'age' estiver desatualizado)
        if not self.birth:
            return None
        today = date.today()
        return today.year - self.birth.year - ((today.month, today.day) < (self.birth.month, self.birth.day))

    def clean(self):
        # validações leves (opcionais)
        if self.pregnant and self.pregnant != 'unknown' and self.sex != 'female':
            from django.core.exceptions import ValidationError
            raise ValidationError({'pregnant': "Pregnancy status only applicable for female sex."})
