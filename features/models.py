from django.db import models
from django.contrib.auth.hashers import make_password, check_password


# Create your models here.
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


# To create scholarship application response from students