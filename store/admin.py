from django.contrib import admin
from .models import Product, Category, Cart, Payment, Order
from store.forms import OrderChangeForm


admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Cart)
admin.site.register(Payment)
# admin.site.register(Order)


@admin.register(Order)
class OrderModelAdmin(admin.ModelAdmin):
    list_display = [
        "order_id",
        "status",
        "delivery_person",
        "user",
        "total",
        "created_at",
    ]

    list_filter = ["status", "delivery_person"]

    search_fields = [
        "order_id",
        "user__email",
        "user__first_name",
        "user__last_name",
        "delivery_person__user__email",
        "delivery_person__user__first_name",
        "delivery_person__user__last_name",
    ]

    form = OrderChangeForm

    # disable delete
    def has_delete_permission(self, request, obj=...):
        return False

    # disable add
    def has_add_permission(self, request):
        return False
