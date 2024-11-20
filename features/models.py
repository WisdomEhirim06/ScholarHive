from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.core.validators import MinValueValidator
import datetime
from django.core.exceptions import ValidationError
from django.utils import timezone


# User Types: Students and Providers
class Students(models.Model):
    EDUCATION_CHOICES = [
        ('Undergraduate', 'Undergraduate'),
        ('Masters', 'Masters'),
        ('PhD', 'PhD'),
    ]
    firstName = models.CharField(max_length=15)
    lastName = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    educationLevel = models.CharField(max_length=50, choices=EDUCATION_CHOICES, blank=True, null=True)
    is_premium = models.BooleanField(default=False)
    password = models.CharField(max_length=128)
    #last_login = models.DateTimeField(default=datetime.now)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)


class Providers(models.Model):
    organizationName = models.CharField(unique=True, max_length=25)
    organizationEmail = models.EmailField(max_length=25)
    organizationWebsite = models.URLField()
    password = models.CharField(max_length=128)
    #last_login = models.DateTimeField(default=datetime.now)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)


# To create scholarship provider info for scholarships
# Scholarships Model
class Scholarship(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('ACTIVE', 'Active'),
        ('CLOSED', 'Closed'),
        ('EXPIRED', 'Expired')
    ]

    EDUCATION_CHOICES = [
        ('Undergraduate', 'Undergraduate'),
        ('Masters', 'Masters'),
        ('PhD', 'PhD'),
    ]

    # Provider relationship
    provider = models.ForeignKey(Providers, on_delete=models.CASCADE, related_name='scholarships')

    # Basic scholarship information
    title = models.CharField(max_length=200)
    description = models.TextField()
    deadline = models.DateTimeField()
    requirements = models.TextField()
    educationLevel = models.CharField(max_length=50, choices=EDUCATION_CHOICES, blank=True, null=True)

    # Tracking fields
    max_applications = models.PositiveIntegerField(null=True, blank=True)
    current_applicants = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        # Custom validation for deadline
        if self.deadline:
            if self.deadline < timezone.now():
                raise ValidationError({
                    'deadline': 'Deadline cannot be in the past.'
                })
            
            # Deadline should be at least 7 days from now for new scholarships
            if not self.pk and self.deadline < timezone.now() + datetime.timedelta(days=7):
                raise ValidationError({
                    'deadline': 'Deadline must be at least 7 days from now for new scholarships.'
                })

        # Validate current applicants against max applications
        if self.current_applicants > self.max_applications:
            raise ValidationError({
                'current_applicants': 'Current applicants cannot exceed maximum applications.'
            })

        # Validate status transitions
        if self.pk:  # If this is an existing scholarship
            old_instance = Scholarship.objects.get(pk=self.pk)
            if old_instance.status in ['CLOSED', 'EXPIRED'] and self.status == 'ACTIVE':
                raise ValidationError({
                    'status': 'Cannot reactivate a closed or expired scholarship.'
                })

    def save(self, *args, **kwargs):
        # Auto-update status based on deadline and current applications
        self.clean()

        if self.deadline < timezone.now():
            self.status = 'EXPIRED'
        elif self.current_applicants >= self.max_applications:
            self.status = 'CLOSED'
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} by {self.provider.organizationName} is {self.status}"



# To create scholarship application response from students