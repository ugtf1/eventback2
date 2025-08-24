from django.urls import path
from . import views
from . import views_paypal, views_stripe, views_paystack

urlpatterns = [
    path("", views.home, name="home"),
    path("booking/", views.booking_form, name="booking_form"),
    path("booking/<int:hall_id>/", views.booking_form, name="booking_form_for_hall"),
    path("api/availability/", views.api_check_availability, name="api_check_availability"),
    path("checkout/<int:booking_id>/", views.checkout, name="checkout"),
    path("payment/success/<int:booking_id>/", views.payment_success, name="payment_success"),

    # PayPal
    path("payments/paypal/create-order/", views_paypal.paypal_create_order, name="paypal_create_order"),
    path("payments/paypal/return/<int:booking_id>/", views_paypal.paypal_return, name="paypal_return"),

    # Stripe
    path("payments/stripe/create-session/", views_stripe.stripe_create_session, name="stripe_create_session"),
    path("payments/stripe/success/<int:booking_id>/", views_stripe.stripe_success, name="stripe_success"),
    path("payments/stripe/webhook/", views_stripe.stripe_webhook, name="stripe_webhook"),

    # Paystack
    path("payments/paystack/initialize/", views_paystack.paystack_initialize, name="paystack_initialize"),
    path("payments/paystack/return/<int:booking_id>/", views_paystack.paystack_return, name="paystack_return"),
]
