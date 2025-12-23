from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm, ShippingAddressForm
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import ShippingAddress


def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Account created successfully! You can now login."
            )
            return redirect(reverse("accounts:login_page"))
    else:
        form = CustomUserCreationForm()
    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        remember_me = request.POST.get("remember")
        print("remeber", remember_me)
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)

            # Handle "Remember Me"
            if not remember_me:
                print("Remember not selected")
                # Session expires when the browser closes
                request.session.set_expiry(0)

            messages.success(request, "Logged in successful")
            return redirect(reverse("store:home_page"))

        messages.error(request, "Email or password is incorrect")

    return render(request, "accounts/login.html")


def logout_view(request):
    logout(request)
    return redirect(reverse("accounts:login_page"))


@login_required(login_url="accounts:login_page")
def customer_profile(request):
    if request.method == "POST":
        form = ShippingAddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            return redirect("accounts:customer_profile")
    else:
        form = ShippingAddressForm()
        addresses = ShippingAddress.objects.filter(user=request.user)
    context = {"form": form, "addresses": addresses}
    return render(request, "accounts/customer_profile.html", context)
