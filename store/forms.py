from django import forms
from .models import Category, Order
from accounts.models import DeliveryPerson


SORTING_CHOICES = [
    ("price_asc", "Price Low to High"),
    ("price_desc", "Price High to Low"),
    ("latest", "Latest"),
    ("oldest", "Oldest"),
]


class ProductFilterForm(forms.Form):
    name = forms.CharField(
        max_length=60,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "search by name"}
        ),
    )

    min_price = forms.DecimalField(
        max_digits=10,
        required=False,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "min. amount"}
        ),
    )

    max_price = forms.DecimalField(
        max_digits=10,
        required=False,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "max. amount"}
        ),
    )

    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={"class": ""}),
    )

    sorting_key = forms.ChoiceField(
        choices=SORTING_CHOICES,
        required=False,
        initial=SORTING_CHOICES[0],
        widget=forms.Select(attrs={"class": "form-control"}),
    )


class OrderChangeForm(forms.ModelForm):

    delivery_person = forms.ModelChoiceField(
        queryset=DeliveryPerson.objects.filter(is_verified=True, is_active=True),
        required=False,
    )

    class Meta:
        model = Order
        fields = ["delivery_person"]
