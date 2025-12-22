from django.contrib import admin
from .models import CustomUser, DeliveryPerson
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm


# admin.site.register(CustomUser)
@admin.register(CustomUser)
class CustomUserModelAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm

    list_display = ("email", "first_name", "last_name")
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


# admin.site.register(DeliveryPerson)
@admin.register(DeliveryPerson)
class DeliveryPersonModelAdmin(admin.ModelAdmin):
    list_display = ("user", "phone_number", "dob", "is_verified", "approved_at")

    search_fields = (
        "user__email",
        "user__first_name",
        "user__last_name",
        "phone_number",
    )

    list_filter = ("vehicle_color", "is_verified")

    fieldsets = (
        ("Basic Information", {"fields": ("user", "dob")}),
        ("Contact Information", {"fields": ("phone_number", "emergency_contact")}),
        ("Documents", {"fields": ("citizenship", "driving_license")}),
        (
            "Vehicle Information",
            {"fields": ("vehicle_type", "vehicle_plate_number", "vehicle_color")},
        ),
        (
            "Account Information",
            {"fields": ("is_active", "is_verified")},
        ),
    )
