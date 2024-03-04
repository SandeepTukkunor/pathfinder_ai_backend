from django.urls import path
from .views import SignUpView, SignInView, RefreshTokenView, GetAllUsers


urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('signin/', SignInView.as_view(), name='signin'),
    path('refresh-token/', RefreshTokenView.as_view(), name='refresh_token'),
    path("calculate_age/", GetAllUsers.as_view(),  name = 'calculate_age'),
     
]


