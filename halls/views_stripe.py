import json
import stripe
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Booking

stripe.api_key = settings.STRIPE_SECRET_KEY

@require_POST
def stripe_create_session(request):
    booking_id = request.POST.get("booking_id")
    booking = get_object_or_404(Booking, pk=booking_id, status="pending")

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": settings.PAYPAL_CURRENCY.lower(),  # align with USD for test
                "product_data": {"name": f"Hall Booking: {booking.hall.name}"},
                "unit_amount": int(float(booking.total_amount) * 100),
            },
            "quantity": 1,
        }],
        mode="payment",
        metadata={"booking_id": str(booking.id)},
        success_url=request.build_absolute_uri(f"/payments/stripe/success/{booking.id}/"),
        cancel_url=request.build_absolute_uri(f"/checkout/{booking.id}/"),
    )
    booking.payment_provider = "stripe"
    booking.provider_ref = session.id
    booking.save(update_fields=["payment_provider", "provider_ref"])
    return redirect(session.url, code=303)

def stripe_success(request, booking_id):
    """
    We rely on webhook to mark as paid; this page is the UX redirect.
    If webhook hasn't arrived yet, user might briefly see 'pending' on refresh.
    """
    return redirect("payment_success", booking_id=booking_id)

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
    # For local dev, you can skip signature verification if not using a webhook secret.
    # If you set one, uncomment and verify with stripe.Webhook.construct_event(...)
    try:
        event = json.loads(payload)
    except Exception:
        return HttpResponseBadRequest("Invalid payload")

    if event.get("type") == "checkout.session.completed":
        session = event["data"]["object"]
        booking_id = session.get("metadata", {}).get("booking_id")
        if booking_id:
            try:
                booking = Booking.objects.get(pk=int(booking_id), status="pending")
                booking.status = "paid"
                booking.save(update_fields=["status"])
            except Booking.DoesNotExist:
                pass

    return HttpResponse(status=200)
