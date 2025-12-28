from background_task import background
from django.core.mail import send_mail
import time


@background()
def order_placed_mail_send_task(
    from_email,
    user_email,
    order_id,
    init_payment_url,
):
    time.sleep(5)  # simulate delay
    print("Sending mail to ", user_email)
    send_mail(
        subject="Order Placed",
        message="""
        Your order has been placed successfully. 
        Please forward with payment to get your order delivered.""",
        from_email=from_email,
        recipient_list=[user_email],
        fail_silently=False,
        html_message=f"""
        
        
        Order ID: {order_id}
        Click here to initiate payment: 
        <a  href="{init_payment_url}">Pay Now</a>
        
        """,
    )
