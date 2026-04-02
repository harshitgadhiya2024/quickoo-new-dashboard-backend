from email.message import EmailMessage

import aiosmtplib

from app.core.config import get_settings


async def send_admin_created_email(new_admin_email: str) -> None:
    settings = get_settings()

    message = EmailMessage()
    message["From"] = settings.smtp_from
    message["To"] = settings.booking_admin_email
    message["Subject"] = "New admin user created"
    message.set_content(
        f"A new admin user has been created.\n\nEmail: {new_admin_email}\n"
    )

    await aiosmtplib.send(
        message,
        hostname=settings.smtp_host,
        port=settings.smtp_port,
        start_tls=not settings.smtp_secure,
        use_tls=settings.smtp_secure,
        username=settings.smtp_user,
        password=settings.smtp_pass,
    )


async def send_order_created_email(order_data: dict) -> None:
    settings = get_settings()

    message = EmailMessage()
    message["From"] = settings.smtp_from
    message["To"] = settings.booking_admin_email
    message["Subject"] = f"New order created: {order_data.get('order_id')}"
    message.set_content(
        "A new order has been created.\n\n"
        f"Order ID: {order_data.get('order_id')}\n"
        f"Customer: {order_data.get('first_name')} {order_data.get('last_name')}\n"
        f"Email: {order_data.get('email')}\n"
        f"Phone: {order_data.get('phonenumber')}\n"
        f"Pickup Date: {order_data.get('pickup_date')}\n"
        f"Pickup Time: {order_data.get('pickup_time')}\n"
        f"Vehicle Class: {order_data.get('vehicle_class')}\n"
        f"Route Distance: {order_data.get('route_distance')}\n"
        f"Total Price: {order_data.get('total_price')}\n"
        f"Payment Paid: {order_data.get('is_payment_paid')}\n"
        f"Transaction ID: {order_data.get('transcation_id')}\n"
        f"From: {order_data.get('from')}\n"
        f"To: {order_data.get('to')}\n"
        f"Stops: {order_data.get('stops')}\n"
        f"Special Request: {order_data.get('special_request')}\n"
        f"Status: {order_data.get('status')}\n"
    )

    await aiosmtplib.send(
        message,
        hostname=settings.smtp_host,
        port=settings.smtp_port,
        start_tls=not settings.smtp_secure,
        use_tls=settings.smtp_secure,
        username=settings.smtp_user,
        password=settings.smtp_pass,
    )
