from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
]

# /providers/register/
# /providers/login/
# /students/register/
# /students/login/
# /logout/