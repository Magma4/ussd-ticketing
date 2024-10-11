from django.shortcuts import render, redirect
from .models import *

# Create your views here.
def index(request):
    return render(request, 'index.html')

def ticketlogs(request):
    return render(request, 'ticketlogs.html')

def faqs(request):
    return render(request, 'faqs.html')
