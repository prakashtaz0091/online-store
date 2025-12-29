from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Cart, CartProduct, Order, OrderItem, Payment, Review
from django.core.paginator import Paginator
from .forms import ProductFilterForm, ReviewForm
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F, Sum, ExpressionWrapper, DecimalField
from .utils import generate_order_id
from django.db import transaction, IntegrityError
import requests
import json
from decimal import Decimal
from django.conf import settings

from django.views.decorators.cache import cache_page
from django.core.cache import cache
from . import signals


def home(request):

    featured_products = (
        Product.objects.filter(featured=True)
        .order_by("-created_at")[:8]
        .only("name", "price", "image")
    )

    context = {"products": featured_products}

    return render(request, "store/home.html", context)


@cache_page(10)
def products(request):
    print("recomputing products----------------------------------")
    products = Product.objects.all()

    filter_form = ProductFilterForm(request.GET)
    if filter_form.is_valid():
        if filter_form.cleaned_data.get("name"):
            products = products.filter(
                name__icontains=filter_form.cleaned_data.get("name")
            )

        if filter_form.cleaned_data.get("min_price"):
            products = products.filter(
                price__gte=filter_form.cleaned_data.get("min_price")
            )

        if filter_form.cleaned_data.get("max_price"):
            products = products.filter(
                price__lte=filter_form.cleaned_data.get("max_price")
            )

        if filter_form.cleaned_data.get("categories"):
            products = products.filter(
                categories__in=filter_form.cleaned_data.get("categories")
            )

        sorting_key = filter_form.cleaned_data.get("sorting_key")
        if sorting_key:
            if sorting_key == "price_asc":
                products = products.order_by("price")
            elif sorting_key == "price_desc":
                products = products.order_by("-price")
            elif sorting_key == "oldest":
                products = products.order_by("created_at")
            elif sorting_key == "latest":
                products = products.order_by("-created_at")

    products_paginator = Paginator(products, 16)
    page_number = request.GET.get("page")
    page_obj = products_paginator.get_page(page_number)

    context = {
        "products": page_obj,
        "filter_form": filter_form,
    }
    return render(request, "store/products.html", context)


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)

    context = {"product": product}

    return render(request, "store/product_detail.html", context)


@login_required(login_url=reverse_lazy("accounts:login_page"))
def add_to_cart(request, pk):
    try:
        product = get_object_or_404(Product, pk=pk)
        logged_in_user = request.user
        cart, created = Cart.objects.get_or_create(user=logged_in_user)

        if CartProduct.objects.filter(product=product, cart=cart).exists():
            messages.success(request, "Product already in your cart")
            return redirect("store:product_detail_page", pk=pk)

        quantity = int(request.POST.get("quantity"))
        if quantity < 0:
            messages.error(request, "Quantify cannot be zero")
            return redirect("store:product_detail_page", pk=pk)

        CartProduct.objects.create(product=product, cart=cart, quantity=quantity)
        messages.success(request, "Product added to cart successfully")
    except Exception as e:
        print(e)
        messages.error(request, "Adding product to cart failed")

    return redirect("store:product_detail_page", pk=pk)


@login_required(login_url=reverse_lazy("accounts:login_page"))
def remove_from_cart(request, pk):
    try:
        cart_item = CartProduct.objects.get(pk=pk)
    except CartProduct.DoesNotExist:
        messages.error(request, "Cart item doesn't exists")

    except Exception as e:
        print(e)
        messages.error(request, "Removing item from cart failed")
    else:
        cart_item.delete()
        messages.success(request, "Cart item removed successful")

    return redirect("store:cart_page")


@login_required(login_url=reverse_lazy("accounts:login_page"))
def update_cart(request, pk):
    try:
        cart_item = CartProduct.objects.get(pk=pk)
    except CartProduct.DoesNotExist:
        messages.error(request, "Cart item doesn't exists")

    except Exception as e:
        print(e)
        messages.error(request, "Updating item from cart failed")
    else:
        try:
            updated_quantity = int(request.POST.get("quantity"))
        except ValueError:
            messages.error(request, "Quantity must be a number")
        else:
            if updated_quantity < 0:
                messages.error(request, "Quantity can't be less than 1")

            cart_item.quantity = updated_quantity
            cart_item.save()
            messages.success(request, "Cart item updated successful")

    return redirect("store:cart_page")


@login_required(login_url=reverse_lazy("accounts:login_page"))
def cart(request):
    try:
        user_cart = request.user.cart
        if cart is not None:
            # cart_products = CartProduct.objects.filter(cart=user_cart)
            # cart_total = 0
            # for cart_item in cart_products:
            #     cart_total += cart_item.get_total_price

            cart_products = (
                CartProduct.objects.filter(cart=user_cart)
                .select_related("product")
                .annotate(
                    subtotal=ExpressionWrapper(
                        F("product__price") * F("quantity"),
                        output_field=DecimalField(max_digits=10, decimal_places=2),
                    )
                )
            )

            cart_total = cart_products.aggregate(total=Sum("subtotal"))["total"] or 0

    except Exception:
        messages.error(request, "Something went wrong, please try again later")
        return redirect("store:home_page")

    context = {"products": cart_products, "cart_total": cart_total}

    return render(request, "store/cart.html", context)


@login_required(login_url=reverse_lazy("accounts:login_page"))
def place_order(request):
    user_cart = request.user.cart

    cart_products = CartProduct.objects.filter(cart=user_cart).annotate(
        subtotal=ExpressionWrapper(
            F("product__price") * F("quantity"),
            output_field=DecimalField(max_digits=10, decimal_places=2),
        )
    )
    cart_sub_total = cart_products.aggregate(total=Sum("subtotal"))["total"] or 0

    try:
        order_id = generate_order_id(request.user.id)
        with transaction.atomic():
            # create new order
            new_order = Order.objects.create(
                user=request.user,
                order_id=order_id,
                subtotal=cart_sub_total,
                total=cart_sub_total,
            )

            # create order items for newly created order
            for cart_item in cart_products:
                OrderItem.objects.create(
                    order=new_order,
                    product=cart_item.product,
                    product_name=cart_item.product.name,
                    price=cart_item.product.price,
                    quantity=cart_item.quantity,
                )

            # remove ordered items from cart
            for cart_item in cart_products:
                cart_item.delete()

    except IntegrityError:
        messages.error(request, "Failed to create an order")
        return redirect("store:cart_page")
    except Exception as e:
        print("Unexpected behaviour: ", str(e))
        return redirect("store:cart_page")
    else:
        messages.success(request, "Order placed successful")
        return redirect("store:order_page")


@login_required(login_url=reverse_lazy("accounts:login_page"))
def cancel_order(request, pk):
    try:
        order_to_delete = Order.objects.get(pk=pk)
    except Order.DoesNotExist:
        messages.error(request, "Failed to cancel the order")
    else:
        order_to_delete.delete()
        messages.success(request, "Order cancel successful")

    return redirect("store:order_page")


@login_required(login_url=reverse_lazy("accounts:login_page"))
def order(request):

    orders = Order.objects.filter(user=request.user).prefetch_related(
        "items", "items__product", "payment"
    )

    context = {"orders": orders}

    return render(request, "store/order.html", context)


@login_required(login_url="accounts:login_page")
def khalti_payment(request, order_id):
    # 1. Fetch order securely (ownership check)
    order = get_object_or_404(
        Order,
        order_id=order_id,
        user=request.user,
    )

    if order.status == Order.Status.PAID:
        messages.info(request, "This order is already paid.")
        return redirect("store:order_page")

    purchase_order_id = f"TR-{order.order_id}"

    # 2. Create or reuse payment safely
    payment, created = Payment.objects.get_or_create(
        purchase_order_id=purchase_order_id,
        defaults={
            "order": order,
            "amount": order.total,
            "status": Payment.Status.INITIATED,
        },
    )

    if not created and payment.status != Payment.Status.INITIATED:
        messages.warning(request, "Payment already processed for this order.")
        return redirect("store:order_page")

    amount_paisa = int((payment.amount * Decimal("100")).quantize(Decimal("1")))

    payload = {
        "return_url": settings.SITE_URL + reverse("store:khalti_payment_response"),
        "website_url": settings.SITE_URL + reverse("store:home_page"),
        "amount": amount_paisa,
        "purchase_order_id": payment.purchase_order_id,
        "purchase_order_name": str(order.order_id),
        "customer_info": {
            "name": request.user.get_full_name() or request.user.email,
            "email": request.user.email,
            "phone": getattr(order, "phone", "no phone"),
        },
    }

    headers = {
        "Authorization": f"Key {settings.KHALTI_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            url=f"{settings.KHALTI_BASE_URL}/epayment/initiate/",
            json=payload,
            headers=headers,
            timeout=10,
        )

        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        messages.error(request, "Payment service unavailable. Try again later.")
        return redirect("store:order_page")

    pidx = data.get("pidx")
    payment_url = data.get("payment_url")

    if not pidx or not payment_url:
        messages.error(request, "Invalid response from payment gateway.")
        return redirect("store:order_page")

    payment.pidx = pidx
    payment.save(update_fields=["pidx"])

    return redirect(payment_url)


@login_required(login_url="accounts:login_page")
def khalti_payment_response(request):
    pidx = request.GET.get("pidx")

    if not pidx:
        messages.error(request, "Invalid payment response.")
        return redirect("store:home_page")

    try:
        payment = Payment.objects.select_related("order").get(pidx=pidx)
    except Payment.DoesNotExist:
        messages.error(request, "Payment record not found.")
        return redirect("store:home_page")

    # Idempotency
    if payment.status == Payment.Status.SUCCESS:
        messages.info(request, "Payment already verified.")
        return redirect("store:order_page")

    # 1. Verify with Khalti (server-to-server)
    headers = {
        "Authorization": f"Key {settings.KHALTI_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            url=f"{settings.KHALTI_BASE_URL}/epayment/lookup/",
            json={"pidx": pidx},
            headers=headers,
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException:
        messages.error(request, "Payment verification failed.")
        return redirect("store:home_page")

    # 2. Validate response
    if data.get("status") != "Completed":
        payment.status = Payment.Status.FAILED
        payment.save(update_fields=["status"])
        messages.error(request, "Payment was not completed.")
        return redirect("store:home_page")

    total_amount_paisa = int(data.get("total_amount", 0))
    expected_amount_paisa = int(payment.amount * Decimal("100"))

    if total_amount_paisa != expected_amount_paisa:
        payment.status = Payment.Status.FAILED
        payment.save(update_fields=["status"])
        messages.error(request, "Payment amount mismatch.")
        return redirect("store:home_page")

    transaction_id = data.get("transaction_id")

    # 3. Finalize atomically
    try:
        with transaction.atomic():
            payment.transaction_id = transaction_id
            payment.status = Payment.Status.SUCCESS
            payment.save(update_fields=["transaction_id", "status"])

            payment.order.status = Order.Status.PAID
            payment.order.save(update_fields=["status"])
    except Exception:
        messages.error(request, "Payment verification failed.")
        return redirect("store:home_page")

    messages.success(request, "Payment successful. Your order has been confirmed.")
    return redirect("store:order_page")


@login_required(login_url="accounts:login_page")
def review(request, order_item_id):
    order_item = get_object_or_404(OrderItem, pk=order_item_id)

    review_instance = Review.objects.filter(
        user=request.user,
        product=order_item.product,
    ).first()

    if request.method == "POST":
        form = ReviewForm(
            request.POST,
            instance=review_instance,
            user=request.user,
            product=order_item.product,
        )

        if form.is_valid():
            form.save()
            return redirect("store:order_page")

        messages.error(request, "Please correct the errors below.")
    else:
        form = ReviewForm(instance=review_instance)

    return render(
        request,
        "store/review.html",
        {
            "order_item": order_item,
            "form": form,
        },
    )
