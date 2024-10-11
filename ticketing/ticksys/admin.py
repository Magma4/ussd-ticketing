from django.contrib import admin
from .models import Ticket, Agent, TicketLog

class TicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_number','id_number', 'category', 'status', 'client_type', 'agent', 'created_at')
    search_fields = ('ticket_number','id_number', 'category')

class TicketLogAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'status', 'timestamp', 'agent')

admin.site.register(Ticket, TicketAdmin)
admin.site.register(Agent)
admin.site.register(TicketLog, TicketLogAdmin)
