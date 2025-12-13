from django.db import models
from django.contrib.auth.models import AbstractUser
from cloudinary.models import CloudinaryField

# Create your models here.



class User(AbstractUser):
    # remove unused fields from Django default
    first_name = None
    last_name = None
    username = None

    # login using email
    email = models.EmailField(unique=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]  # only needed for createsuperuser

    # Basic details
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, unique=True, null=True, blank=True)

    # Profile Image (Cloudinary is better)
    profile_image = CloudinaryField(
        "image",
        folder="profile_pics",
        null=True,
        blank=True,
        default="default_v0m4nt",
    )

    # Gender & DOB
    gender = models.CharField(
        max_length=10,
        choices=[
            ("male", "Male"),
            ("female", "Female"),
            ("other", "Other"),
        ],
        null=True,
        blank=True,
    )

    dob = models.DateField(null=True, blank=True)

    # User roles
    role = models.CharField(
        max_length=20,
        choices=[
            ("user", "User"),
            ("admin", "Admin"),
        ],
        default="user",
    )

    # Referral System
    referral_code = models.CharField(max_length=20, unique=True, blank=True)
    referred_by = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    # timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email
