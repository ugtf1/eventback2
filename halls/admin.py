from django.contrib import admin
from .models import Hall, Booking

@admin.register(Hall)
class HallAdmin(admin.ModelAdmin):
    list_display = ("name", "hourly_rate")
    search_fields = ("name",)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("name", "hall", "start_datetime", "end_datetime", "total_amount", "status", "payment_provider")
    list_filter = ("status", "hall")
    search_fields = ("name", "email", "phone", "provider_ref")
