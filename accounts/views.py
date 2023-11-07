from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.utils.decorators import method_decorator
from django.db.models import Q
import requests
from accounts.decorators import check_user_role
from rest_framework.parsers import MultiPartParser, FormParser
from .models import CustomUser
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.contrib.auth.hashers import check_password
from datetime import datetime, timedelta
from drf_yasg import openapi
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.sessions.backends.db import SessionStore
from .tokens import create_jwt_pair_for_user
from .serializers import UserDetailsSerializer, UserProfileSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authtoken.models import Token
from .token import create_jwt_pair_for_user

from .serializers import (
    ForgetPasswordSerializer,
    LoginSerializer,
    RegisterUserSerializer,
    SetNewPasswordSerializer,
    OTPVerificationSerializer,
    PhoneNumberRegistrationSerializer,
)
from rest_framework.views import APIView
from django.utils import timezone
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny, IsAdminUser
from django.core.exceptions import ObjectDoesNotExist
from .permissions import (
    is_support_level1,
    is_support_level2,
    IsAdmin,
    isAccountant1,
    isAccountant2,
)
import random
from django.conf import settings
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.decorators import action

from drf_yasg.utils import swagger_auto_schema
from .utils import send_otp, generateRandomOTP


# phone number registration
class PhoneNumberRegistrationView(APIView):
    @swagger_auto_schema(
        operation_summary="This is responsible for registering/validating a user with phone number and can also be used to regenerate OTP",
        operation_description="This endpoint registers/validate a users phone number. Note: this endpoint will also be used to regenerate OTP in case the user fails to receive the OTP",
        request_body=PhoneNumberRegistrationSerializer,
    )
    def post(self, request):
        otp_expire = timezone.now() + timedelta(minutes=10)
        otp = generateRandomOTP(100000, 999999)
        serializer = PhoneNumberRegistrationSerializer(data=request.data)
        # serializer.is_valid(raise_exception=True)

        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as validation_error:
            return Response(
                {"error": "Phone number not valid"}, status=status.HTTP_400_BAD_REQUEST
            )

        validated_data = serializer.validated_data
        phone_number = validated_data.get("phone_number")

        unverified_user = CustomUser.objects.filter(
            phone_number=phone_number,
            is_active=False,
            is_verified=False,
        ).first()
        in_active_user = CustomUser.objects.filter(
            phone_number=phone_number,
            is_active=False,
            is_verified=True,
        ).first()
        current_user = CustomUser.objects.filter(
            phone_number=phone_number,
            is_active=True,
            is_verified=True,
        ).first()

        # check if this instance is already in the database
        if unverified_user:
            max_otp_try = int(unverified_user.max_otp_try) - 1

            if (
                int(unverified_user.max_otp_try) == 0
                and timezone.now() < unverified_user.otp_max_out
            ):
                return Response(
                    "You have tried many times. Please, try after an hour.",
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # update the OTP in the database
            unverified_user.otp = otp

            # update the otp_expire in the database
            unverified_user.otp_expire = otp_expire

            # update the max_otp_try in the database
            unverified_user.max_otp_try = max_otp_try

            if max_otp_try == 0:
                unverified_user.otp_max_out = timezone.now() + timedelta(hours=1)
            elif max_otp_try == -1:
                unverified_user.max_otp_try = settings.MAX_OTP_TRY
            else:
                unverified_user.otp_max_out = None
                unverified_user.max_otp_try = max_otp_try

            unverified_user.save()

            try:
                send_otp(phone_number=phone_number, otp=otp)
                response = {"message": "An OTP has been sent to your mobile number"}
            except requests.ConnectionError:
                response = {
                    "error": "There was a problem connecting to the server. Please check your internet connection and try again later."
                }
                return Response(
                    data=response, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            except requests.Timeout:
                response = {
                    "error": "There was a problem connecting to the server. Please check your internet connection and try again later."
                }
                return Response(
                    data=response, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            except Exception as e:
                return Response(
                    {"error": f"An unexpected error occurred: {e}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            return Response(data=response, status=status.HTTP_201_CREATED)

        elif in_active_user:
            return Response(
                {"Phone number is verified, proceed to register"},
                status=status.HTTP_307_TEMPORARY_REDIRECT,
            )

        elif current_user:
            return Response(
                {"Phone number already exist. Please login"},
                status=status.HTTP_308_PERMANENT_REDIRECT,
            )
        # the else block handles user not existing in the database
        else:
            try:
                send_otp(phone_number=phone_number, otp=otp)
                new_user = CustomUser.objects.create(
                    phone_number=phone_number, otp=otp, otp_expire=otp_expire
                )

                response = {
                    "Message": "An OTP has been sent to your mobile number",
                }

                return Response(data=response, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response(
                    {"error": f"An unexpected error occurred: {e}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )


# VERIFY OTP
class OTPVerificationView(APIView):
    @swagger_auto_schema(
        operation_summary="This is responsible for verifying a user with an OTP",
        operation_description="This endpoint verifies a user with his phone number",
        request_body=OTPVerificationSerializer,
    )
    def post(self, request):
        otp = request.data.get("otp", "")
        user = request.user

        try:
            instance = CustomUser.objects.get(
                Q(is_active=True, is_verified=True, otp=otp) | 
                Q(is_active=False, is_verified=False, otp=otp)
            )
           
        except CustomUser.DoesNotExist:
            return Response(
                "Wrong OTP, please enter the correct OTP",
                status=status.HTTP_400_BAD_REQUEST,
            )

        if timezone.now() > instance.otp_expire:
            return Response(
                {"message": "OTP has expired"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        instance.is_verified = True
        instance.max_otp_try = settings.MAX_OTP_TRY
        instance.otp_max_out = None
        instance.save()

        return Response("Verification successful", status=status.HTTP_200_OK)


# regenerate OTP
class RegenerateOTP(APIView):
    @swagger_auto_schema(
        operation_summary="This endpoint is responsible for regenerating OTP if expired",
        operation_description="This endpoint regenerate OTP after expiration period. Note: the session ID is included in the response headers under the 'X-Session-Id' field. This session ID can be used to maintain user sessions across requests. To include the session ID in subsequent requests, the frontend/client-side developer should extract the session ID from the 'X-Session-Id' field in the response headers and include it in the 'Cookie' header of subsequent requests. Please refer to your HTTP client library's documentation on how to do this.",
        manual_parameters=[
            openapi.Parameter(
                "session_id",
                openapi.IN_HEADER,
                description="The session ID extracted from the 'X-Session-Id' field in the response headers.",
                type=openapi.TYPE_STRING,
            )
        ],
    )
    def post(self, request):
        cookie = request.headers.get("Cookie")
        if cookie:
            cookie_list = cookie.split("; ")
            for c in cookie_list:
                if c.startswith("sessionid="):
                    sessionid = c.split("=")[1]
                elif c.startswith("csrftoken="):
                    csrftoken = c.split("=")[1]

        session = SessionStore(session_key=sessionid)
        phone_number = session.get("phone_number")

        instance = CustomUser.objects.filter(phone_number=phone_number).first()

        if not instance:
            return Response("User not found", status=status.HTTP_404_NOT_FOUND)

        if int(instance.max_otp_try) == 0 and timezone.now() < instance.otp_max_out:
            return Response(
                "Max OTP try reached, try after an hour.",
                status=status.HTTP_400_BAD_REQUEST,
            )
        otp = generateRandomOTP(100000, 999999)
        otp_expire = timezone.now() + timedelta(minutes=10)
        max_otp_try = int(instance.max_otp_try) - 1

        instance.otp = otp
        instance.otp_expire = otp_expire
        instance.max_otp_try = max_otp_try

        if max_otp_try == 0:
            instance.otp_max_out = timezone.now() + timedelta(hours=1)
        elif max_otp_try == -1:
            instance.max_otp_try = settings.MAX_OTP_TRY
        else:
            instance.otp_max_out = None
            instance.max_otp_try = max_otp_try
        instance.save()
        send_otp(instance.phone_number, otp)

        return Response(
            "successfully re-generated the new otp", status=status.HTTP_200_OK
        )


class RegisterUserView(APIView):
    @swagger_auto_schema(
        operation_summary="This endpoint is responsible for registering a user",
        operation_description="This endpoint register a user",
        request_body=RegisterUserSerializer,
    )
    def post(self, request):
        data = request.data
        phone_number = request.data.get("phone_number")

        try:
            inactive_verified_user = CustomUser.objects.get(
                phone_number=phone_number, is_active=False, is_verified=True
            )
        except CustomUser.DoesNotExist:
            return Response(
                {"message": "Unverified phone number, please check the number"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = RegisterUserSerializer(instance=inactive_verified_user, data=data)
        if serializer.is_valid():
            serializer.save()
            response = {"message": "Account created successfully, proceed to login"}
            return Response(response, status=status.HTTP_201_CREATED)
        return Response(response, status=status.HTTP_400_BAD_REQUEST)


# login a user
class LoginView(APIView):
    @swagger_auto_schema(
        operation_summary="This endpoint is responsible for logging in a registered user",
        operation_description="This endpoint logs in a user",
        request_body=LoginSerializer,
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data.get("phone_number")
        password = serializer.validated_data.get("password")

        try:
            user = CustomUser.objects.get(
                phone_number=phone_number, is_active=True, is_verified=True
            )
        except ObjectDoesNotExist:
            return Response(
                data={"message": "Phone number does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not check_password(password, user.password):
            return Response(
                data={"message": "Wrong password"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        new_user = authenticate(request, phone_number=phone_number, password=password)

        if user is not None:
            tokens = create_jwt_pair_for_user(new_user)
            response = {
                "message": "Login successful",
                "token": tokens,
                "phone_number": user.phone_number,
                "user": {
                    "fname": user.first_name,
                    "lname": user.last_name,
                },
            }
            return Response(data=response, status=status.HTTP_200_OK)
        else:
            return Response(
                data={"message": "Invalid phone number or password"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ForgetPasswordView(APIView):
    @swagger_auto_schema(
        operation_summary="This endpoint is responsible for changing a user's password",
        operation_description="This endpoint takes the phone number of the user, sends an OTP for verification",
        request_body=ForgetPasswordSerializer,
    )
    def post(self, request):
        data = request.data
        # the phone number from user input
        phone_number = data.get("phone_number")

        # handle phone number logic
        if phone_number.startswith("+234"):
            print('phone number real')
        else:
            phone_number = "+234" + phone_number[1:]
            print(phone_number)
            

        try:
            user = CustomUser.objects.get(phone_number=phone_number)
        except CustomUser.DoesNotExist:
            return Response(
                {"error": "User not found for the given phone number"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # create a token
        token, created = Token.objects.get_or_create(user=user)

        otp = generateRandomOTP(100000, 999999)
        otp_expire = timezone.now() + timedelta(minutes=10)
        send_otp(phone_number, otp)

        # update the user details in the database
        user.otp = otp
        user.otp_expire = otp_expire
        user.save()

        return Response(
            {
                "message": "OTP has been sent to your registered phone number",
                "token": token.key,
            },
            status=status.HTTP_200_OK,
        )


class SetNewPasswordView(APIView):
    authentication_classes = [TokenAuthentication]

    @swagger_auto_schema(
        operation_summary="This endpoint is responsible for setting a new password",
        operation_description="""
        This endpoint sets a new password for a user. Include the token in the 'Authorization' header as follows: `Authorization: Token <YOUR_TOKEN_HERE>`
        """,
        request_body=SetNewPasswordSerializer,
    )
    def post(self, request):
        serializer = SetNewPasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            new_password = serializer.validated_data.get("password1")
            user.set_password(new_password)
            user.save()
            return Response(
                {"message": "Password changed successfully"}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    # authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="This endpoint is responsible for logging tthe user out of the application",
        operation_description="""
        This endpoint logs out the user from the application`
        """,
    )
    def post(self, request):
        user = request.user
        user.create_jwt_pair_for_user(user).delete()
        return Response(
            data={"message": "You have been logged out"}, status=status.HTTP_200_OK
        )


class UserProfileView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="This endpoint is responsible for user editing their profile image",
        operation_description="""
        This endpoint allows user to edit their profile image>`
        """,
        request_body=UserProfileSerializer,
    )
    def put(self, request, format=None):
        user = request.user
        profile = user.profile

        serializer = UserProfileSerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            response = {
                "message": "Profile image updated successfully",
            }
            return Response(data=response, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            current_user = request.user
            serializer = UserDetailsSerializer(current_user)

            response = {"data": serializer.data}

            return Response(data=response, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(
                {"message": "You are not authorized to view this user"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
