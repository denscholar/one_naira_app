from api import settings
from django.conf import settings
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.core.validators import MinLengthValidator, MaxLengthValidator
from .utils import get_full_profile_picture_url
from .models import CustomUser, UserProfile


# PHONE VERIFICATION SERIALIZER
class PhoneNumberRegistrationSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField()

    class Meta:
        model = CustomUser
        fields = ("phone_number",)

    def custom_phone_number_validation(self, value):
        if not value:
            raise serializers.ValidationError("Phone number is required.")

        # Perform your phone number validation logic here
        if (
            len(value) != 11
            and not value.startswith("080")
            and not value.startswith("+234")
        ):
            raise serializers.ValidationError(
                "Phone number must start with '+234' or '080' and be 11 digits long."
            )

        if len(value) == 11:
            value = "+234" + value[1:]
        elif len(value) == 13:
            value = "+" + value

        return value

    def validate(self, data):
        phone_number = data.get("phone_number")
        validated_phone_number = self.custom_phone_number_validation(
            phone_number)
        data["phone_number"] = validated_phone_number
        return data


# OTP VERIFICATION
class OTPVerificationSerializer(serializers.ModelSerializer):
    otp = serializers.CharField(max_length=6)

    class Meta:
        model = CustomUser
        fields = ("otp",)


class RegisterUserSerializer(serializers.ModelSerializer):

    """
    This code defines two CharField attributes for the password1 and password2 fields, respectively. These fields are write-only and have a minimum length of settings.MIN_PASSWORD_LENGTH. If the password entered by the user is shorter than settings.MIN_PASSWORD_LENGTH, an error message is returned.
    """

    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    email_address = serializers.EmailField(required=False, allow_blank=True)
    phone_number = serializers.CharField(max_length=14, required=True)
    password1 = serializers.CharField(
        min_length=settings.MIN_PASSWORD_LENGTH,
        error_messages={
            "min_length": "password must be longer than {settings.MIN_PASSWORD_LENGTH} characters".format(
                settings=settings
            )
        },
    )
    password2 = serializers.CharField(
        min_length=settings.MIN_PASSWORD_LENGTH,
        error_messages={
            "min_length": "password must be longer than {settings.MIN_PASSWORD_LENGTH} characters".format(
                settings=settings
            )
        },
    )

    class Meta:
        model = CustomUser
        fields = (
            "first_name",
            "last_name",
            "email_address",
            "phone_number",
            "gender",
            "password1",
            "password2",
        )

    def validate(self, data):
        phone_number = data.get("phone_number", '')

        if data["password1"] != data["password2"]:
            raise serializers.ValidationError("Password do not match")
        if len(data["password1"]) < settings.MIN_PASSWORD_LENGTH:
            raise serializers.ValidationError(
                "Password must be at least {settings.MIN_PASSWORD_LENGTH} characters long.".format(
                    settings=settings
                )
            )
        if data.get("email_address") == "":
            del data["email_address"]

        if len(phone_number) == 11:
            phone_number = "+234" + phone_number[1:]
        elif len(phone_number) == 13:
            phone_number = "+" + phone_number
        elif len(phone_number) == 14:
            pass
        else:
            raise serializers.ValidationError(
                "Phone number must start with '+234' or '080' "
            )
        data["phone_number"] = phone_number
        return data


    def update(self, instance, validated_data):

        instance.first_name = validated_data.get(
            "first_name", instance.first_name)
        instance.last_name = validated_data.get(
            "last_name", instance.last_name)
        instance.email_address = validated_data.get(
            "email_address", instance.email_address
        )
        instance.set_password(validated_data["password1"])
        instance.is_active = True
        instance.save()
        Token.objects.create(user=instance)
        return instance


class SetNewPasswordSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(
        write_only=True,
        min_length=settings.MIN_PASSWORD_LENGTH,
        error_messages={
            "min_length": f"password must be longer than {settings.MIN_PASSWORD_LENGTH} characters"
        },
    )

    password2 = serializers.CharField(
        write_only=True,
        min_length=settings.MIN_PASSWORD_LENGTH,
        error_messages={
            "min_length": f"password must be longer than {settings.MIN_PASSWORD_LENGTH} characters"
        },
    )

    class Meta:
        model = CustomUser
        fields = (
            "password1",
            "password2",
        )

    def validate(self, data):
        if data["password1"] != data["password2"]:
            raise serializers.ValidationError("Password do not match")
        if len(data["password1"]) < settings.MIN_PASSWORD_LENGTH:
            raise serializers.ValidationError(
                f"Password must be at least {settings.MIN_PASSWORD_LENGTH} characters long.".format(
                    settings=settings
                )
            )
        return data

    def update(self, instance, validated_data):
        instance.set_password(validated_data["password1"])
        instance.save()
        return instance


class LoginSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(required=True)

    class Meta:
        model = CustomUser
        fields = ("phone_number", "password")

    def validate(self, data):
        phone_number = data.get("phone_number")
        password = data.get("password")

        if len(phone_number) == 11:
            phone_number = "+234" + phone_number[1:]
        elif len(phone_number) == 13:
            phone_number = "+" + phone_number
        elif len(phone_number) == 14:
            pass
        else:
            raise serializers.ValidationError("Incorrect phone number")
        data["phone_number"] = phone_number

        return data


class ForgetPasswordSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(required=True)

    class Meta:
        model = CustomUser
        fields = ("phone_number",)

    def validate(self, data):
        phone_number = data.get("phone_number")
        if len(phone_number) == 11:
            phone_number = "+234" + phone_number[1:]
        elif len(phone_number) == 13:
            phone_number = "+" + phone_number
        elif len(phone_number) == 14:
            pass
        else:
            raise serializers.ValidationError(
                "Phone number must start with '+234' or '080' "
            )
        data["phone_number"] = phone_number
        return data


class TransactionPinSerializer(serializers.ModelSerializer):
    transaction_pin = serializers.CharField(
        required=True,
        validators=[
            MinLengthValidator(4, message="Pin must be four digits long."),
            MaxLengthValidator(4, message="Pin must be four digits long."),
        ],
    )

    class Meta:
        model = CustomUser
        fields = ("transaction_pin",)


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ("profile_picture",)

    def update(self, instance, validated_data):
        instance.profile_picture = validated_data.get(
            "profile_picture", instance.profile_picture
        )
        instance.save()
        return instance
    
class UserDetailsSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    email_address = serializers.CharField(read_only=True)
    profile_picture = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email_address', 'profile_picture')

    def get_profile_picture(self, obj):
        return get_full_profile_picture_url(obj)
