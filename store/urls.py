from django.urls import path
from . import views

app_name = "store"

urlpatterns = [
    path("", views.home, name="home_page"),
    path("products/", views.products, name="products_page"),
    path("products/<int:pk>/detail/", views.product_detail, name="product_detail_page"),
    path("cart/<int:pk>/add/", views.add_to_cart, name="add_to_cart"),
]
