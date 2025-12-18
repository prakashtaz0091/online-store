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
