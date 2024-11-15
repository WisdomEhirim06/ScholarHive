from rest_framework import serializers
from .models import Students, Providers

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