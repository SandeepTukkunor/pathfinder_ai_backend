from datetime import datetime
from tokenize import TokenError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from user.models import CustomUser


from .serializers import UserSerializer
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
        



class GetAllUsers(APIView):
    # authentication_classes = [JWTAuthentication]

    permission_classes = [IsAuthenticated]
    

    def get(self, request):
        CustemUser = CustomUser.objects.all()

        return Response({"Status": "Success", "Data": "Users Fetched Succefully"})