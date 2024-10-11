import uuid
from django.db import models
from django.contrib.auth.models import User

class Ticket(models.Model):
    TICKET_STATUS = [
        ('Assigned', 'Assigned'),
        ('In Progress', 'In Progress'),
        ('Done', 'Done'),
    ]
    
    CLIENT_TYPE = [
        ('Staff', 'Staff'),
        ('Student', 'Student'),
    ]
    
    MODE_CHOICES = [
        ('Walk-In', 'Walk-In'),
        ('Phone', 'Phone'),
        ('Email', 'Email'),
    ]

    # New UUID field for ticket number
    ticket_number = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    id_number = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=TICKET_STATUS, default='Assigned')
    category = models.CharField(max_length=100)
    client_type = models.CharField(max_length=20, choices=CLIENT_TYPE)
    agent = models.ForeignKey('Agent', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    mode = models.CharField(max_length=20, choices=MODE_CHOICES, default='Walk-In')

    def __str__(self):
        return f"Ticket {self.ticket_number} - {self.id_number} - {self.category} ({self.status})"


class Agent(models.Model):
    user = models.ForeignKey(User, models.CASCADE, null=True)
    full_name = models.CharField(max_length=100)
    image = models.ImageField(default='avatar.jpg', upload_to='Profile_Images')

    def __str__(self):
        return self.username

class TicketLog(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='logs')
    status = models.CharField(max_length=20, choices=Ticket.TICKET_STATUS)
    timestamp = models.DateTimeField(auto_now_add=True)
    agent = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Log for Ticket {self.ticket.id_number} at {self.timestamp}"
