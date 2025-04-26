from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
import uuid
from .models import User, UserProfile, BusinessOwnerProfile
from .serializers import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    ProfileSerializer, BusinessProfileSerializer,
    PasswordChangeSerializer, EmailChangeSerializer,
    LoginSerializer, UserRegistrationResponseSerializer,
    EmailVerificationSerializer, ForgotPasswordSerializer,
    ResetPasswordSerializer, ResendVerificationSerializer
)
from .permissions import IsOwnerOrReadOnly
import logging
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth import authenticate
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

logger = logging.getLogger(__name__)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]  # Default to authenticated

    def get_serializer_class(self):
        if self.action in ['create', 'register']:
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        elif self.action == 'login':
            return LoginSerializer
        elif self.action == 'verify_email':
            return EmailVerificationSerializer
        elif self.action == 'forgot_password':
            return ForgotPasswordSerializer
        elif self.action == 'reset_password':
            return ResetPasswordSerializer
        elif self.action == 'resend_verification':
            return ResendVerificationSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action in ['register', 'verify_email', 'resend_verification', 'forgot_password', 'reset_password', 'login']:
            return [AllowAny()]
        if self.action in ['list', 'retrieve', 'update', 'partial_update', 'destroy',
                           'toggle_active', 'toggle_staff']:
            return [IsAdminUser()]
        if self.action in ['me', 'change_password', 'change_email', 'logout']:
            return [IsAuthenticated()]
        return [IsAuthenticated()]

    def get_queryset(self):
        if self.action == 'list' and not self.request.user.is_staff:
            return User.objects.filter(id=self.request.user.id)
        return super().get_queryset()

    def send_verification_email(self, user):
        try:
            verification_code = user.generate_verification_code()
            
            # Create email subject and message
            subject = 'Welcome to EthioTravel - Verify Your Email'
            html_message = render_to_string('emails/verification_code.html', {
                'verification_code': verification_code,
                'user': user
            })
            
            # Send email using EmailMessage for better control
            email = EmailMessage(
                subject=subject,
                body=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email],
                reply_to=[settings.DEFAULT_FROM_EMAIL],
            )
            email.content_subtype = "html"  # Main content is now text/html
            email.send(fail_silently=False)
            
            logger.info(f"Verification code sent to {user.email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send verification code to {user.email}: {str(e)}")
            return False

    @swagger_auto_schema(
        tags=['Users'],
        operation_description="Register a new user",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'email', 'password', 'password2', 'first_name', 'last_name', 'role'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING),
                'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
                'password': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD),
                'password2': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD),
                'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                'last_name': openapi.Schema(type=openapi.TYPE_STRING),
                'role': openapi.Schema(type=openapi.TYPE_STRING, enum=['user', 'business_owner', 'admin'])
            }
        ),
        responses={
            201: openapi.Response(
                description="User registered successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_STRING),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'data': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'user': openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                        'username': openapi.Schema(type=openapi.TYPE_STRING),
                                        'email': openapi.Schema(type=openapi.TYPE_STRING),
                                        'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                                        'last_name': openapi.Schema(type=openapi.TYPE_STRING),
                                        'role': openapi.Schema(type=openapi.TYPE_STRING),
                                        'status': openapi.Schema(type=openapi.TYPE_STRING),
                                        'email_verified': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                                    }
                                ),
                                'access_token': openapi.Schema(type=openapi.TYPE_STRING),
                                'refresh_token': openapi.Schema(type=openapi.TYPE_STRING)
                            }
                        )
                    }
                )
            ),
            400: "Bad Request"
        }
    )
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'status': 'success',
                'message': 'Registration successful',
                'data': {
                    'user': UserRegistrationResponseSerializer(user).data,
                    'access_token': str(refresh.access_token),
                    'refresh_token': str(refresh)
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def verify_email(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']
        code = serializer.validated_data['code']
        
        try:
            user = User.objects.get(email=email)
            
            if not user.verification_code:
                return Response({
                    'status': 'error',
                    'message': 'No verification pending for this email'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if user.verification_expires < timezone.now():
                return Response({
                    'status': 'error',
                    'message': 'Verification code has expired'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if user.verification_code != code:
                return Response({
                    'status': 'error',
                    'message': 'Invalid verification code'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user.email_verified = True
            user.status = 'active'
            user.verification_code = None
            user.verification_expires = None
            user.save()
            
            return Response({
                'status': 'success',
                'message': 'Email verified successfully'
            })
            
        except User.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def resend_verification(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']
        
        try:
            user = User.objects.get(email=email)
            if user.email_verified:
                return Response({
                    'status': 'error',
                    'message': 'Email is already verified'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            email_sent = self.send_verification_email(user)
            
            if email_sent:
                return Response({
                    'status': 'success',
                    'message': 'New verification code sent'
                })
            else:
                return Response({
                    'status': 'error',
                    'message': 'Failed to send verification code'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except User.DoesNotExist:
            # For security reasons, don't reveal if the email exists
            return Response({
                'status': 'success',
                'message': 'If the email exists and is not verified, a new code has been sent'
            })

    def send_reset_password_email(self, user):
        try:
            reset_token = user.generate_reset_password_token()
            
            # Create email subject and message
            subject = 'Reset Your Password - EthioTravel'
            html_message = render_to_string('emails/reset_password.html', {
                'reset_token': reset_token,
                'user': user
            })
            
            # Send email using EmailMessage for better control
            email = EmailMessage(
                subject=subject,
                body=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email],
                reply_to=[settings.DEFAULT_FROM_EMAIL],
            )
            email.content_subtype = "html"  # Main content is now text/html
            email.send(fail_silently=False)
            
            logger.info(f"Password reset email sent to {user.email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send password reset email to {user.email}: {str(e)}")
            return False

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def forgot_password(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
            email_sent = self.send_reset_password_email(user)
            
            response_data = {
                'status': 'success',
                'message': 'Password reset instructions sent to your email if account exists'
            }
            
            if not email_sent and settings.DEBUG:
                response_data['reset_token'] = user.reset_password_token
            
            return Response(response_data)
        except User.DoesNotExist:
            # Return same message even if user doesn't exist (security)
            return Response({
                'status': 'success',
                'message': 'Password reset instructions sent to your email if account exists'
            })

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def reset_password(self, request, token=None):
        if not token:
            return Response({
                'status': 'error',
                'message': 'Reset token is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(reset_password_token=token)
            
            if user.reset_password_expires < timezone.now():
                return Response({
                    'status': 'error',
                    'message': 'Reset token has expired'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            # Set new password
            user.set_password(serializer.validated_data['new_password'])
            user.reset_password_token = None
            user.reset_password_expires = None
            user.save()
            
            return Response({
                'status': 'success',
                'message': 'Password reset successful'
            })
            
        except User.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Invalid reset token'
            }, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=['Users'],
        operation_description="Change user password",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['current_password', 'new_password', 'new_password2'],
            properties={
                'current_password': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD),
                'new_password': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD),
                'new_password2': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD)
            }
        ),
        responses={
            200: openapi.Response(
                description="Password changed successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: "Bad Request"
        }
    )
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['current_password']):
                return Response({'error': 'Current password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'message': 'Password successfully changed'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=['Users'],
        operation_description="Change user email",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
                'password': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD)
            }
        ),
        responses={
            200: openapi.Response(
                description="Email change request sent",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: "Bad Request"
        }
    )
    @action(detail=False, methods=['post'])
    def change_email(self, request):
        serializer = EmailChangeSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['password']):
                return Response({'error': 'Password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)
            new_email = serializer.validated_data['email']
            if User.objects.filter(email=new_email).exists():
                return Response({'error': 'Email already in use'}, status=status.HTTP_400_BAD_REQUEST)
            user.email = new_email
            user.email_verified = False
            user.generate_verification_token()
            verification_url = f"{settings.FRONTEND_URL}/verify-email/{user.verification_token}"
            send_mail(
                'Verify Your New Email',
                f'Click the link to verify your new email: {verification_url}',
                settings.DEFAULT_FROM_EMAIL,
                [new_email],
                fail_silently=False,
            )
            user.save()
            return Response({'message': 'Verification email sent to new address'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=['Users'],
        operation_description="Get current user profile",
        responses={
            200: openapi.Response(
                description="User profile",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'username': openapi.Schema(type=openapi.TYPE_STRING),
                        'email': openapi.Schema(type=openapi.TYPE_STRING),
                        'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                        'last_name': openapi.Schema(type=openapi.TYPE_STRING),
                        'role': openapi.Schema(type=openapi.TYPE_STRING),
                        'status': openapi.Schema(type=openapi.TYPE_STRING),
                        'email_verified': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                    }
                )
            )
        }
    )
    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @swagger_auto_schema(
        tags=['Users'],
        operation_description="Logout user",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['refresh'],
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        responses={
            200: openapi.Response(
                description="Logout successful",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: "Bad Request"
        }
    )
    @action(detail=False, methods=['post'])
    def logout(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Successfully logged out'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def toggle_active(self, request, pk=None):
        user = self.get_object()
        user.is_active = not user.is_active
        user.save()
        return Response({'is_active': user.is_active})

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def toggle_staff(self, request, pk=None):
        user = self.get_object()
        user.is_staff = not user.is_staff
        user.save()
        return Response({'is_staff': user.is_staff})

    @swagger_auto_schema(
        tags=['Users'],
        operation_description="Login user",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
                'password': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD)
            }
        ),
        responses={
            200: openapi.Response(
                description="Login successful",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_STRING),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'data': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'user': openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                        'username': openapi.Schema(type=openapi.TYPE_STRING),
                                        'email': openapi.Schema(type=openapi.TYPE_STRING),
                                        'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                                        'last_name': openapi.Schema(type=openapi.TYPE_STRING),
                                        'role': openapi.Schema(type=openapi.TYPE_STRING),
                                        'status': openapi.Schema(type=openapi.TYPE_STRING),
                                        'email_verified': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                                    }
                                ),
                                'access_token': openapi.Schema(type=openapi.TYPE_STRING),
                                'refresh_token': openapi.Schema(type=openapi.TYPE_STRING)
                            }
                        )
                    }
                )
            ),
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden"
        }
    )
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password']
            )
            if user:
                if not user.is_active:
                    return Response({
                        'status': 'error',
                        'message': 'Your account is inactive. Please contact support.'
                    }, status=status.HTTP_403_FORBIDDEN)
                
                if not user.email_verified:
                    return Response({
                        'status': 'error',
                        'message': 'Please verify your email before logging in.'
                    }, status=status.HTTP_403_FORBIDDEN)
                
                refresh = RefreshToken.for_user(user)
                return Response({
                    'status': 'success',
                    'message': 'Login successful',
                    'data': {
                        'user': UserSerializer(user).data,
                        'access_token': str(refresh.access_token),
                        'refresh_token': str(refresh)
                    }
                })
            else:
                return Response({
                    'status': 'error',
                    'message': 'Invalid email or password'
                }, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    @swagger_auto_schema(
        tags=['Users'],
        operation_description="Create user profile",
        request_body=ProfileSerializer,
        responses={
            201: ProfileSerializer,
            400: "Bad Request"
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Users'],
        operation_description="List user profiles",
        responses={
            200: ProfileSerializer(many=True)
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Users'],
        operation_description="Retrieve user profile",
        responses={
            200: ProfileSerializer,
            404: "Not Found"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Users'],
        operation_description="Update user profile",
        request_body=ProfileSerializer,
        responses={
            200: ProfileSerializer,
            400: "Bad Request",
            404: "Not Found"
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

class BusinessProfileViewSet(viewsets.ModelViewSet):
    queryset = BusinessOwnerProfile.objects.all()
    serializer_class = BusinessProfileSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    @swagger_auto_schema(
        operation_description="Create business profile",
        request_body=BusinessProfileSerializer,
        responses={
            201: BusinessProfileSerializer,
            400: "Bad Request"
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="List business profiles",
        responses={
            200: BusinessProfileSerializer(many=True)
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Retrieve business profile",
        responses={
            200: BusinessProfileSerializer,
            404: "Not Found"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update business profile",
        request_body=BusinessProfileSerializer,
        responses={
            200: BusinessProfileSerializer,
            400: "Bad Request",
            404: "Not Found"
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)