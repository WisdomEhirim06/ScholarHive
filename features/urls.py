from django.urls import path
from . import views

urlpatterns = [
    path('providers/register/', views.provider_register, name='provider_register'),
    path('providers/login/', views.provider_login, name='provider_login'),
    path('students/register/', views.student_register, name='student_register'),
    path('students/login/', views.student_login, name='student_login'),
    path('logout/', views.user_logout, name='user_logout'),
    path('session-status/', views.get_session_status, name='get_session_status'),
    path('scholarships/create/', views.create_scholarships, name='create_scholarship'),
    path('scholarships/update/<int:scholarship_id>/', views.update_scholarship, name='update_scholarship'),
    path('scholarships/delete/<int:scholarship_id>/', views.delete_scholarship, name='delete_scholarship'),
    path('scholarships/details/<scholarship_id>/', views.scholarship_detail, name='scholarship_details'),
    path('scholarships/', views.list_scholarships, name='list_all_scholarships'),
    
]


