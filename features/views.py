from rest_framework import status
from . serializers import StudentLoginSerializer, StudentRegistrationSerializer, ProviderLoginSerializer, ProviderRegistrationSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.middleware.csrf import get_token
from .models import Students, Providers


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
            'isAuthenticated': False,
            'user': None
        })
    
    user_type = request.session.get('user_type')
    user_id = request.session.get('user_id')
    
    try:
        if user_type == 'student':
            student = Students.objects.get(id=user_id)
            return Response({
                'isAuthenticated': True,
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
                'isAuthenticated': True,
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
            'isAuthenticated': False,
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