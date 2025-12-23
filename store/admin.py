from django.contrib import admin
from .models import Product, Category, Cart, Payment, Order
from .forms import OrderChangeForm


admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Cart)
admin.site.register(Payment)
# admin.site.register(Order)


@admin.register(Order)
class OrderModelAdmin(admin.ModelAdmin):
    list_display = ["order_id", "user", "status", "total", "delivery_person"]

    search_fields = (
        "order_id",
        "user__email",
        "user__first_name",
        "user__last_name",
    )
    list_filter = ("status", "delivery_person")

    form = OrderChangeForm

    # disable delete
    def has_delete_permission(self, request, obj=None):
        return False

    # disable add
    def has_add_permission(self, request):
        return False
