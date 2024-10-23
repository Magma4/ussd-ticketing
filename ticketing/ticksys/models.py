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
    user = models.ForeignKey(User, models.CASCADE, null=True)
    ticket_number = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    id_number = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=TICKET_STATUS, default='Assigned')
    category = models.CharField(max_length=100)
    client_type = models.CharField(max_length=20, choices=CLIENT_TYPE)
    agent = models.CharField(max_length=100, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    mode = models.CharField(max_length=20, choices=MODE_CHOICES, default='Walk-In')

    def __str__(self):
        return f"Ticket {self.ticket_number} - {self.id_number} - {self.category} ({self.status})"


class Agent(models.Model):
    username = models.ForeignKey(User, models.CASCADE, null=True)
    image = models.ImageField(default='avatar.jpg', upload_to='Profile_Images')

    def __str__(self):
        return self.username.username


