import re
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Order, Refund, CancellationRequest, SupportTicket, ChatMessage
from .serializers import (OrderSerializer, RefundSerializer, TicketCreateSerializer, CancelSerializer,
                          ChatInSerializer, ChatMessageSerializer)

ORDER_ID = re.compile(r"^FD\d{4}$")

# (regex, intent) - the website turns the intent into the right menu / answer
INTENTS = [
    (r"track|where.*order|status", "track"),
    (r"late|delay|slow|not arrived|taking long", "delay"),
    (r"partner|rider|driver", "partner"),
    (r"missing|not.*receive.*item|item.*missing", "missing"),
    (r"wrong", "wrong"),
    (r"cold|stale|bad|quality|taste|spill", "quality"),
    (r"fail", "payfail"),
    (r"deduct|debited|charged", "deducted"),
    (r"duplicate|twice|double", "duplicate"),
    (r"not received|no refund|refund.*(not|where)", "norefund"),
    (r"refund|money back", "refund"),
    (r"cancel", "cancel"),
    (r"ticket|complain", "ticket"),
    (r"human|agent|person|call", "human"),
]


def detect_intent(text):
    t = text.lower()
    for pattern, intent in INTENTS:
        if re.search(pattern, t):
            return intent
    return None


def clean_id(value):
    return (value or "").strip().upper()


class ChatView(APIView):
    """POST /api/chat/ - save the customer's message, work out what they need."""

    def post(self, request):
        s = ChatInSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.validated_data
        oid = clean_id(d.get("order_id"))
        ChatMessage.objects.create(session_id=d["session_id"], sender="customer", text=d["message"], order_id=oid)
        intent = detect_intent(d["message"])
        reply = "" if intent else "Sorry, I didn't get that. Please pick one of the options."
        if reply:
            ChatMessage.objects.create(session_id=d["session_id"], sender="bot", text=reply, order_id=oid)
        return Response({"intent": intent, "reply": reply})


class OrderDetailView(APIView):
    """GET /api/order/<order_id>/"""

    def get(self, request, order_id):
        oid = clean_id(order_id)
        if not ORDER_ID.match(oid):
            return Response({"error": "Order IDs look like FD1001."}, status=status.HTTP_400_BAD_REQUEST)
        order = get_object_or_404(Order, order_id=oid)
        return Response(OrderSerializer(order).data)


class CancelOrderView(APIView):
    """POST /api/cancel-order/  {order_id, reason}"""

    def post(self, request):
        s = CancelSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        order = get_object_or_404(Order, order_id=clean_id(s.validated_data["order_id"]))
        if not order.cancellable:
            return Response({"error": "This order can no longer be cancelled."}, status=status.HTTP_400_BAD_REQUEST)
        order.status = "cancelled"
        order.save(update_fields=["status"])
        CancellationRequest.objects.create(order=order, reason=s.validated_data["reason"])
        Refund.objects.get_or_create(order=order, defaults={"amount": order.total, "state": "Initiated"})
        return Response({"message": "Order cancelled. Refund started."})


class RefundStatusView(APIView):
    """GET /api/refund/<order_id>/"""

    def get(self, request, order_id):
        order = get_object_or_404(Order, order_id=clean_id(order_id))
        refund = getattr(order, "refund", None)
        return Response({"refund": RefundSerializer(refund).data if refund else None})


class SupportTicketView(APIView):
    """POST /api/support-ticket/  {order_id?, issue, escalate, session_id, transcript}"""

    def post(self, request):
        s = TicketCreateSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.validated_data
        order = Order.objects.filter(order_id=clean_id(d.get("order_id"))).first() if d.get("order_id") else None
        ticket = SupportTicket.objects.create(
            order=order, issue=d["issue"], escalated_to_human=d["escalate"],
            session_id=d.get("session_id", ""), transcript=d.get("transcript", []),
        )
        return Response({"ticket_id": ticket.ticket_id}, status=status.HTTP_201_CREATED)


class ChatHistoryView(APIView):
    """GET /api/chat-history/?session_id=...  (support agents read this)"""

    def get(self, request):
        sid = request.query_params.get("session_id")
        qs = ChatMessage.objects.filter(session_id=sid) if sid else ChatMessage.objects.all()[:200]
        return Response(ChatMessageSerializer(qs, many=True).data)
