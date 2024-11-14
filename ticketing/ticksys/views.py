from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import *
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
from django.db.models.functions import TruncMonth, ExtractMonth, ExtractDay, ExtractYear
from django.db.models import Count
from datetime import datetime
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponseRedirect
from django.views import generic
from django.urls import reverse_lazy, reverse
from django.db.models import Q, Sum
from bootstrap_modal_forms.generic import (
  BSModalCreateView,
  BSModalUpdateView,
  BSModalDeleteView
)
from django.views.generic.edit import CreateView
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


# Create your views here.
class Index(generic.ListView):
    model = Ticket
    context_object_name = 'ticket'
    template_name = 'index.html'

# Create
class TicketCreateView(CreateView):
    model = Ticket
    form_class = TicketForm
    template_name = 'ticket_form_modal.html'
    success_url = reverse_lazy('index')
    success_message = 'Ticket created.'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request  # Pass request to the form
        return kwargs

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.user = self.request.user  # Assign the user to the instance
        instance.save()
        messages.success(self.request, "Ticket created")
        return super().form_valid(form)

# Update
# class TicketUpdateView(BSModalUpdateView):
#     model = Ticket
#     template_name = 'dashboard/order_update.html'
#     form_class = OrderForm
#     success_message = 'Request was updated.'

#     def form_valid(self, form):
#         instance = form.save(commit=False)  # Save the form data without committing to the database yet
#         request_quantity = instance.request_quantity
#         stock_quantity = instance.item_name.get_total_quantity()  # Use the method to get the total quantity

#         if request_quantity <= stock_quantity:
#             messages.success(self.request, "Request updated successfully")
#             return super().form_valid(form)  # This saves the form and redirects to success_url
#         else:
#             messages.error(self.request, "Requested quantity exceeds available stock")
#             # Redirecting to the same page if the form is not valid
#             return HttpResponseRedirect(self.request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

#     def get_context_data(self, **kwargs):
#         context = super(OrderUpdateView, self).get_context_data(**kwargs)
#         context['orders'] = Order.objects.all()  # Adding orders to the context
#         return context

#     def get_success_url(self):
#         # Check if the user is a superuser
#         if self.request.user.is_superuser:
#             return reverse('view-request')  # Redirect superusers to the dashboard
#         else:
#             return reverse('dashboard')


# # Delete
# class OrderDeleteView(BSModalDeleteView):
#     model = Order
#     template_name = 'dashboard/order_delete.html'
#     success_message = 'Request was deleted.'
    
    
#     def get_success_url(self):
#         # Check if the user is a superuser
#         if self.request.user.is_superuser:
#             return reverse('view-request')  # Redirect superusers to the dashboard
#         else:
#             return reverse('dashboard')
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
    form = TicketForm()
    tickets = Ticket.objects.all()
    tickets_by_user = Ticket.objects.filter(user=user).count()
    recent_tickets = Ticket.objects.filter(user=user).order_by('-created_at')[:10]

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
    # assigned_to_today = Ticket.objects.filter( user=user, updated_at__date=today).count()
    user_tickets_today = Ticket.objects.filter(user=user, created_at__date=today, updated_at__date=today).count()
    
    assigned_to = Ticket.objects.filter( user=user, status='Assigned' or 'In Progress').count()
    total_resolved = Ticket.objects.filter(user=user, status='Done').count()
    context = {
        'user' : user,
        'form' : form,
        'tickets' : tickets,
        'tickets_by_user' : tickets_by_user,
        'user_tickets_today' : user_tickets_today,
        'assigned_to' : assigned_to,
        'total_resolved' : total_resolved,
        'months' : months,
        'ticket_counts' : ticket_counts,
        'recent_tickets' : recent_tickets

    }
    return render(request, 'index.html', context)

def ticketlogs(request):
    user = request.user
    tickets = Ticket.objects.annotate(month=ExtractMonth('created_at'), day=ExtractDay('created_at'), year=ExtractYear('created_at')).order_by('-id').filter(user=user)
    
    # Paginate the orders, showing 10 per page
    paginator = Paginator(tickets, 15)  # Show 10 orders per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    all_users = User.objects.all()  # Retrieve all users to populate the dropdown
    tickets_by_user = Ticket.objects.filter(user=user).order_by('-created_at')

    context = {
        'tickets_by_user' : tickets_by_user,
        'all_users' : all_users,
        'page_obj' : page_obj,
    }

    return render(request, 'ticketlogs.html', context)

def faqs(request):
    return render(request, 'faqs.html')


def search_ticket(request):
    if request.method == 'POST':
        form = TicketSearchForm(request.POST)
        if form.is_valid():
            id_number = form.cleaned_data.get('id_number')
            tickets = Ticket.objects.filter(id_number=id_number).order_by('-created_at')

            # Render the search results to an HTML string
            html = render_to_string('partials/search_results.html', {'tickets': tickets}, request=request)
            return JsonResponse({'html': html})
    return JsonResponse({'html': '<p>No tickets found. Search for ticket history using ID Number.</p>'})


def create_ticket(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user  # Associate the logged-in user with the ticket
            ticket.save()
            messages.success(request, 'Ticket has been created successfully')
            return redirect('dashboard')  # Redirect to the dashboard or any other view
    else:
        form = TicketForm()

    return render(request, 'ticket_form_modal.html', {'form': form})


def update_ticket_status(request, ticket_id):
    if request.method == 'POST':
        ticket = get_object_or_404(Ticket, id=ticket_id)
        previous_status = ticket.status
        new_status = request.POST.get('status')
        assigned_user_username = request.POST.get('assigned_user')

        # Check if the assigned user is actually changing
        user_changed = assigned_user_username and ticket.user != get_object_or_404(User, username=assigned_user_username)
        
        if user_changed:
            # Only handle user assignment if it's actually a new user
            assigned_user = get_object_or_404(User, username=assigned_user_username)
            ticket.user = assigned_user
            ticket.status = 'Assigned'
            messages.success(request, f'Ticket #{ticket.ticket_number} has been assigned to {assigned_user}')
        elif new_status and new_status != previous_status:
            # Handle status change only if status is actually different
            ticket.status = new_status
            messages.success(request, f'Ticket #{ticket.ticket_number} status changed from {previous_status} to {new_status}')
            
        ticket.save()
        return redirect('ticketlogs')
    
    return HttpResponseRedirect('/')

def searchdata(request):
    user = request.user
    q = request.GET.get('query')  

    if q:
        try:
            tickets_by_user = Ticket.objects.filter(user=user)
            tickets = tickets_by_user.filter(
                Q(ticket_number__icontains=q) |
                Q(id_number__icontains=q)   
            )
        except ValueError:
            tickets_by_user = Ticket.objects.filter(user=user)
            tickets = tickets_by_user.filter(
                Q(ticket_number__icontains=q) |
                Q(id_number__icontains=q)
            )
    else:
        tickets = tickets_by_user.all()
        messages.error(request, "No results found")

    paginator = Paginator(tickets, 10)  # Paginate the results, 10 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': q, 
    }
    return render(request, 'ticketlogs.html', context=context)
