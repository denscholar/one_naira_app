from django.urls import path
from . import views

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    # LOGIN endpoints
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="login"),
    path("user_details/", views.UserAPIView.as_view(), name="user-details"),
    path('profile/', views.UserProfileView.as_view(), name="profile"),
    # JWT Token endpoints
    path("jwt/create/", TokenObtainPairView.as_view(), name="token_create"),
    path("jwt/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("jwt/verify/", TokenVerifyView.as_view(), name="token_verify"),
    # REGISTRATION endpoint
    path("register/", views.RegisterUserView.as_view(), name="register"),
    path(
        "register/phone/",
        views.PhoneNumberRegistrationView.as_view(),
        name="register_with_phone",
    ),
    path(
        "verify_otp/", views.OTPVerificationView.as_view(), name="verify_phone"
    ),
    path(
        "forget_password/",
        views.ForgetPasswordView.as_view(),
        name="forget_password",
    ),
    path(
        "set_new_password/",
        views.SetNewPasswordView.as_view(),
        name="set_new_password",
    ),
    path(
        "regenerate_otp/", views.RegenerateOTP.as_view(), name="regenerate-otp"
    ),

]
