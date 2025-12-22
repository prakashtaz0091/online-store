from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.base_user import BaseUserManager
from django.utils import timezone
from django.core.exceptions import ValidationError


class CustomUserManager(BaseUserManager):
    """Custom user model manager where email is the unique identifiers for authentication instead of usernames."""

    def create_user(self, email, password, **extra_fields):
        """Create and save a user with the given email and password."""
        if not email:
            raise ValueError(_("The Email must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):

    class Role(models.TextChoices):
        CUSTOMER = "customer", "Customer"
        DELIVERY_PERSON = "delivery_person", "Delivery Person"
        INVENTORY_STAFF = "inventory_staff", "Inventory Staff"

    username = None
    email = models.EmailField(_("email address"), unique=True)
    # avatar_url = models.URLField(blank=True, null=True)

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.lower()
        super().save(*args, **kwargs)


class DeliveryPerson(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="delivery_profile"
    )
    dob = models.DateField()

    # account status
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    approved_at = models.DateTimeField(null=True, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    # contact
    phone_number = models.CharField(max_length=20)
    emergency_contact = models.CharField(max_length=15, blank=True)

    # location
    current_latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    current_longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    last_location_update = models.DateTimeField(null=True, blank=True)

    # documents
    citizenship = models.FileField(
        upload_to="delivery_person/citizenships/",
        null=True,
        blank=True,
        help_text="front and back side of the citizenship card in a pdf format",
    )
    driving_license = models.FileField(
        upload_to="delivery_person/driving_licenses/", null=True, blank=True
    )

    # vehicle info
    class VehicleType(models.TextChoices):
        BICYCLE = "bicycle", "Bicycle"
        MOTORCYCLE = "motorcycle", "Motorcycle"
        CAR = "car", "Car"
        VAN = "van", "Van"
        TRUCK = "truck", "Truck"

    vehicle_type = models.CharField(max_length=20, choices=VehicleType.choices)
    vehicle_plate_number = models.CharField(max_length=20)
    vehicle_color = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        default="black",
        help_text="color of the vehicle",
    )

    def __str__(self):
        return self.user.get_full_name() or self.user.email

    def clean(self):
        super().clean()

        # dob
        today = timezone.now().date()
        if self.dob:
            if self.dob > today:
                raise ValidationError("Date of birth cannot be in the future")
            if self.dob > (today - timezone.timedelta(days=365 * 18)):
                raise ValidationError("Delivery person must be at least 18 years old")

        # citizenship
        if self.citizenship:
            if self.citizenship.size > 5 * 1024 * 1024:
                raise ValidationError("Citizenship file size cannot exceed 5MB")

        # driving license
        if self.driving_license:
            if self.driving_license.size > 5 * 1024 * 1024:
                raise ValidationError("Driving license file size cannot exceed 5MB")

        # check if verified
        if self.is_verified:
            if not self.citizenship:
                raise ValidationError("Citizenship is required")
            if not self.driving_license:
                raise ValidationError("Driving license is required")

    def save(self, *args, **kwargs):
        self.full_clean()

        # if verified save approved_at
        if self.is_verified:
            self.approved_at = timezone.now()

        super().save(*args, **kwargs)
