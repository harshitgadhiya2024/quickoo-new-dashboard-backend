import html
from email.message import EmailMessage
from typing import Any

import aiosmtplib

from app.core.config import get_settings
from app.db.mongodb import get_database


def _format_location(loc: Any) -> str:
    if not loc or not isinstance(loc, dict):
        return "—"
    return str(loc.get("address") or "—").strip() or "—"


def _format_date(value: Any) -> str:
    if value is None:
        return "—"
    if hasattr(value, "strftime"):
        try:
            return value.strftime("%d %B %Y")
        except (AttributeError, ValueError):
            pass
    return str(value)


def _format_time(value: Any) -> str:
    if value is None:
        return "—"
    if hasattr(value, "strftime"):
        try:
            return value.strftime("%H:%M")
        except (AttributeError, ValueError):
            pass
    return str(value)


def _format_stops(stops: Any) -> str:
    if not stops or not isinstance(stops, list):
        return "None"
    lines = []
    for i, stop in enumerate(stops, start=1):
        if isinstance(stop, dict):
            lines.append(f"{i}. {_format_location(stop)}")
        else:
            lines.append(f"{i}. {stop}")
    return "\n".join(lines) if lines else "None"


def _format_money_gbp(amount: Any) -> str:
    try:
        return f"£{float(amount):,.2f}"
    except (TypeError, ValueError):
        return str(amount)


def _build_customer_confirmation_plain(order_data: dict) -> str:
    paid = order_data.get("is_payment_paid")
    payment_line = "Paid" if paid else "Payment pending"
    fn = order_data.get("first_name") or ""
    ln = order_data.get("last_name") or ""
    flight = order_data.get("flight_number")
    special = order_data.get("special_request")
    lines = [
        (f"Hi {fn}," if fn else "Hi,").strip(),
        "",
        "Thank you for booking with Quickoo. Your journey is confirmed.",
        "",
        f"Booking number: {order_data.get('order_id')}",
        "",
        "Your details",
        f"  Name: {fn} {ln}".strip(),
        f"  Email: {order_data.get('email')}",
        f"  Phone: {order_data.get('phonenumber')}",
        "",
        "Journey",
        f"  Pick-up: {_format_location(order_data.get('from'))}",
        f"  Drop-off: {_format_location(order_data.get('to'))}",
        f"  Stops:\n{_format_stops(order_data.get('stops'))}",
        f"  Distance: {order_data.get('route_distance')} miles",
        "",
        "Schedule",
        f"  Date: {_format_date(order_data.get('pickup_date'))}",
        f"  Time: {_format_time(order_data.get('pickup_time'))}",
        f"  Vehicle: {order_data.get('vehicle_class')}",
    ]
    if flight:
        lines.append(f"  Flight number: {flight}")
    if special:
        lines.append(f"  Special requests: {special}")
    lines.extend(
        [
            "",
            "Payment",
            f"  Total: {_format_money_gbp(order_data.get('total_price'))}",
            f"  Status: {payment_line}",
            "",
            "If anything looks wrong, reply to this email or contact us.",
            "",
            "— Quickoo",
        ]
    )
    return "\n".join(lines)


def _h(text: Any) -> str:
    if text is None:
        return ""
    return html.escape(str(text), quote=True)


def _build_customer_confirmation_html(order_data: dict) -> str:
    paid = bool(order_data.get("is_payment_paid"))
    payment_badge = "Paid" if paid else "Payment pending"
    payment_color = "#0d9488" if paid else "#ca8a04"
    fn = order_data.get("first_name") or ""
    ln = order_data.get("last_name") or ""
    greeting = _h(f"Hi {fn},") if fn else "Hi,"
    flight = order_data.get("flight_number")
    special = order_data.get("special_request")
    flight_row = ""
    if flight:
        flight_row = f"""
            <tr><td style="padding:8px 0;color:#64748b;width:140px;">Flight number</td>
            <td style="padding:8px 0;color:#0f172a;">{_h(flight)}</td></tr>"""
    special_block = ""
    if special:
        special_block = f"""
        <div style="margin-top:20px;padding:16px;background:#f8fafc;border-radius:8px;border-left:4px solid #3b82f6;">
          <p style="margin:0;font-size:13px;color:#64748b;text-transform:uppercase;letter-spacing:0.05em;">Special requests</p>
          <p style="margin:8px 0 0;font-size:15px;color:#0f172a;">{_h(special)}</p>
        </div>"""

    stops_html = ""
    stops = order_data.get("stops") or []
    if isinstance(stops, list) and stops:
        items_parts = []
        for s in stops:
            if isinstance(s, dict):
                items_parts.append(
                    f'<li style="margin:6px 0;color:#0f172a;">{_h(_format_location(s))}</li>'
                )
            else:
                items_parts.append(f'<li style="margin:6px 0;color:#0f172a;">{_h(s)}</li>')
        items = "".join(items_parts)
        stops_html = f'<ul style="margin:8px 0 0;padding-left:20px;">{items}</ul>'
    else:
        stops_html = '<p style="margin:8px 0 0;color:#64748b;">No intermediate stops</p>'

    booking_id = _h(order_data.get("order_id") or "—")

    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f1f5f9;font-family:system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#f1f5f9;padding:32px 16px;">
    <tr><td align="center">
      <table role="presentation" width="100%" style="max-width:560px;background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 4px 24px rgba(15,23,42,0.08);">
        <tr><td style="background:linear-gradient(135deg,#0f172a 0%,#1e3a5f 100%);padding:28px 32px;">
          <p style="margin:0;font-size:13px;color:#94a3b8;text-transform:uppercase;letter-spacing:0.08em;">Booking confirmed</p>
          <h1 style="margin:8px 0 0;font-size:22px;font-weight:600;color:#ffffff;">Your journey with Quickoo</h1>
        </td></tr>
        <tr><td style="padding:28px 32px;">
          <p style="margin:0 0 20px;font-size:16px;line-height:1.5;color:#334155;">{greeting}</p>
          <p style="margin:0 0 24px;font-size:15px;line-height:1.6;color:#475569;">Thank you for your booking. Below is a summary of the details you provided. We will be in touch if we need anything else.</p>
          <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:20px;margin-bottom:24px;">
            <p style="margin:0 0 4px;font-size:12px;color:#64748b;text-transform:uppercase;letter-spacing:0.06em;">Booking number</p>
            <p style="margin:0;font-size:20px;font-weight:600;color:#0f172a;letter-spacing:0.02em;font-family:ui-monospace,monospace;">{booking_id}</p>
          </div>
          <h2 style="margin:0 0 12px;font-size:14px;color:#0f172a;text-transform:uppercase;letter-spacing:0.06em;">Your details</h2>
          <table role="presentation" width="100%" style="margin-bottom:24px;font-size:15px;">
            <tr><td style="padding:8px 0;color:#64748b;width:100px;">Name</td><td style="padding:8px 0;color:#0f172a;">{_h((fn + " " + ln).strip() or "—")}</td></tr>
            <tr><td style="padding:8px 0;color:#64748b;">Email</td><td style="padding:8px 0;color:#0f172a;">{_h(order_data.get("email") or "—")}</td></tr>
            <tr><td style="padding:8px 0;color:#64748b;">Phone</td><td style="padding:8px 0;color:#0f172a;">{_h(order_data.get("phonenumber") or "—")}</td></tr>
          </table>
          <h2 style="margin:0 0 12px;font-size:14px;color:#0f172a;text-transform:uppercase;letter-spacing:0.06em;">Journey</h2>
          <table role="presentation" width="100%" style="margin-bottom:8px;font-size:15px;">
            <tr><td style="padding:8px 0;color:#64748b;width:100px;vertical-align:top;">Pick-up</td><td style="padding:8px 0;color:#0f172a;">{_h(_format_location(order_data.get("from")))}</td></tr>
            <tr><td style="padding:8px 0;color:#64748b;vertical-align:top;">Drop-off</td><td style="padding:8px 0;color:#0f172a;">{_h(_format_location(order_data.get("to")))}</td></tr>
            <tr><td style="padding:8px 0;color:#64748b;vertical-align:top;">Stops</td><td style="padding:8px 0;">{stops_html}</td></tr>
            <tr><td style="padding:8px 0;color:#64748b;">Distance</td><td style="padding:8px 0;color:#0f172a;">{_h(order_data.get("route_distance"))} miles</td></tr>
          </table>
          <h2 style="margin:24px 0 12px;font-size:14px;color:#0f172a;text-transform:uppercase;letter-spacing:0.06em;">Schedule</h2>
          <table role="presentation" width="100%" style="margin-bottom:8px;font-size:15px;">
            <tr><td style="padding:8px 0;color:#64748b;width:140px;">Date</td><td style="padding:8px 0;color:#0f172a;">{_h(_format_date(order_data.get("pickup_date")))}</td></tr>
            <tr><td style="padding:8px 0;color:#64748b;">Time</td><td style="padding:8px 0;color:#0f172a;">{_h(_format_time(order_data.get("pickup_time")))}</td></tr>
            <tr><td style="padding:8px 0;color:#64748b;">Vehicle</td><td style="padding:8px 0;color:#0f172a;">{_h(order_data.get("vehicle_class") or "—")}</td></tr>
            {flight_row}
          </table>
          {special_block}
          <div style="margin-top:28px;padding:20px;background:linear-gradient(135deg,#f0fdf4 0%,#ecfdf5 100%);border-radius:10px;border:1px solid #bbf7d0;">
            <p style="margin:0 0 8px;font-size:12px;color:#166534;text-transform:uppercase;letter-spacing:0.06em;">Amount</p>
            <p style="margin:0;font-size:26px;font-weight:700;color:#0f172a;">{_h(_format_money_gbp(order_data.get("total_price")))}</p>
            <p style="margin:12px 0 0;font-size:14px;">
              <span style="display:inline-block;padding:4px 10px;border-radius:999px;background:{payment_color};color:#ffffff;font-weight:600;">{payment_badge}</span>
            </p>
          </div>
          <p style="margin:28px 0 0;font-size:13px;line-height:1.6;color:#94a3b8;">This email summarises the journey details you provided and the total amount for your booking.</p>
        </td></tr>
        <tr><td style="padding:20px 32px;background:#f8fafc;border-top:1px solid #e2e8f0;">
          <p style="margin:0;font-size:13px;color:#64748b;text-align:center;">Quickoo · Need help? Reply to this email.</p>
        </td></tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""


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
    vehicle_class_value = order_data.get("vehicle_class")
    vehicle_class_display = await _resolve_vehicle_class_name(vehicle_class_value)

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
        f"Vehicle Class: {vehicle_class_display}\n"
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


async def _resolve_vehicle_class_name(vehicle_class_value: Any) -> str:
    if not vehicle_class_value:
        return "—"

    db = get_database()
    vehicle_class = await db.vehicle_classes.find_one(
        {"vehicle_class_id": str(vehicle_class_value)},
        {"class_name": 1},
    )
    if vehicle_class and vehicle_class.get("class_name"):
        return str(vehicle_class["class_name"])

    return str(vehicle_class_value)


async def send_order_confirmation_to_customer(order_data: dict) -> None:
    settings = get_settings()
    to_email = order_data.get("email")
    if not to_email or not str(to_email).strip():
        return

    normalized_order_data = dict(order_data)
    normalized_order_data["vehicle_class"] = await _resolve_vehicle_class_name(
        normalized_order_data.get("vehicle_class")
    )

    plain = _build_customer_confirmation_plain(normalized_order_data)
    html_body = _build_customer_confirmation_html(normalized_order_data)
    order_ref = normalized_order_data.get("order_id") or "booking"

    message = EmailMessage()
    message["From"] = settings.smtp_from
    message["To"] = str(to_email).strip()
    message["Subject"] = f"Quickoo — booking confirmed ({order_ref})"
    message.set_content(plain)
    message.add_alternative(html_body, subtype="html")

    await aiosmtplib.send(
        message,
        hostname=settings.smtp_host,
        port=settings.smtp_port,
        start_tls=not settings.smtp_secure,
        use_tls=settings.smtp_secure,
        username=settings.smtp_user,
        password=settings.smtp_pass,
    )
