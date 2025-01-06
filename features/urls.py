from django.urls import path
from . import views

urlpatterns = [
    # Registration and Login
    path('providers/register/', views.provider_register, name='provider_register'),
    path('providers/login/', views.provider_login, name='provider_login'),
    path('students/register/', views.student_register, name='student_register'),
    path('students/login/', views.student_login, name='student_login'),
    
    path('logout/', views.user_logout, name='user_logout'),
    path('session-status/', views.get_session_status, name='get_session_status'),
    
    # Scholarships
    path('scholarships/create/', views.create_scholarships, name='create_scholarship'),
    path('scholarships/update/<int:scholarship_id>/', views.update_scholarship, name='update_scholarship'),
    path('scholarships/delete/<int:scholarship_id>/', views.delete_scholarship, name='delete_scholarship'),
    path('scholarships/details/<int:scholarship_id>/', views.scholarship_detail, name='scholarship_details'),
    path('scholarships/', views.list_scholarships, name='list_all_scholarships'),
    
    # Application Forms
    path('scholarships/<int:scholarship_id>/application-form/', views.create_application_form, name='create_application_form'),
    path('scholarships/<int:scholarship_id>/application-form/get/', views.get_application_form, name='get_application_form'),
    
    # Apply and Submissions
    path('scholarships/<int:scholarship_id>/apply/', views.submit_application, name='submit_application'),
    path('scholarships/<int:scholarship_id>/applications/', views.list_scholarship_applications, name='list_scholarship_applications'),
    path('applications/<int:application_id>/', views.get_application_detail, name='get_application_detail'),
    path('applications/<int:application_id>/review/', views.review_application, name='review_application'),

    # Student Applications
    path('student/applications/', views.list_student_applications, name='list_student_applications'),
    path('student/applications/<int:application_id>/', views.get_application_status, name='get_application_status'),
]


