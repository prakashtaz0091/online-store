from django.shortcuts import render
from .models import Product
from django.core.paginator import Paginator
from .forms import ProductFilterForm


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
