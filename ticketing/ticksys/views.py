from django.shortcuts import render, redirect, get_object_or_404
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
from django.views import generic
from django.urls import reverse_lazy, reverse
from bootstrap_modal_forms.generic import (
  BSModalCreateView,
  BSModalUpdateView,
  BSModalDeleteView
)
from django.views.generic.edit import CreateView


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
    user_tickets_today = Ticket.objects.filter(user=user, created_at__date=today).count()
    assigned_to = Ticket.objects.filter( agent=user, status='Assigned' or 'In Progress').count()
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
    tickets_by_user = Ticket.objects.filter(user=user).order_by('-created_at')

    context = {
        'tickets_by_user' : tickets_by_user
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
            messages.success(request, 'Ticket created successfully.')
            return redirect('dashboard')  # Redirect to the dashboard or any other view
    else:
        form = TicketForm()

    return render(request, 'ticket_form_modal.html', {'form': form})


# def update_ticket_status(request, ticket_number):
#     """This function updates ticket status"""
#     user = request.user
#     if request.method == 'POST':
#         tickets = get_object_or_404(Ticket, id=ticket_number)
#         new_status = request.POST.get('status')

#         try:
#             # Check if the status is being changed to 'released'
#             if new_status == 'Assigned':
#                 Ticket.status = new_status
#                 tickets.approved_by = request.user.username  # Set the approved_by field to the username of the admin
#                 tickets.save()
#                 messages.success(request, f"Request with ID {ticket_number} has been Assigned by {request.user.username}.")
#             elif new_status == 'released':
#                 order.status = new_status
#                 order.released_by = request.user.username  # Set the released_by field to the username of the admin
#                 order.save()
#                 messages.success(request, f"Request with ID {order.id} has been released by {request.user.username}.")
#             elif new_status == 'returned':
#                 order.status = new_status
#                 order.returned_to = request.user.username  # Set the returned_to field to the username of the admin
#                 order.save()
#                 messages.success(request, f"Request with ID {order.id} has been received by {request.user.username}.")
#             else:
#                 order.status = new_status
#                 order.save()
#                 messages.success(request, f"Request {order.id} status has been updated.")
#         except ValidationError as e:
#             messages.error(request, e.message)
    
#     return redirect('view-request')