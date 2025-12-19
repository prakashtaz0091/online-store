from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Cart, CartProduct, Order, OrderItem
from django.core.paginator import Paginator
from .forms import ProductFilterForm
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F, Sum, ExpressionWrapper, DecimalField
from .utils import generate_order_id
from django.db import transaction, IntegrityError


def home(request):

    featured_products = Product.objects.filter(featured=True).order_by("-created_at")[
        :8
    ]

    context = {"products": featured_products}

    return render(request, "store/home.html", context)


def products(request):
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

            cart_products = CartProduct.objects.filter(cart=user_cart).annotate(
                subtotal=ExpressionWrapper(
                    F("product__price") * F("quantity"),
                    output_field=DecimalField(max_digits=10, decimal_places=2),
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
                user=request.user, order_id=order_id, subtotal=cart_sub_total
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

    orders = Order.objects.filter(user=request.user)

    context = {"orders": orders}

    return render(request, "store/order.html", context)
