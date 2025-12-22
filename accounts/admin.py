from django.contrib import admin
from .models import DeliveryPerson, CustomUser
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserChangeForm, CustomUserCreationForm


@admin.register(CustomUser)
class CustomUserModelAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm

    list_display = ("email",)
    ordering = ("email",)

    # EDIT EXISTING USER
    fieldsets = (
        (
            "User Credentials",
            {
                "fields": ("email", "password"),
            },
        ),
        (
            "User Information",
            {
                "fields": ("first_name", "last_name", "role"),
            },
        ),
    )

    # ADD NEW USER
    add_fieldsets = (
        (
            "User Credentials",
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
        (
            "User Information",
            {
                "fields": ("first_name", "last_name", "role"),
            },
        ),
    )


@admin.register(DeliveryPerson)
class DeliveryPersonModelAdmin(admin.ModelAdmin):

    list_display = ["user", "phone_number", "is_verified", "is_active"]

    search_fields = ["user__email", "user__first_name", "user__last_name"]

    list_filter = ["is_active", "is_verified"]

    fieldsets = (
        (
            "Delivery Person Information",
            {
                "fields": ("user", "dob"),
            },
        ),
        (
            "Contact",
            {
                "fields": ("phone_number", "emergency_contact"),
            },
        ),
        (
            "Documents",
            {
                "fields": ("citizenship", "driving_license"),
            },
        ),
        (
            "Vehicle Information",
            {
                "fields": ("vehicle_type", "vehicle_plate_number", "vehicle_color"),
            },
        ),
        (
            "Status",
            {
                "fields": ("is_active", "is_verified"),
            },
        ),
    )
