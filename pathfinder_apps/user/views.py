from datetime import datetime
from tokenize import TokenError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict

from .models import CustomUser, UserInfo


from .serializers import UserSerializer, UserInfoSerializer
from datetime import date

class SignUpView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            return Response({"access_token": access_token, "refresh_token": refresh_token})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SignInView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(username=email, password=password)
        print(user)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)



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