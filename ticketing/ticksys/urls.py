from django.urls import path
from . import views

urlpatterns = [

    path('update_ticket/<int:pk>/', views.update_ticket_status, name='update_ticket_status'),
    path('index/', views.index, name='index'),
    path('ticketlogs/', views.ticketlogs, name='ticketlogs'),
    path('faqs/', views.faqs, name='faqs'),
    path('search_ticket/', views.search_ticket, name='search_ticket'),
    path('create_ticket/', views.TicketCreateView.as_view(), name='create_ticket'),
    path('ticket/<int:pk>/edit/', views.edit_ticket, name='edit_ticket'),
    path('ticket/<int:pk>/delete/', views.delete_ticket, name='delete_ticket'),
    path('searchdata', views.searchdata, name='searchdata'),
    path('ticket_excel', views.ticket_excel, name='ticket_excel'),
    path('notifications/', views.get_notifications, name='get_notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('mark-all-notifications-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
]
