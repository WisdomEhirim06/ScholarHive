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
    path('scholarships/<int:scholarship_id>/update/', views.update_scholarship, name='update_scholarship'),
    path('scholarships/<int:scholarship_id>/delete/', views.delete_scholarship, name='delete_scholarship'),
    path('scholarships/my-scholarships/', views.list_provider_scholarships, name='list_provider_scholarships'),
    path('scholarships/all/', views.list_all_scholarships, name='list_all_scholarships'),
    
]


