# users/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from .serializers import RegisterSerializer, LoginSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import VerificationCode, CustomUser

# user/views.py
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        print('data:', request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'User registered successfully',
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            
            user = authenticate(username=username, password=password)
            
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'message': 'Login successful',
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_200_OK)
            
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GenerateVerificationCodeView(APIView):
    """
    API to generate a verification code for email verification
    
    POST /api/generate-verification-code/
    {
        "email": "user@example.com"
    }
    
    Returns:
    {
        "status": "success",
        "message": "Verification code sent to email",
        "code": "123456",  # For development only
        "verification_url": "http://your-frontend.com/verify?code=123456"
    }
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email', '').strip()
        
        if not email:
            return Response(
                {"error": "Email is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if email exists in the database
        if not CustomUser.objects.filter(email=email).exists():
            return Response(
                {"error": "Email not registered"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            return Response(
                {"error": "Please enter a valid email address"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Generate a new verification code
            verification = VerificationCode.generate_code(email)
            
            # In production, you would send the code via email here
            # For now, we'll include it in the response for testing
            
            # Build verification URL (frontend route)
            verification_url = f"http://localhost:3000/reset-password/abc123securetoken/?code={verification.code}"
            
            return Response({
                'status': 'success',
                'message': 'Verification code generated successfully',
                'code': verification.code,  # Remove in production
                'verification_url': verification_url
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {"error": f"Failed to generate verification code: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VerifyCodeView(APIView):
    """
    API to verify a code and reset password in one step
    
    POST /api/verify-code/
    {
        "code": "123456",
        "new_password": "new_secure_password"
    }
    
    Returns:
    {
        "status": "success",
        "message": "Password has been reset successfully"
    }
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        code = request.data.get('code', '').strip()
        new_password = request.data.get('new_password', '').strip()
        
        if not all([code, new_password]):
            return Response(
                {"error": "Code and new_password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(new_password) < 8:
            return Response(
                {"error": "Password must be at least 8 characters long"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Find the verification code (no email needed)
            verification = VerificationCode.objects.filter(
                code=code,
                is_used=False
            ).order_by('-created_at').first()
            
            if not verification or not verification.is_valid():
                return Response(
                    {"error": "Invalid or expired verification code"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get the user by email from the verification record
            try:
                user = CustomUser.objects.get(email=verification.email)
            except CustomUser.DoesNotExist:
                return Response(
                    {"error": "User account not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Update the user's password
            user.set_password(new_password)
            user.save()
            
            # Mark the code as used
            verification.mark_as_used()
            
            return Response({
                'status': 'success',
                'message': 'Password has been reset successfully'
            })
            
        except Exception as e:
            return Response(
                {"error": f"Password reset failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserProfileView(APIView):
    """
    API to get the authenticated user's profile details
    
    GET /api/user/profile/
    
    Headers:
    Authorization: Bearer <access_token>
    
    Returns:
    {
        "id": 1,
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "username": "johndoe",
        "phone_number": "+1234567890",
        "industry_type": "Technology",
        "country": "United States"
    }
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        return Response({
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username,
            'phone_number': user.phone_number,
            'industry_type': user.industry_type,
            'country': user.country
        })