from rest_framework import status
from . serializers import (
    ProviderLoginSerializer, ProviderRegistrationSerializer, ScholarshipSerializer, 
    StudentRegistrationSerializer, StudentLoginSerializer, ScholarshipDetailSerializer, ScholarshipListPreviewSerializer
)
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.middleware.csrf import get_token
from .models import Students, Providers, Scholarship
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
    try:
        provider = Providers.objects.get(id=request.session['user_id'])
    except Providers.DoesNotExist:
        request.session.flush()
        return Response({'error': 'Provider account not found'}, status=status.HTTP_404_NOT_FOUND)
    
    scholarship_data = request.data.copy()
    scholarship_data['status'] = 'ACTIVE'

    serializer = ScholarshipSerializer(data=scholarship_data)
    if serializer.is_valid():
        serializer.save(provider=provider)
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


# @api_view(['GET'])
# def list_provider_scholarships(request):
#     # Check if user is authenticated as a provider
#     if not request.session.get('is_authenticated', False) or request.session.get('user_type') != 'provider':
#         return Response({
#             'error': 'Unauthorized. Only providers can view their scholarships.'
#         }, status=status.HTTP_403_FORBIDDEN)
    
#     # Get scholarships for the current provider
#     scholarships = Scholarship.objects.filter(provider_id=request.session['user_id'])
#     serializer = ScholarshipSerializer(scholarships, many=True)
#     return Response(serializer.data)




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