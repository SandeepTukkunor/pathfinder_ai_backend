from django.urls import path
from .views import SignUpView, SignInView, RefreshTokenView,UserInfoApiView


urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('signin/', SignInView.as_view(), name='signin'),
    path('refresh-token/', RefreshTokenView.as_view(), name='refresh_token'),
    path("user_info/", UserInfoApiView.as_view(), name="user_info")
     
]


