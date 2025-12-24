from django import forms
from .models import Category, Order, Review
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

    # check if delivery_person is set on save
    def save(self, commit=True):
        if self.cleaned_data["delivery_person"]:
            self.instance.status = Order.Status.ON_THE_WAY
        return super().save(commit)


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["text", "rating"]
        widgets = {
            "text": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Write your review here",
                }
            ),
            "rating": forms.HiddenInput(),
        }

    def __init__(self, *args, user=None, product=None, **kwargs):
        self.user = user
        self.product = product
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        if not self.user or not self.product:
            raise ValueError("user and product are required")

        review, _ = Review.objects.update_or_create(
            user=self.user,
            product=self.product,
            defaults=self.cleaned_data,
        )
        return review
