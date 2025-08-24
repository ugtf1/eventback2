import json
from datetime import datetime, timedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseBadRequest
from django.utils import timezone
from django.views.decorators.http import require_GET
from .models import Hall, Booking
from .utils import is_available

def home(request):
    halls = Hall.objects.all()
    # optional search
    q = request.GET.get("q")
    if q:
        halls = halls.filter(name__icontains=q)

    today = timezone.localdate()
    # month starts for next 6 months
    months = []
    d = today.replace(day=1)
    for i in range(6):
        months.append((d.replace(day=1) + timedelta(days=32*i)).replace(day=1))

    start_window = months[0]
    last_month = months[-1]
    if last_month.month == 12:
        end_window = last_month.replace(year=last_month.year + 1, month=1, day=1)
    else:
        end_window = last_month.replace(month=last_month.month + 1, day=1)

    bookings = Booking.objects.filter(
        start_datetime__date__lt=end_window,
        end_datetime__date__gte=start_window
    ).values("start_datetime", "end_datetime")

    booked_dates = set()
    for b in bookings:
        s = b["start_datetime"].date()
        e = b["end_datetime"].date()
        cur = s
        while cur <= e:
            booked_dates.add(cur.isoformat())
            cur += timedelta(days=1)

    context = {
        "halls": halls,
        "calendar_month_starts": [d.isoformat() for d in months],
        "booked_dates_json": json.dumps(sorted(list(booked_dates))),
    }
    return render(request, "halls/home.html", context)

def booking_form(request, hall_id=None):
    halls = Hall.objects.all()
    hall = get_object_or_404(Hall, pk=hall_id) if hall_id else halls.first()

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        address = request.POST.get("address", "")
        hall_id = request.POST.get("hall")
        purpose = request.POST.get("purpose")
        start_dt = request.POST.get("start_datetime")
        end_dt = request.POST.get("end_datetime")

        if not (name and email and phone and hall_id and purpose and start_dt and end_dt):
            return HttpResponseBadRequest("Missing fields")

        hall = get_object_or_404(Hall, pk=hall_id)
        try:
            start_dt = datetime.fromisoformat(start_dt)
            end_dt = datetime.fromisoformat(end_dt)
        except Exception:
            return HttpResponseBadRequest("Invalid datetime")

        if end_dt <= start_dt:
            return HttpResponseBadRequest("End must be after start")

        if not is_available(hall, start_dt, end_dt):
            return render(request, "halls/booking_form.html", {
                "halls": halls,
                "selected_hall": hall,
                "error": "Selected time is not available. Please choose another time."
            })

        hours = (end_dt - start_dt).total_seconds() / 3600
        total_amount = round(float(hall.hourly_rate) * max(0.5, hours), 2)

        booking = Booking.objects.create(
            name=name, email=email, phone=phone, address=address,
            hall=hall, purpose=purpose, start_datetime=start_dt, end_datetime=end_dt,
            total_amount=total_amount, status="pending"
        )
        return redirect("checkout", booking_id=booking.id)

    return render(request, "halls/booking_form.html", {"halls": halls, "selected_hall": hall})

@require_GET
def api_check_availability(request):
    from datetime import datetime
    hall_id = request.GET.get("hall_id")
    start_dt = request.GET.get("start")
    end_dt = request.GET.get("end")
    if not (hall_id and start_dt and end_dt):
        return JsonResponse({"ok": False, "error": "Missing params"}, status=400)

    hall = get_object_or_404(Hall, pk=hall_id)
    try:
        s = datetime.fromisoformat(start_dt)
        e = datetime.fromisoformat(end_dt)
    except Exception:
        return JsonResponse({"ok": False, "error": "Invalid datetime"}, status=400)

    available = is_available(hall, s, e)
    return JsonResponse({"ok": True, "available": available})

def checkout(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, status="pending")
    return render(request, "halls/checkout.html", {"booking": booking})

def payment_success(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    return render(request, "halls/payment_success.html", {"booking": booking})
