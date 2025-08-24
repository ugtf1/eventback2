from django.db import models

class Hall(models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="hall_images/", blank=True, null=True)

    def __str__(self):
        return self.name

class Booking(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("cancelled", "Cancelled"),
    )
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=40)
    address = models.CharField(max_length=255, blank=True)
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE, related_name="bookings")
    purpose = models.CharField(max_length=255)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    payment_provider = models.CharField(max_length=20, blank=True)   # paypal/stripe/paystack
    provider_ref = models.CharField(max_length=100, blank=True)      # order/session/reference
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.hall.name}"

    @property
    def hours(self):
        delta = self.end_datetime - self.start_datetime
        return round(delta.total_seconds() / 3600, 2)
