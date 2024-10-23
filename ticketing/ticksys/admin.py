from django.contrib import admin
from .models import Ticket, Agent

class TicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_number','id_number', 'category', 'status', 'client_type', 'agent', 'created_at')
    search_fields = ('ticket_number','id_number', 'category')



admin.site.register(Ticket, TicketAdmin)
admin.site.register(Agent)
