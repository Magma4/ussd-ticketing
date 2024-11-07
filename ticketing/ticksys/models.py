import uuid
from django.db import models
from django.contrib.auth.models import User
import random
import string


def generate_ticket_number():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
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

    CATEGORY = [
        ('Credentials', 'Credentials'),
        ('Fees & Payments', 'Fees & Payments'),
        ('VClass', 'VClass'),
        ('Transcript', 'Transcript'),
        ('Admission', 'Admission'),
        ('Wi-Fi', 'Wi-Fi'),
        ('Other', 'Other')
    ]

    # New UUID field for ticket number
    user = models.ForeignKey(User, models.CASCADE, null=True)
    ticket_number = models.CharField(max_length=4, default=generate_ticket_number, unique=True, editable=False)
    id_number = models.CharField(max_length=20, unique=False)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=TICKET_STATUS, default='In Progress')
    category = models.CharField(max_length=100, choices=CATEGORY)
    client_type = models.CharField(max_length=20, choices=CLIENT_TYPE, default='Student')
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


