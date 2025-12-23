from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm, ShippingAddressForm
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import ShippingAddress, CustomUser
from store.models import Order
from django.views.decorators.http import require_POST


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

        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)

            # Handle "Remember Me"
            if not remember_me:
                print("Remember not selected")
                # Session expires when the browser closes
                request.session.set_expiry(0)

            messages.success(request, "Logged in successful")

            if user.role == CustomUser.Roles.DELIVERY_PERSON:
                return redirect("accounts:customer_profile")

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

        if request.user.role == CustomUser.Roles.CUSTOMER:
            form = ShippingAddressForm()
            addresses = ShippingAddress.objects.filter(user=request.user)
            context = {"form": form, "addresses": addresses}
        elif request.user.role == CustomUser.Roles.DELIVERY_PERSON:
            orders = Order.objects.filter(
                delivery_person=request.user.delivery_profile
            ).order_by("updated_at")

            pending_orders = orders.filter(status=Order.Status.ON_THE_WAY)
            delivered_orders = orders.filter(status=Order.Status.DELIVERED)
            context = {
                "orders": orders,
                "pending_orders": pending_orders,
                "delivered_orders": delivered_orders,
            }

    return render(request, "accounts/customer_profile.html", context)


@login_required(login_url="accounts:login_page")
@require_POST
def set_as_delivered(request, order_id):
    try:
        order = Order.objects.get(order_id=order_id)
        order.status = Order.Status.DELIVERED
        order.save(update_fields=["status"])
    except Order.DoesNotExist:
        messages.error(request, "Order not found")

    return redirect("accounts:customer_profile")
