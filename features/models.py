from django.db import models

# Create your models here.
class Student(models.Model):
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
    password = models.CharField(max_length=25)
    #last_login = models.DateTimeField(default=datetime.now)

   


class Providers(models.Model):
    organizationName = models.CharField(unique=True, max_length=25)
    organizationEmail = models.EmailField(max_length=25)
    organizationWebsite = models.URLField()
    password = models.CharField(max_length=25)
    #last_login = models.DateTimeField(default=datetime.now)

