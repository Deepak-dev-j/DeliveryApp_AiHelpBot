from django.contrib import admin
from .models import Order, Refund, CancellationRequest, SupportTicket, ChatMessage


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_id", "restaurant", "total", "status", "payment_status")
    search_fields = ("order_id", "restaurant")


@admin.register(SupportTicket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("ticket_id", "order", "issue", "escalated_to_human", "status", "created_at")
    list_filter = ("status", "escalated_to_human")
    readonly_fields = ("transcript",)


admin.site.register(Refund)
admin.site.register(CancellationRequest)


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("session_id", "sender", "text", "order_id", "created_at")
    list_filter = ("sender",)
