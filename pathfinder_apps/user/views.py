from datetime import datetime
from tokenize import TokenError
from click import UUID
from django.conf import settings
import jwt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict


from .models import CustomUser, UserInfo
from ..utils.email_utils import EmailUtils
from .serializers import UserSerializer, UserInfoSerializer
from datetime import timedelta
import pytz
from jwt.exceptions import ExpiredSignatureError, DecodeError



class SignUpView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            #sending email 
            now_ist = datetime.now(pytz.timezone('Asia/Kolkata'))

# Generate a JWT token that expires in 15 minutes
            token = jwt.encode({'user_id': str(user.id), 'exp': now_ist + timedelta(minutes=1)}, settings.SECRET_KEY, algorithm='HS256')
            verification_link = f"http://localhost:8000/user/verify/{token}"    
            email_utils = EmailUtils()
            email_utils.send_verification_email( user.email, verification_link)
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            return Response({"access_token": access_token, "refresh_token": refresh_token})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SignInView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(email=email, password=password)
        if user is not None:
            if not user.is_email_verified:
                return Response({'error': 'Email not verified'}, status=status.HTTP_403_FORBIDDEN)
            
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
class LogoutView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)



class RefreshTokenView(APIView):
    def post(self, request):
        refresh_token = request.data.get('refresh')
        try:
            token = RefreshToken(refresh_token)
            # Check if the token is blacklisted
            if RefreshToken.objects.filter(token=refresh_token, blacklisted=True).exists():
                return Response({'error': 'Token blacklisted'}, status=status.HTTP_400_BAD_REQUEST)

            token.blacklist()  # Blacklist the old refresh token
            new_refresh = RefreshToken.for_user(token.user)
            return Response({
                'refresh': str(new_refresh),
                'access': str(new_refresh.access_token),
            }, status=status.HTTP_200_OK)
        except TokenError:
            return Response({'error': 'Invalid refresh token'}, status=status.HTTP_400_BAD_REQUEST)
        

class VerifyEmailView(APIView):
    def get(self, request, token):
        try:
            key = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = UUID(key['user_id'])  # Convert the string back to a UUID
            user = CustomUser.objects.get(id=user_id)
            if user.is_email_verified:
                return Response({'error': 'Email is already verified'}, status=status.HTTP_400_BAD_REQUEST)
            user.is_email_verified = True
            user.save()
            return Response({'email': 'Your email has been activated'}, status=status.HTTP_200_OK)
        except jwt.exceptions.DecodeError as identifier:
            return Response({'error': 'token not valid'}, status=status.HTTP_400_BAD_REQUEST)
        
        except ExpiredSignatureError:
            return Response({"error": "Signature has expired"}, status=status.HTTP_401_UNAUTHORIZED)
        

class ResendEmailView(APIView):
    def post(self, request):
        email = request.data.get("email")
        user = CustomUser.objects.filter(email=email).first()
        if user:
            #sending email 
            now_ist = datetime.now(pytz.timezone('Asia/Kolkata'))
            # Generate a JWT token that expires in 15 minutes
            token = jwt.encode({'user_id': str(user.id), 'exp': now_ist + timedelta(minutes=15)}, settings.SECRET_KEY, algorithm='HS256')
            verification_link = f"http://localhost:8000/user/verify/{token}"    
            email_utils = EmailUtils()
            email_utils.send_verification_email(user.email, verification_link)
            return Response({"message": "Verification email has been sent."})
        return Response({"error": "User not found"}, status=status.HTTP_400_BAD_REQUEST)
    

class ForgotPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')
        user = CustomUser.objects.filter(email=email).first()
        if user:
            now_ist = datetime.now(pytz.timezone('Asia/Kolkata'))

            # Generate a JWT token that expires in 15 minutes
            token = jwt.encode({'user_id': str(user.id), 'exp': now_ist + timedelta(minutes=15)}, settings.SECRET_KEY, algorithm='HS256')
            reset_link = f"http://localhost:8000/user/reset_password/{token}"    
            email_utils = EmailUtils()
            email_utils.send_reset_password_email(user.email, reset_link)
            return Response({"message": "Reset password email has been sent."})
        return Response({"error": "User not found"}, status=status.HTTP_400_BAD_REQUEST)
    



class ResetPasswordView(APIView):
    def post(self, request, token):
        password = request.data.get('password')
        try:
            # Decode the token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload['user_id']
            user = CustomUser.objects.get(id=user_id)
            user.set_password(password)
            user.save()
            return Response({"message": "Password has been reset."})
        except (jwt.DecodeError, jwt.ExpiredSignatureError):
            return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)


class UserInfoApiView(generics.GenericAPIView):
    # authentication_classes = [JWTAuthentication]

    permission_classes = [IsAuthenticated]

    def get_user_info(self, instance):
        user_info_dict = model_to_dict(instance)
        return user_info_dict

    def get(self, request):        
        user_info = UserInfo.objects.get(user=request.user.id)
        return_data = self.get_user_info(user_info)
        return Response({"Status": "Success", "Data":return_data}, status=status.HTTP_200_OK)    

    def post(self, request):
        serializer = UserInfoSerializer(data=request.data, partial=True, context={'user': request.user})
        if serializer.is_valid():
            serializer.save()
            return Response({"Status": "Success", "Data": "User Info Saved Successfully"}, status=status.HTTP_201_CREATED)
        
        return Response({"error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


    def patch(self, request):
        user_info = get_object_or_404(UserInfo, user=request.user.id)
        serializer = UserInfoSerializer(user_info, data=request.data, partial=True, context={'user': request.user})
        if serializer.is_valid():
            serializer.save()
            return Response({"Status": "Success", "Data": "User Info Updated Successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        pass