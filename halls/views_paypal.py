import requests
from django.conf import settings
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .models import Booking

def _paypal_api_base():
    # sandbox => api.sandbox.paypal.com, live => api.paypal.com
    return f"https://api.{settings.PAYPAL_MODE}.paypal.com"

def _paypal_access_token():
    res = requests.post(
        f"{_paypal_api_base()}/v1/oauth2/token",
        auth=(settings.PAYPAL_CLIENT_ID, settings.PAYPAL_CLIENT_SECRET),
        data={"grant_type": "client_credentials"},
        timeout=20,
    )
    res.raise_for_status()
    return res.json()["access_token"]

@require_POST
def paypal_create_order(request):
    booking_id = request.POST.get("booking_id")
    booking = get_object_or_404(Booking, pk=booking_id, status="pending")

    access_token = _paypal_access_token()
    payload = {
        "intent": "CAPTURE",
        "purchase_units": [{
            "reference_id": str(booking.id),
            "amount": {
                "currency_code": settings.PAYPAL_CURRENCY,
                "value": f"{booking.total_amount:.2f}",
            }
        }],
        "application_context": {
            "return_url": request.build_absolute_uri(f"/payments/paypal/return/{booking.id}/"),
            "cancel_url": request.build_absolute_uri(f"/checkout/{booking.id}/"),
            "brand_name": "Safe Haven",
            "landing_page": "LOGIN",
            "user_action": "PAY_NOW",
        },
    }
    res = requests.post(
        f"{_paypal_api_base()}/v2/checkout/orders",
        headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
        json=payload, timeout=20
    )
    res.raise_for_status()
    data = res.json()
    approve = next(l["href"] for l in data["links"] if l["rel"] == "approve")
    # store order id
    booking.payment_provider = "paypal"
    booking.provider_ref = data["id"]
    booking.save(update_fields=["payment_provider", "provider_ref"])
    return redirect(approve)

def paypal_return(request, booking_id):
    """
    PayPal redirects back with ?token=ORDER_ID.
    We capture the order server-side, verify COMPLETED, then mark paid.
    """
    booking = get_object_or_404(Booking, pk=booking_id, status="pending")
    order_id = request.GET.get("token") or booking.provider_ref
    if not order_id:
        return redirect("checkout", booking_id=booking.id)

    access_token = _paypal_access_token()
    cap = requests.post(
        f"{_paypal_api_base()}/v2/checkout/orders/{order_id}/capture",
        headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
        timeout=20,
    )
    cap.raise_for_status()
    status = cap.json().get("status")
    if status == "COMPLETED":
        booking.status = "paid"
        booking.save(update_fields=["status"])
        return redirect("payment_success", booking_id=booking.id)
    # If not completed, return to checkout
    return redirect("checkout", booking_id=booking.id)
