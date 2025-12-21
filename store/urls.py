from django.urls import path
from . import views

app_name = "store"

urlpatterns = [
    path("", views.home, name="home_page"),
    # products
    path("products/", views.products, name="products_page"),
    path("products/<int:pk>/detail/", views.product_detail, name="product_detail_page"),
    # cart
    path("cart/<int:pk>/add/", views.add_to_cart, name="add_to_cart"),
    path("cart/<int:pk>/remove/", views.remove_from_cart, name="remove_from_cart"),
    path("cart/<int:pk>/update/", views.update_cart, name="update_cart"),
    path("cart/", views.cart, name="cart_page"),
    # order
    path("order/", views.place_order, name="place_order"),
    path("order/<int:pk>/cancel/", views.cancel_order, name="cancel_order"),
    path("order/view/", views.order, name="order_page"),
    # khalti-payment
    path(
        "order/<order_id>/payment/khalti/", views.khalti_payment, name="khalti_payment"
    ),
    path(
        "order/payment/khalti/",
        views.khalti_payment_response,
        name="khalti_payment_response",
    ),
]
