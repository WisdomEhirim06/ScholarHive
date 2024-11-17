from django.urls import path
from . import views

urlpatterns = [
    path('providers/register/', views.provider_register, name='provider_register'),
    path('providers/login/', views.provider_login, name='provider_login'),
    path('students/register/', views.student_register, name='student_register'),
    path('students/login/', views.student_login, name='student_login'),
    path('logout/', views.user_logout, name='user_logout'),
    path('session-status/', views.get_session_status, name='get_session_status'),
    
]


# /providers/register/
# /providers/login/
# /students/register/
# /students/login/
# /logout/