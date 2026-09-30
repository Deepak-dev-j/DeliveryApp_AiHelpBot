from django.urls import path
from . import views

urlpatterns = [
    path("chat/", views.ChatView.as_view()),
    path("order/<str:order_id>/", views.OrderDetailView.as_view()),
    path("cancel-order/", views.CancelOrderView.as_view()),
    path("refund/<str:order_id>/", views.RefundStatusView.as_view()),
    path("support-ticket/", views.SupportTicketView.as_view()),
    path("chat-history/", views.ChatHistoryView.as_view()),
]
