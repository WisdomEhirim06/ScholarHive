from rest_framework import serializers
from .models import Students, Providers,Scholarship, ApplicationFormField, ScholarshipApplication

class StudentRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, max_length=128)

    class Meta:
        model = Students
        fields = ['id', 'firstName', 'lastName', 'email', 'password', 'educationLevel']
        extra_kwargs = {
            'email': {'required': True},
            'firstName': {'required': True},
            'lastName': {'required': True},
            'educationLevel': {'required': False}
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        student = Students.objects.create(**validated_data)
        student.set_password(password)
        student.save()
        return student

class StudentLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        try:
            student = Students.objects.get(email=email)
            if not student.check_password(password):
                raise serializers.ValidationError({
                    'error': 'Invalid password'
                })
            data['student'] = student
        except Students.DoesNotExist:
            raise serializers.ValidationError({
                'error': 'No student account found with this email'
            })
        
        return data
class ProviderRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, max_length=128)

    class Meta:
        model = Providers
        fields = ['id','organizationName', 'organizationEmail', 'organizationWebsite', 'password']
        extra_kwargs = {
            'organizationEmail': {'required': True},
            'organizationName': {'required': True},
            'organizationWebsite': {'required': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        provider = Providers.objects.create(**validated_data)
        provider.set_password(password)
        provider.save()
        return provider

class ProviderLoginSerializer(serializers.Serializer):
    organizationEmail = serializers.EmailField(max_length=25)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('organizationEmail')
        password = data.get('password')

        try:
            provider = Providers.objects.get(organizationEmail=email)
            if not provider.check_password(password):
                raise serializers.ValidationError({
                    'error': 'Invalid password'
                })
            data['provider'] = provider
        except Providers.DoesNotExist:
            raise serializers.ValidationError({
                'error': 'No provider account found with this email'
            })
        
        return data
    

class ScholarshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scholarship
        fields = [
            'id', 
            'title', 
            'description', 
            'deadline', 
            'requirements',
            'educationLevel',
            'max_applications',
            'current_applicants', 
            'status',
            'provider',
            'created_at', 
            'updated_at'
        ]
        read_only_fields = ['id', 'current_applicants', 'status', 'provider', 'created_at', 'updated_at']


class ScholarshipListPreviewSerializer(serializers.ModelSerializer):
    provider_name = serializers.CharField(source='provider.organizationName', read_only=True)

    class Meta:
        model = Scholarship
        fields = [
            'id',
            'title',
            'provider_name',
            'deadline'
        ]

# To return details of a scholarship
class ScholarshipDetailSerializer(serializers.ModelSerializer):
    provider_name = serializers.CharField(source='provider.organizationName')
   
    class Meta:
        model = Scholarship
        fields = [
            'id',
            'title',
            'provider_name',
            'description',
            'requirements',
            'deadline',
            'educationLevel',
            'max_applications',
            'current_applicants',
            'created_at',
            
        ]


class ApplicationFormFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationFormField
        fields = ['id', 'field_type', 'label', 'required', 'options', 'order']

class ApplicationFormCreateSerializer(serializers.Serializer):
    fields = ApplicationFormFieldSerializer(many=True)

    def create(self, validated_data):
        scholarship = validated_data['scholarship']
        fields_data = validated_data['fields']
        
        # Delete existing fields if any
        ApplicationFormField.objects.filter(scholarship=scholarship).delete()
        
        # Create new fields
        fields = []
        for order, field_data in enumerate(fields_data):
            field_data['order'] = order
            field_data['scholarship'] = scholarship
            fields.append(ApplicationFormField.objects.create(**field_data))
        
        return fields

class ScholarshipApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScholarshipApplication
        fields = ['id', 'scholarship', 'student', 'status', 'responses', 'files', 
                 'submitted_at', 'created_at', 'updated_at']
        read_only_fields = ['student', 'status', 'submitted_at', 'created_at', 'updated_at']
