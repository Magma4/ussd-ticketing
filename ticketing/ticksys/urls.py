from django.urls import path
from . import views

urlpatterns = [
   
    path('index/', views.index, name='index'),
    path('ticketlogs/', views.ticketlogs, name='ticketlogs'),
    path('faqs/', views.faqs, name='faqs'),
    path('search_ticket/', views.search_ticket, name='search_ticket'),
    path('create_ticket/', views.TicketCreateView.as_view(), name='create_ticket'),
    path('update_ticket/<int:ticket_id>/', views.update_ticket_status, name='update_ticket_status'),
    path('searchdata', views.searchdata, name='searchdata'),
]