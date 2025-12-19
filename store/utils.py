from datetime import datetime


def generate_order_id(user_id):
    now = datetime.now()
    return f"ORD-{now.year}{now.month}{now.day}-{user_id}-{now.hour}{now.minute}"
