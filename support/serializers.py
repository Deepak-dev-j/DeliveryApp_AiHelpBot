from rest_framework import serializers
from .models import Order, Refund, SupportTicket, ChatMessage


class RefundSerializer(serializers.ModelSerializer):
    when = serializers.CharField(source="expected_in")
    amount = serializers.FloatField()

    class Meta:
        model = Refund
        fields = ("state", "amount", "when")


class OrderSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="order_id")
    eta = serializers.IntegerField(source="eta_minutes", allow_null=True)
    delay = serializers.IntegerField(source="delay_minutes", allow_null=True)
    pay = serializers.CharField(source="payment_status")
    total = serializers.FloatField()
    cancellable = serializers.BooleanField(read_only=True)
    partner = serializers.SerializerMethodField()
    refund = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ("id", "restaurant", "items", "total", "status", "eta", "delay",
                  "partner", "pay", "refund", "cancellable")

    def get_partner(self, o):
        return {"name": o.partner_name, "phone": o.partner_phone} if o.partner_name else None

    def get_refund(self, o):
        return RefundSerializer(o.refund).data if hasattr(o, "refund") else None


class TicketCreateSerializer(serializers.Serializer):
    order_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    issue = serializers.CharField(max_length=255)
    escalate = serializers.BooleanField(default=False)
    session_id = serializers.CharField(required=False, allow_blank=True)
    transcript = serializers.ListField(required=False, default=list)


class CancelSerializer(serializers.Serializer):
    order_id = serializers.CharField()
    reason = serializers.CharField(required=False, allow_blank=True, default="")


class ChatInSerializer(serializers.Serializer):
    session_id = serializers.CharField()
    message = serializers.CharField()
    order_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ("sender", "text", "order_id", "created_at")
