from django.core.management.base import BaseCommand
from support.models import Order, Refund


DEMO = [
    dict(order_id="FD1001", restaurant="Spice Route", items=["Paneer Wrap", "Masala Fries"], total=420, status="preparing", eta_minutes=30),
    dict(order_id="FD1002", restaurant="Noodle Bar", items=["Veg Hakka Noodles", "Spring Rolls"], total=380, status="out_for_delivery", eta_minutes=25, delay_minutes=20, partner_name="Ravi", partner_phone="+91 98765 43210"),
    dict(order_id="FD1003", restaurant="Biryani House", items=["Chicken Biryani", "Raita"], total=510, status="delivered"),
    dict(order_id="FD1004", restaurant="Pizza Corner", items=["Margherita Pizza"], total=350, status="cancelled", _refund=("Processing", "3-5 working days")),
    dict(order_id="FD1005", restaurant="Dosa Point", items=["Masala Dosa", "Filter Coffee"], total=260, status="payment_failed", payment_status="deducted", _refund=("Initiated", "5-7 working days")),
    dict(order_id="FD1006", restaurant="Sweet Tooth", items=["Brownie Sundae"], total=290, status="preparing", eta_minutes=20, payment_status="duplicate", _refund=("Processing", "3-5 working days")),
]


class Command(BaseCommand):
    help = "Create the demo orders FD1001 - FD1006"

    def handle(self, *args, **opts):
        for row in DEMO:
            row = dict(row)
            refund = row.pop("_refund", None)
            order, _ = Order.objects.update_or_create(order_id=row.pop("order_id"), defaults=row)
            if refund:
                Refund.objects.update_or_create(order=order, defaults=dict(state=refund[0], amount=order.total, expected_in=refund[1]))
        self.stdout.write(self.style.SUCCESS("Demo orders FD1001-FD1006 ready."))
