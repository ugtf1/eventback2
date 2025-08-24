from django.db.models import Q
from .models import Booking

def is_available(hall, start_dt, end_dt):
    overlap = Booking.objects.filter(
        hall=hall, status__in=["pending", "paid"]
    ).filter(Q(start_datetime__lt=end_dt) & Q(end_datetime__gt=start_dt)).exists()
    return not overlap
