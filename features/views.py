from rest_framework import status
from . serializers import (
    ProviderLoginSerializer, ProviderRegistrationSerializer, ScholarshipSerializer, 
    StudentRegistrationSerializer, StudentLoginSerializer, ScholarshipDetailSerializer, ScholarshipListPreviewSerializer,
    ApplicationFormCreateSerializer, ApplicationFormFieldSerializer, ScholarshipApplicationSerializer
)
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.middleware.csrf import get_token
from .models import Students, Providers, Scholarship, ApplicationFormField, ScholarshipApplication
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .utils import check_auth

# For Student and Provider Registration
@api_view(['POST'])
def student_register(request):
    serializer = StudentRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        student = serializer.save()

        request.session['user_type'] = 'student'
        request.session['user_id'] = student.id 
        request.session['is_authenticated'] = True

        return Response({
            'message': 'Registration Successful',
            'id': student.id,
            'email': student.email,
            'firstName': student.firstName,
            'lastName': student.lastName,
            'token': get_token(request) 
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def student_login(request):
    serializer = StudentLoginSerializer(data=request.data)
    if serializer.is_valid():
        student = serializer.validated_data['student']
        # Store student details in session
        request.session['user_type'] = 'student'
        request.session['user_id'] = student.id
        request.session['is_authenticated'] = True
        
        return Response({
            'message': 'Login successful',
            'id': student.id,
            'email': student.email,
            'firstName': student.firstName,
            'lastName': student.lastName,
            'token': get_token(request)
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def provider_register(request):
    serializer = ProviderRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        provider = serializer.save()
        # Store provider details in session
        request.session['user_type'] = 'provider'
        request.session['user_id'] = provider.id
        request.session['is_authenticated'] = True
        
        return Response({
            'message': 'Registration successful',
            'id': provider.id,
            'organizationName': provider.organizationName,
            'organizationEmail': provider.organizationEmail,
            'organizationWebsite': provider.organizationWebsite,
            'token': get_token(request)
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def provider_login(request):
    serializer = ProviderLoginSerializer(data=request.data)
    if serializer.is_valid():
        provider = serializer.validated_data['provider']
        # Store provider details in session
        request.session['user_type'] = 'provider'
        request.session['user_id'] = provider.id
        request.session['is_authenticated'] = True
        
        return Response({
            'message': 'Login successful',
            'id': provider.id,
            'organizationName': provider.organizationName,
            'organizationEmail': provider.organizationEmail,
            'organizationWebsite': provider.organizationWebsite,
            'token': get_token(request)
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def user_logout(request):
    # Clear all session data
    request.session.flush()
    return Response({'message': 'Logged out successfully'})


@api_view(['GET'])
def get_session_status(request):
    if not request.session.get('is_authenticated', False):
        return Response({
            'is_authenticated': False,
            'user': None
        })
    
    user_type = request.session.get('user_type')
    user_id = request.session.get('user_id')
    
    try:
        if user_type == 'student':
            student = Students.objects.get(id=user_id)
            return Response({
                'is_authenticated': True,
                'userType': 'student',
                'user': {
                    'id': student.id,
                    'email': student.email,
                    'firstName': student.firstName,
                    'lastName': student.lastName,
                    'educationLevel': student.educationLevel
                }
            })
        elif user_type == 'provider':
            provider = Providers.objects.get(id=user_id)
            return Response({
                'is_authenticated': True,
                'userType': 'provider',
                'user': {
                    'id': provider.id,
                    'organizationName': provider.organizationName,
                    'organizationEmail': provider.organizationEmail,
                    'organizationWebsite': provider.organizationWebsite
                }
            })
    except (Students.DoesNotExist, Providers.DoesNotExist):
        # If user not found, clear session
        request.session.flush()
        return Response({
            'is_authenticated': False,
            'user': None
        })
    

def session_authentication_middleware(get_response):
    def middleware(request):
        # Check if request path requires authentication
        protected_paths = ['/api/protected-endpoint']  # Add your protected endpoints
        
        if request.path in protected_paths:
            is_authenticated = request.session.get('is_authenticated', False)
            user_type = request.session.get('user_type')
            
            if not is_authenticated:
                return Response({
                    'error': 'Authentication required'
                }, status=status.HTTP_401_UNAUTHORIZED)
        
        response = get_response(request)
        return response
    
    return middleware


@api_view(['POST'])
@check_auth('provider')
def create_scholarships(request):
    # Check if the user is authenticated as a provider
    # Now to obtain the provider
    user_type = request.session.get('user_type')
    if user_type != 'provider':
        return Response({'error': 'Only providers can create scholarships'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        provider = Providers.objects.get(id=request.session['user_id'])
    except Providers.DoesNotExist:
        request.session.flush()
        return Response({'error': 'Provider account not found'}, status=status.HTTP_404_NOT_FOUND)
    
    scholarship_data = request.data.copy()
    scholarship_data['status'] = 'ACTIVE'

    serializer = ScholarshipSerializer(data=scholarship_data)
    if serializer.is_valid():
        scholarship = serializer.save(provider=provider)
        scholarship.status = 'ACTIVE'
        scholarship.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@check_auth('provider')
def update_scholarship(request, scholarship_id):
    """
    Update a scholarship. PUT for complete update, PATCH for partial update.
    Only the scholarship provider can update their own scholarships.
    """
    # Authentication check
    try:
        scholarship = get_object_or_404(Scholarship, id=scholarship_id)
        
        # Authorization check - ensure provider owns the scholarship
        if scholarship.provider.id != request.session['user_id']:
            return Response({
                'error': 'You do not have permission to update this scholarship.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Check if scholarship is in a state that allows updates
        if scholarship.status in ['CLOSED', 'EXPIRED']:
            return Response({
                'error': f'Cannot update scholarship with status: {scholarship.status}'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Handle different update types
        if request.method == 'PUT':
            serializer = ScholarshipSerializer(scholarship, data=request.data)
        else:  # PATCH
            serializer = ScholarshipSerializer(scholarship, data=request.data, partial=True)

        if serializer.is_valid():
            # Additional validation
            if 'deadline' in request.data:
                deadline = serializer.validated_data['deadline']
                if deadline < timezone.now():
                    return Response({
                        'error': 'Deadline cannot be in the past.'
                    }, status=status.HTTP_400_BAD_REQUEST)

            if 'max_applications' in request.data:
                max_apps = serializer.validated_data['max_applications']
                if max_apps < scholarship.current_applicants:
                    return Response({
                        'error': 'Maximum applications cannot be less than current applicants.'
                    }, status=status.HTTP_400_BAD_REQUEST)

            # Save the updated scholarship
            updated_scholarship = serializer.save()
            
            # Update status based on conditions
            if updated_scholarship.deadline < timezone.now():
                updated_scholarship.status = 'EXPIRED'
            elif updated_scholarship.current_applicants >= updated_scholarship.max_applications:
                updated_scholarship.status = 'CLOSED'
            else:
                updated_scholarship.status = 'ACTIVE'
            
            updated_scholarship.save()
            
            return Response({
                'message': 'Scholarship updated successfully',
                'scholarship': ScholarshipSerializer(updated_scholarship).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Scholarship.DoesNotExist:
        return Response({
            'error': 'Scholarship not found.'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
def delete_scholarship(request, scholarship_id):
    """
    Delete a scholarship. Only the scholarship provider can delete their own scholarships.
    """
    # Authentication check
    if not request.session.get('is_authenticated', False) or request.session.get('user_type') != 'provider':
        return Response({
            'error': 'Unauthorized. Only providers can delete scholarships.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        scholarship = get_object_or_404(Scholarship, id=scholarship_id)
        
        # Authorization check - ensure provider owns the scholarship
        if scholarship.provider.id != request.session['user_id']:
            return Response({
                'error': 'You do not have permission to delete this scholarship.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Check if scholarship has any applications before deletion
        if scholarship.current_applicants > 0:
            return Response({
                'error': 'Cannot delete scholarship with existing applications.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Perform the deletion
        scholarship.delete()
        return Response({
            'message': 'Scholarship deleted successfully.'
        }, status=status.HTTP_204_NO_CONTENT)

    except Scholarship.DoesNotExist:
        return Response({
            'error': 'Scholarship not found.'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def list_scholarships(request):
    """
    List all active scholarships with basic preview information.
    """
    scholarships = Scholarship.objects.filter(
        status='ACTIVE'
    ).select_related('provider').order_by('deadline')
    
    serializer = ScholarshipListPreviewSerializer(scholarships, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def scholarship_detail(request, scholarship_id):
    """
    Get complete detailed information about a specific scholarship.
    """
    try:
        scholarship = Scholarship.objects.select_related('provider').get(id=scholarship_id)
        
        # Only provider can view their non-active scholarships
        if scholarship.status != 'ACTIVE':
            # i set it to active, remember to change it to active
            if not request.session.get('is_authenticated') or \
               request.session.get('user_type') != 'provider' or \
               request.session.get('user_id') != scholarship.provider.id:
                return Response({
                    'error': 'Scholarship not available'
                }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ScholarshipDetailSerializer(scholarship)
        return Response(serializer.data)
        
    except Scholarship.DoesNotExist:
        return Response({
            'error': 'Scholarship not found'
        }, status=status.HTTP_404_NOT_FOUND)
    

@api_view(['POST'])
@check_auth('provider')
def create_application_form(request, scholarship_id):
    """
    Allow providers to create/update application form for their scholarship
    """
    try:
        scholarship = get_object_or_404(Scholarship, id=scholarship_id)
        
        # Verify provider owns this scholarship
        if scholarship.provider.id != request.session['user_id']:
            return Response({
                'error': 'You do not have permission to modify this scholarship'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ApplicationFormCreateSerializer(data=request.data, context={'scholarship': scholarship})
        if serializer.is_valid():
            serializer.save(scholarship=scholarship)
            return Response({
                'message': 'Application form created successfully'
            }, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    except Scholarship.DoesNotExist:
        return Response({
            'error': 'Scholarship not found'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_application_form(request, scholarship_id):
    """
    Get application form fields for a scholarship
    """
    try:
        scholarship = get_object_or_404(Scholarship, id=scholarship_id)
        fields = ApplicationFormField.objects.filter(scholarship=scholarship)
        serializer = ApplicationFormFieldSerializer(fields, many=True)
        return Response(serializer.data)
        
    except Scholarship.DoesNotExist:
        return Response({
            'error': 'Scholarship not found'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@check_auth('student')
def submit_application(request, scholarship_id):
    """
    Allow students to submit scholarship applications
    """
    try:
        scholarship = get_object_or_404(Scholarship, id=scholarship_id)
        student = get_object_or_404(Students, id=request.session['user_id'])
        
        # Check if student already applied
        if ScholarshipApplication.objects.filter(scholarship=scholarship, student=student).exists():
            return Response({
                'error': 'You have already applied for this scholarship'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate responses against form fields
        form_fields = ApplicationFormField.objects.filter(scholarship=scholarship)
        responses = request.data.get('responses', {})
        files = request.FILES
        
        # Validate required fields
        for field in form_fields:
            if field.required:
                if str(field.id) not in responses and str(field.id) not in files:
                    return Response({
                        'error': f'Field {field.label} is required'
                    }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create application
        application = ScholarshipApplication.objects.create(
            scholarship=scholarship,
            student=student,
            responses=responses,
            files={},  # Will be updated with file paths after upload
            status='SUBMITTED',
            submitted_at=timezone.now()
        )
        
        # Handle file uploads
        if files:
            file_paths = {}
            for field_id, file in files.items():
                # Save file and store path
                path = f'applications/{application.id}/{file.name}'
                # Here you would implement file storage logic
                file_paths[field_id] = path
            
            application.files = file_paths
            application.save()
        
        # Update scholarship application count
        scholarship.current_applicants += 1
        scholarship.save()
        
        return Response({
            'message': 'Application submitted successfully',
            'application_id': application.id
        }, status=status.HTTP_201_CREATED)
        
    except Scholarship.DoesNotExist:
        return Response({
            'error': 'Scholarship not found'
        }, status=status.HTTP_404_NOT_FOUND)


'''
TODO: validation for SELECT option in custom field applications
working on the FORM/DATA type
making sure that students can not create application forms
mplement password reset functionality for students and providers.
Add email verification upon signup to enhance security and prevent spam registrations.
Implement automatic status updates for scholarships based on deadlines (e.g., close applications when the deadline passes).
Notify providers when their scholarship is approaching its deadline.
Add a basic notification system:
Notify students when their application status changes.
Notify providers about new applications.
Optionally implement a messaging system to facilitate communication between providers and students.
'''


@api_view(['GET'])
@check_auth('provider')
def list_scholarship_applications(request, scholarship_id):
    """
    List all applications for a specific scholarship
    Only accessible by the scholarship provider
    """
    try:
        scholarship = get_object_or_404(Scholarship, id=scholarship_id)
        
        # Verify provider owns this scholarship
        if scholarship.provider.id != request.session['user_id']:
            return Response({
                'error': 'You do not have permission to view these applications'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get applications with optional status filter
        status_filter = request.GET.get('status', None)
        applications = ScholarshipApplication.objects.filter(scholarship=scholarship)
        
        if status_filter:
            applications = applications.filter(status=status_filter)
        
        applications = applications.order_by('-submitted_at')
        
        serializer = ScholarshipApplicationSerializer(applications, many=True)
        return Response({
            'total_applications': applications.count(),
            'applications': serializer.data
        })
        
    except Scholarship.DoesNotExist:
        return Response({
            'error': 'Scholarship not found'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@check_auth('provider')
def get_application_detail(request, application_id):
    """
    Get detailed information about a specific application
    Only accessible by the scholarship provider
    """
    try:
        application = get_object_or_404(ScholarshipApplication, id=application_id)
        
        # Verify provider owns the scholarship
        if application.scholarship.provider.id != request.session['user_id']:
            return Response({
                'error': 'You do not have permission to view this application'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ScholarshipApplicationSerializer(application)
        return Response(serializer.data)
        
    except ScholarshipApplication.DoesNotExist:
        return Response({
            'error': 'Application not found'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@check_auth('provider')
def review_application(request, application_id):
    """
    Review an application (accept/reject)
    Only accessible by the scholarship provider
    """
    try:
        application = get_object_or_404(ScholarshipApplication, id=application_id)
        
        # Verify provider owns the scholarship
        if application.scholarship.provider.id != request.session['user_id']:
            return Response({
                'error': 'You do not have permission to review this application'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Validate status
        new_status = request.data.get('status')
        if new_status not in ['ACCEPTED', 'REJECTED']:
            return Response({
                'error': 'Invalid status. Must be either ACCEPTED or REJECTED'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update application
        application.status = new_status
        application.reviewed_at = timezone.now()
        application.review_notes = request.data.get('notes', '')
        application.save()
        
        serializer = ScholarshipApplicationSerializer(application)
        return Response({
            'message': f'Application {new_status.lower()}',
            'application': serializer.data
        })
        
    except ScholarshipApplication.DoesNotExist:
        return Response({
            'error': 'Application not found'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@check_auth('student')
def list_student_applications(request):
    """
    List all applications submitted by the current student
    """
    try:
        applications = ScholarshipApplication.objects.filter(
            student_id=request.session['user_id']
        ).order_by('-submitted_at')
        
        serializer = ScholarshipApplicationSerializer(applications, many=True)
        return Response(serializer.data)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@check_auth('student')
def get_application_status(request, application_id):
    """
    Get status of a specific application
    Only accessible by the student who submitted the application
    """
    try:
        application = get_object_or_404(
            ScholarshipApplication,
            id=application_id,
            student_id=request.session['user_id']
        )
        
        serializer = ScholarshipApplicationSerializer(application)
        return Response(serializer.data)
        
    except ScholarshipApplication.DoesNotExist:
        return Response({
            'error': 'Application not found'
        }, status=status.HTTP_404_NOT_FOUND)