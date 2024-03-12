from django.urls import path
from .views import SignUpView, SignInView, RefreshTokenView,UserInfoApiView, VerifyEmailView, ResendEmailView,\
ForgotPasswordView, ResetPasswordView, LogoutView


urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', SignInView.as_view(), name='signin'),
    path('refresh-token/', RefreshTokenView.as_view(), name='refresh_token'),
    path("user_info/", UserInfoApiView.as_view(), name="user_info"),
    path('verify/<str:token>/', VerifyEmailView.as_view(), name='verify_email'),
    path('resend_email/', ResendEmailView.as_view(), name='resend_email'),
    path('forgot_password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset_password/<str:token>/', ResetPasswordView.as_view(), name='reset_password'),
    path('logout/', LogoutView.as_view(), name='logout'),



     
]


