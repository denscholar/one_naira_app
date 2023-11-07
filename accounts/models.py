from django.db import models
from django.conf import settings
from django.contrib.auth.hashers import is_password_usable
from django.contrib.auth.hashers import check_password, make_password

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, password, **extra_fields):
        """
        Creates and saves a User with the given phone_number, password, and any extra fields.
        """
       

        if not phone_number:
            raise ValueError("Phone number is required")

        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, phone_number, password, **extra_fields):
        """
        Creates and saves a superuser with the given phone_number, password, and any extra fields.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault('is_verified', True)


        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        if extra_fields.get("is_active") is not True:
            raise ValueError("Superuser must have is_active=True.")
        if extra_fields.get("is_verified") is not True:
            raise ValueError("Superuser must have is_verified=True.")


        return self.create_user(phone_number, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    GENDER_CHOICES_LIST = (
        ('male', 'male'),
        ('female', 'female'),
    )
    phone_number = models.CharField(
        max_length=14,
        unique=True,
        null=False,
        blank=False,
        error_messages={
            "null": "Phone number cannot be null.",
            "blank": "Phone number cannot be blank.",
            "max_length": "Phone number must be at most %(max_length)d characters.",
        },
    
    )
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email_address = models.EmailField(max_length=254, null=True, blank=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(choices=GENDER_CHOICES_LIST, max_length=15, blank=None, null=True)
    transaction_pin = models.CharField(
        default="0000",
        max_length=256,
        help_text="The transaction pin of the user",
    )
    otp = models.CharField(max_length=6, null=True, blank=True)
    otp_expire = models.DateTimeField(blank=True, null=True)  # otp expire date
    max_otp_try = models.CharField(
        max_length=2, default=settings.MAX_OTP_TRY
    )  # number of otp generated trials
    otp_max_out = models.DateTimeField(blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_support_level1 = models.BooleanField(default=False)
    is_support_level2 = models.BooleanField(default=False)
    is_accountant1 = models.BooleanField(default=False)
    is_accountant2 = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "phone_number"

    objects = CustomUserManager()

    def __str__(self):
        return self.phone_number

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"


    def save(self, *args, **kwargs):
        """
        Hashes the transaction pin if it is not already hashed and saves the updated model instance.
        """
        if self.transaction_pin and not self.transaction_pin.startswith("pbkdf2_sha256"):
            self.transaction_pin = make_password(str(self.transaction_pin))
        super().save(*args, **kwargs)


class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="profile")
    profile_picture = models.ImageField(
        upload_to="profile_images/", default='avatar.png'
    )

    def __str__(self):
        return self.user.first_name + ' ' + f"profile"
    

