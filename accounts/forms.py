from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, ShippingAddress
from django.contrib.auth.forms import ReadOnlyPasswordHashField


class CustomUserCreationForm(UserCreationForm):
    password1 = forms.CharField(
        label="Password", widget=forms.PasswordInput(attrs={"class": "form-control"})
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )

    class Meta:
        model = CustomUser
        fields = ("email", "first_name", "last_name")
        widgets = {"email": forms.EmailInput(attrs={"class": "form-control"})}


class CustomUserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = CustomUser
        fields = ("email", "password", "first_name", "last_name", "role")


class ShippingAddressForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = [
            "full_name",
            "phone",
            "address_line",
            "city",
            "postal_code",
            "latitude",
            "longitude",
        ]
        widgets = {
            "latitude": forms.HiddenInput(),
            "longitude": forms.HiddenInput(),
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "address_line": forms.Textarea(attrs={"class": "form-control"}),
            "city": forms.TextInput(attrs={"class": "form-control"}),
            "postal_code": forms.TextInput(attrs={"class": "form-control"}),
        }
