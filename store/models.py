from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=60)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    image = models.ImageField(upload_to="products/")
    featured = models.BooleanField(default=False)
    description = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    categories = models.ManyToManyField(Category)

    def __str__(self):
        return self.name


class Cart(models.Model):
    user = models.OneToOneField("accounts.CustomUser", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.email}'s cart"


class CartProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="carts")
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="products")
    quantity = models.PositiveIntegerField(default=1)

    added_at = models.DateTimeField(auto_now_add=True)

    @property
    def get_total_price(self):
        return self.quantity * self.product.price

    def __str__(self):
        return f"{self.product.name}-> {self.cart.user}"


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        SHIPPED = "shipped", "Shipped"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"

    user = models.ForeignKey(
        "accounts.CustomUser",
        on_delete=models.PROTECT,
        related_name="orders",
    )

    order_id = models.CharField(max_length=30, unique=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )

    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.order_id} ({self.user.email})"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
    )

    product_name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()

    def get_total_price(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"


class ShippingAddress(models.Model):
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="shipping_address",
    )
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address_line = models.TextField()
    city = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=20)

    def __str__(self):
        return f"Shipping for Order {self.order.order_id}"


class Payment(models.Model):
    class Method(models.TextChoices):
        COD = "cod", "Cash on Delivery"
        ESEWA = "esewa", "eSewa"
        KHALTI = "khalti", "Khalti"

    class Status(models.TextChoices):
        INITIATED = "initiated", "Initiated"
        PENDING = "pending", "Pending"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="payment",
    )

    method = models.CharField(
        max_length=20, choices=Method.choices, default=Method.KHALTI
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.INITIATED,
    )

    purchase_order_id = models.CharField(max_length=100, unique=True)

    # from khati
    transaction_id = models.CharField(max_length=100, unique=True)
    pidx = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order.order_id} - {self.status}"
