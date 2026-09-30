from django.db import models


class Order(models.Model):
    STATUS = [
        ("preparing", "Being prepared"), ("out_for_delivery", "Out for delivery"),
        ("delivered", "Delivered"), ("cancelled", "Cancelled"), ("payment_failed", "Payment failed"),
    ]
    PAYMENT = [("paid", "Paid"), ("deducted", "Failed but deducted"), ("duplicate", "Duplicate payment")]

    order_id = models.CharField(max_length=10, unique=True, db_index=True)   # e.g. FD1001
    restaurant = models.CharField(max_length=100)
    items = models.JSONField(default=list)                                   # ["Paneer Wrap", ...]
    total = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS, default="preparing")
    eta_minutes = models.PositiveIntegerField(null=True, blank=True)
    delay_minutes = models.PositiveIntegerField(null=True, blank=True)
    partner_name = models.CharField(max_length=60, blank=True)
    partner_phone = models.CharField(max_length=30, blank=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT, default="paid")
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def cancellable(self):
        return self.status == "preparing"

    def __str__(self):
        return f"{self.order_id} - {self.restaurant}"


class Refund(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="refund")
    state = models.CharField(max_length=20, default="Initiated")            # Initiated / Processing / Completed
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    expected_in = models.CharField(max_length=40, default="3-5 working days")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Refund {self.order.order_id} ({self.state})"


class CancellationRequest(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="cancellations")
    reason = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class SupportTicket(models.Model):
    STATUS = [("open", "Open"), ("in_progress", "In progress"), ("resolved", "Resolved")]
    ticket_id = models.CharField(max_length=12, unique=True, blank=True)
    order = models.ForeignKey(Order, null=True, blank=True, on_delete=models.SET_NULL, related_name="tickets")
    session_id = models.CharField(max_length=64, blank=True)
    issue = models.CharField(max_length=255)
    escalated_to_human = models.BooleanField(default=False)
    transcript = models.JSONField(default=list, blank=True)                  # full chat, for support agents
    status = models.CharField(max_length=15, choices=STATUS, default="open")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.ticket_id:
            self.ticket_id = f"TKT-{4000 + self.pk}"
            super().save(update_fields=["ticket_id"])

    def __str__(self):
        return self.ticket_id


class ChatMessage(models.Model):
    session_id = models.CharField(max_length=64, db_index=True)
    sender = models.CharField(max_length=10)                                 # "customer" or "bot"
    text = models.TextField()
    order_id = models.CharField(max_length=10, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
