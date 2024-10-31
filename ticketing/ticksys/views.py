from django.shortcuts import render, redirect
from .models import *
from .forms import *
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
from django.db.models.functions import TruncMonth
from django.db.models import Count
from datetime import datetime
from django.template.loader import render_to_string
from django.http import JsonResponse


# Create your views here.

def signup(request):
    if request.method == "POST":
        form = Register(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            first_name = form.cleaned_data.get("first_name")
            last_name = form.cleaned_data.get("last_name")
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password1")
            form.save()
            messages.success(request, f'Account has been created for {username}. Continue to Log in.')
            new_user = authenticate(username=username, password=password, first_name=first_name, last_name=last_name, email=email)
            if new_user is not None:
                login(request, new_user)
                return redirect('user-login')
            
            
    else:
        form = Register()

    context = {
        'form' : form,
    }
    return render(request, 'signup.html', context)

def index(request):
    user = request.user
    tickets = Ticket.objects.all()
    tickets_by_user = Ticket.objects.filter(user=user).count()

    current_year = timezone.now().year
    tickets_by_month = Ticket.objects.filter(created_at__year=current_year).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(count=Count('ticket_number')).order_by('month')

    months = [datetime(2000, i + 1, 1).strftime('%b') for i in range(12)]
    ticket_counts = [0] * 12

    for order in tickets_by_month:
        month_index = order['month'].month - 1
        ticket_counts[month_index] = order['count']

    today = timezone.now().date()
    user_tickets_today = Ticket.objects.filter(user=user, created_at__date=today).count()
    assigned_to = Ticket.objects.filter( agent=user, status='Assigned' or 'In Progress').count()
    total_resolved = Ticket.objects.filter(user=user, status='Done').count()
    context = {
        'user' : user,
        'tickets' : tickets,
        'tickets_by_user' : tickets_by_user,
        'user_tickets_today' : user_tickets_today,
        'assigned_to' : assigned_to,
        'total_resolved' : total_resolved,
        'months' : months,
        'ticket_counts' : ticket_counts

    }
    return render(request, 'index.html', context)

def ticketlogs(request):
    return render(request, 'ticketlogs.html')

def faqs(request):
    return render(request, 'faqs.html')


def search_ticket(request):
    if request.method == 'POST':
        form = TicketSearchForm(request.POST)
        if form.is_valid():
            id_number = form.cleaned_data.get('id_number')
            tickets = Ticket.objects.filter(id_number=id_number)

            # Render the search results to an HTML string
            html = render_to_string('partials/search_results.html', {'tickets': tickets}, request=request)
            return JsonResponse({'html': html})
    return JsonResponse({'html': '<p>No tickets found. Search for ticket history using ID Number.</p>'})