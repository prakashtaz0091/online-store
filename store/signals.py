from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import Order
from django.urls import reverse
from .tasks import order_placed_mail_send_task


@receiver(post_save, sender=Order)
def order_placed_mail(sender, instance, created, **kwargs):
    if not created:
        return

    user_email = instance.user.email
    if not user_email:
        return

    order_placed_mail_send_task(
        from_email=settings.DEFAULT_FROM_EMAIL,
        user_email=user_email,
        order_id=instance.order_id,
        init_payment_url=f"{settings.SITE_URL}{reverse("store:khalti_payment", args=[instance.order_id])}",
    )
