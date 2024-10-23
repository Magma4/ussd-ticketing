from django.urls import path
from . import views

urlpatterns = [
   
    path('index/', views.index, name='index'),
    path('ticketlogs/', views.ticketlogs, name='ticketlogs'),
    path('faqs/', views.faqs, name='faqs')
]