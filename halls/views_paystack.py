import requests
from django.conf import settings
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .models import Booking

PAYSTACK_BASE = "https://api.paystack.co"

@require_POST
def paystack_initialize(request):
    booking_id = request.POST.get("booking_id")
    booking = get_object_or_404(Booking, pk=booking_id, status="pending")

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "email": booking.email,
        "amount": int(float(booking.total_amount) * 100),  # kobo
        "callback_url": request.build_absolute_uri(f"/payments/paystack/return/{booking.id}/"),
        # "currency": "NGN",  # default NGN; uncomment if needed explicitly
        "metadata": {"booking_id": booking.id},
    }
    res = requests.post(f"{PAYSTACK_BASE}/transaction/initialize", json=payload, headers=headers, timeout=20)
    res.raise_for_status()
    data = res.json()["data"]
    booking.payment_provider = "paystack"
    booking.provider_ref = data["reference"]
    booking.save(update_fields=["payment_provider", "provider_ref"])
    return redirect(data["authorization_url"])

def paystack_return(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    reference = request.GET.get("reference") or booking.provider_ref
    if not reference:
        return redirect("checkout", booking_id=booking.id)

    headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
    res = requests.get(f"{PAYSTACK_BASE}/transaction/verify/{reference}", headers=headers, timeout=20)
    res.raise_for_status()
    data = res.json()["data"]
    if data["status"] == "success" and data["amount"] == int(float(booking.total_amount) * 100):
        booking.status = "paid"
        booking.save(update_fields=["status"])
        return redirect("payment_success", booking_id=booking.id)
    return redirect("checkout", booking_id=booking.id)
