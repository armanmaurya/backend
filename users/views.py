from urllib.parse import urlencode
from rest_framework.views import APIView
from django.conf import settings
from django.shortcuts import redirect
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.response import Response
from rest_framework import status

from .mixins import PublicApiMixin, ApiErrorsMixin
from .utils import google_get_access_token, google_get_user_info
from users.models import CustomUser as User, EmailVerification
from users.serializers import GoogleAuthInputSerializer, RegisterSerializer, LoginSerializer, EmailVerificationSerializer, VerifyCodeSerializer
from django.contrib.auth import login, logout  # If used custom user model
from django.core.mail import send_mail
from django.utils import timezone
import random
from rest_framework.authentication import SessionAuthentication




def generate_tokens_for_user(user):
    """
    Generate access and refresh tokens for the given user
    """
    serializer = TokenObtainPairSerializer()
    token_data = serializer.get_token(user)
    access_token = token_data.access_token
    refresh_token = token_data
    return access_token, refresh_token

class PersonalInfoView(APIView):
    authentication_classes = [SessionAuthentication]
    def get(self, request):
        user = request.user
        return Response({
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        })

class GoogleAuth(PublicApiMixin, ApiErrorsMixin, APIView):

    def get(self, request, *args, **kwargs):
        input_serializer = GoogleAuthInputSerializer(data=request.GET)
        input_serializer.is_valid(raise_exception=True)

        validated_data = input_serializer.validated_data

        code = validated_data.get('code')
        error = validated_data.get('error')
        redirect_path = validated_data.get('redirect_path')

        login_url = f'{settings.BASE_FRONTEND_URL}/login'
    
        if error or not code:
            params = urlencode({'error': error})
            return redirect(f'{login_url}?{params}')

        redirect_uri = f'{settings.BASE_FRONTEND_URL}{redirect_path}'
        access_token = google_get_access_token(code=code, 
                                               redirect_uri=redirect_uri)

        user_data = google_get_user_info(access_token=access_token)

        try:
            user = User.objects.get(email=user_data['email'])
            request.session['user_id'] = user.id
            login(request, user)
            request.session.save()
            return Response({'message': 'Login successful'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            first_name = user_data.get('given_name', '')
            last_name = user_data.get('family_name', '')

            user = User.objects.create(
                email=user_data['email'],
                first_name=first_name,
                last_name=last_name,
                registration_method='google',
            )
         
            request.session['user_id'] = user.id
            login(request, user)
            request.session.save()
            return Response(status=status.HTTP_201_CREATED)
        
        
class RegisterView(APIView):
    def post(self, request):
        email = request.session.get('email')
        if not email:
            return Response({'error': 'Email not found in session'}, status=status.HTTP_400_BAD_REQUEST)
        request.data['email'] = email
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            login(request, user)  # Log in the user
            request.session.set_expiry(12000000)  # Session expires when the browser is closed
            request.session['user_id'] = user.id  # Save user id in session
            return Response({'message': 'Registration successful'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            request.session['user_id'] = user.id
            login(request, user)
            request.session.save()
            return Response({'message': 'Login successful'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 

        
class LogoutView(APIView):
    def get(self, request):
        logout(request)
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
    
    
class SendVerificationCodeView(APIView):
    def post(self, request):
        serializer = EmailVerificationSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            verification, created = EmailVerification.objects.get_or_create(email=email)
            if not created:
                verification.code = str(random.randint(1000, 9999))
                verification.created_at = timezone.now()
                verification.verified = False
                verification.save()
            send_mail(
                'Your verification code',
                f'Your verification code is {verification.code}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            request.session['email'] = email
            return Response({'message': 'Verification code sent.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class VerifyCodeView(APIView):
    def post(self, request):
        email = request.session.get('email')
        if not email:
            return Response({'error': 'Email not found in session'}, status=status.HTTP_400_BAD_REQUEST)
        request.data['email'] = email
        serializer = VerifyCodeSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            code = serializer.validated_data['code']
            try:
                verification = EmailVerification.objects.get(email=email, code=code)
                if verification.is_valid():
                    verification.verified = True
                    verification.save()
                    return Response({'message': 'Email verified. You can now complete the registration.'}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Verification code expired'}, status=status.HTTP_400_BAD_REQUEST)
            except EmailVerification.DoesNotExist:
                return Response({'error': 'Invalid verification code'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
