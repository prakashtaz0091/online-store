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

    class Roles(models.TextChoices):
        ADMIN = "admin", "Admin"
        DELIVERY_PERSON = "delivery_person", "Delivery Person"
        CUSTOMER = "customer", "Customer"

    username = None
    email = models.EmailField(_("email address"), unique=True)
    # avatar_url = models.URLField(blank=True, null=True)

    role = models.TextField(choices=Roles.choices, default=Roles.CUSTOMER)

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
    dob = models.DateField(help_text="Date of birth of Delivery Person")

    # contact information
    phone_number = models.CharField(max_length=15, help_text="Normal contact")
    emergency_contact = models.CharField(
        max_length=15, help_text="Contact number for emergency cases"
    )

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
    driving_license = models.ImageField(
        upload_to="delivery_person/driving_licenses/",
        null=True,
        blank=True,
        help_text="Clear scanned image of driving license",
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
        help_text="Color of the vehicle",
    )

    # account status
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    approved_at = models.DateTimeField(null=True, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.email

    def clean(self):
        super().clean()

        today = timezone.now().date()

        if self.user.role != CustomUser.Roles.DELIVERY_PERSON:
            raise ValidationError("Please choose the user with role 'delivery person'")

        if self.dob > (today - timezone.timedelta(days=18 * 365)):
            raise ValidationError("Delivery person must be at least 18 years old")

        if self.citizenship and self.citizenship.size > 5 * 1024 * 1024:
            raise ValidationError("Citizenship pdf file size must be less than 5 MB")

        if self.driving_license and self.driving_license.size > 2 * 1024 * 1024:
            raise ValidationError(
                "Driving license image file size must be less than 2 MB"
            )

        if self.is_verified == True and (
            not self.citizenship or not self.driving_license
        ):
            raise ValidationError(
                "Delivery person cannot be verified without citizenship and driving license"
            )

    def save(self, *args, **kwargs):
        self.full_clean()

        # if verified save approved_at
        if self.is_verified == True:
            self.approved_at = timezone.now()

        super().save(*args, **kwargs)


class ShippingAddress(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="shipping_addresses"
    )
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address_line = models.TextField()
    city = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=20)

    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    last_location_update = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = [("latitude", "longitude")]

    def __str__(self):
        return self.full_name
