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
    tickets = Ticket.objects.annotate(
        month=ExtractMonth('created_at'), 
        day=ExtractDay('created_at'), 
        year=ExtractYear('created_at')
    ).filter(
        Q(user=user) | Q(assigned_to=user.username) 
    ).order_by('-id')
    
    
    paginator = Paginator(tickets, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    all_users = User.objects.all()

    context = {
        'tickets': tickets,
        'all_users': all_users,
        'page_obj': page_obj,
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
            ticket.user = request.user  # Associate the logged-in user with the `user` field
            ticket.save()
            messages.success(request, 'Ticket has been created successfully')
            return redirect('dashboard')  # Redirect to the dashboard or any other view
    else:
        form = TicketForm()

    return render(request, 'ticket_form_modal.html', {'form': form})




def update_ticket_status(request, ticket_id):
    if request.method == 'POST':
        # Fetch the ticket
        ticket = get_object_or_404(Ticket, id=ticket_id)

        
        new_status = request.POST.get('status')
        assigned_user_username = request.POST.get('assigned_user')

        # Track changes
        status_changed = new_status and new_status != ticket.status
        user_changed = assigned_user_username and ticket.assigned_to != assigned_user_username

        if user_changed:
            assigned_user = get_object_or_404(User, username=assigned_user_username)
            ticket.assigned_to = assigned_user_username 
            ticket.status = 'Assigned'  
            messages.success(request, f'Ticket #{ticket.ticket_number} has been assigned to {assigned_user_username}')

        if status_changed:
            previous_status = ticket.status
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

    paginator = Paginator(tickets, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': q, 
    }
    return render(request, 'ticketlogs.html', context=context)

def report(request):
    orders = Ticket.objects.annotate(
        month_year=TruncMonth('date')
    ).values('month_year').annotate(
        count=Count('id')
    ).order_by('-month_year')
    status_options = Ticket.objects.values_list('status', flat=True).distinct()
    # pending_orders = Ticket.objects.filter( status='pending').count()
    available_months = [(order['month_year'].strftime('%B %Y'), order['month_year'].strftime('%Y-%m-01'), order['month_year'].strftime('%Y-%m-31')) for order in orders]

    ol = Ticket.objects.order_by('-id')
    orders1 = Ticket.objects.all()

    released_by_set = set()
    received_by_set = set()

    for order in orders1:
        if order.released_by:
            released_by_set.add(order.released_by)
        if order.returned_to:
            received_by_set.add(order.returned_to)
    
    order_id = request.GET.get('id')
    name = request.GET.get('name')
    issued_to = request.GET.get('issued_to')
    itemName = request.GET.get('item_name')
    quantity = request.GET.get('request_quantity')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    status = request.GET.get('status')
    released_by = request.GET.get('released_by')
    received_by = request.GET.get('received_by')

    request.session['id'] = order_id
    request.session['name'] = name
    request.session['issued_to'] = issued_to
    request.session['item_name'] = itemName
    request.session['date_from'] = date_from
    request.session['date_to'] = date_to
    request.session['status'] = status
    request.session['released_by'] = released_by
    request.session['received_by'] = received_by

    # Filter queryset based on search parameters
    ol = ol.filter(
        Q(date__range=[date_from, date_to]) if date_from and date_to else Q()
    )
    if is_valid_queryparam(order_id):
        ol = ol.filter(id=order_id)
    if is_valid_queryparam(name):
        ol = ol.filter(users__username__icontains=name)
    if is_valid_queryparam(issued_to):
        ol = ol.filter(issued_to__icontains=issued_to)
    if is_valid_queryparam(itemName):
        ol = ol.filter(item_name__name__icontains=itemName)
    if is_valid_queryparam(quantity):
        ol = ol.filter(request_quantity=quantity)
    if is_valid_queryparam(status):
        ol = ol.filter(status=status)
    if is_valid_queryparam(released_by):
        ol = ol.filter(released_by__icontains=released_by)
    if is_valid_queryparam(received_by):
        ol = ol.filter(returned_to__icontains=received_by)

    page = request.GET.get('page', 1)
    paginator = Paginator(ol, 30)

    try:
        ol = paginator.page(page)
    except PageNotAnInteger:
        ol = paginator.page(1)
    except EmptyPage:
        ol = paginator.page(paginator.num_pages)

    user = request.user
    is_sub_admin = user.groups.filter(name='sub-admin').exists()

    context = {
        'orders1' : orders,
        'order_list': ol,
        'order_id' : order_id,
        'name': name,
        'issued_to' : issued_to,
        'itemName': itemName,
        'quantity': quantity,
        'date_from': date_from,
        'date_to': date_to,
        'status': status,
        'released_by': released_by,
        'received_by': received_by,
        'available_months': available_months,
        'released_by_options': released_by_set,
        'received_by_options': received_by_set,
        'status_options' : status_options,
        'is_sub_admin' : is_sub_admin,
        'pending_orders' : pending_orders,
    }
    return render(request, 'dashboard/report.html', context)

@login_required
def order_excel(request):
    ol = Order.objects.order_by('users')

    order_id = request.session.get('id')
    name = request.session.get('name')
    issued_to = request.session.get('issued_to')
    itemName = request.session.get('item_name')
    date_from = request.session.get('date_from')
    date_to = request.session.get('date_to')
    status = request.session.get('status')
    released_by = request.session.get('released_by')
    received_by = request.session.get('received_by')

    # Apply filters to the queryset
    ol = ol.filter(
        Q(date__range=[date_from, date_to]) if date_from and date_to else Q()
    )
    if is_valid_queryparam(order_id):
        ol = ol.filter(id=order_id)
    if is_valid_queryparam(name):
        ol = ol.filter(users__username__icontains=name)
    if is_valid_queryparam(issued_to):
        ol = ol.filter(issued_to__icontains=issued_to)
    if is_valid_queryparam(itemName):
        ol = ol.filter(item_name__name__icontains=itemName)
    if is_valid_queryparam(status):
        ol = ol.filter(status=status)
    if is_valid_queryparam(released_by):
        ol = ol.filter(released_by__icontains=released_by)
    if is_valid_queryparam(received_by):
        ol = ol.filter(returned_to__icontains=received_by)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="Request Report {date_from} to {date_to}.xlsx"'
    workbook = Workbook()

    worksheet = workbook.active
    worksheet.merge_cells('A1:J1')
    worksheet.merge_cells('A2:J2')
    first_cell = worksheet.cell(row=1, column=1)
    first_cell.value = f"Report For Requests Generated on {timezone.now()}"

    first_cell.font = Font(bold=True)
    first_cell.alignment = Alignment(horizontal="center", vertical="center")

    worksheet.title = f'Request List {date_from} to {date_to}'

    columns = ['Request ID', 'Issued By','Issued To', 'Item Name', 'Quantity', 'Date Created', 'Date Received', 'Status', 'Released By', 'Received By']
    row_num = 3

    for col_num, column_title in enumerate(columns, 1):
        cell = worksheet.cell(row=row_num, column=col_num)
        cell.value = column_title
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center", vertical="center")
        
        column_letter = get_column_letter(col_num)
        worksheet.column_dimensions[column_letter].width = max(len(str(column_title)), 12)

    for order in ol:
        row_num += 1
        row = [order.id , order.users.username, order.issued_to, order.item_name.name, order.request_quantity,
               order.date.replace(tzinfo=None) if order.date else None,
               order.returned_date.replace(tzinfo=None) if order.returned_date else None,
               order.status, order.released_by, order.returned_to]

        for col_num, cell_value in enumerate(row, 1):
            cell = worksheet.cell(row=row_num, column=col_num)
            cell.value = cell_value
            if isinstance(cell_value, datetime):
                cell.number_format = 'yyyy-mm-dd HH:MM:SS'
            column_letter = get_column_letter(col_num)
            worksheet.column_dimensions[column_letter].width = max(worksheet.column_dimensions[column_letter].width, len(str(cell_value)) + 2)

        worksheet.row_dimensions[row_num].height = 14.4

    total_count_cell = worksheet.cell(row=row_num + 1, column=1)
    total_count_cell.value = "Total Count"
    total_count_cell.font = Font(bold=True)
    total_count_cell.alignment = Alignment(horizontal="center", vertical="center")
    
    total_count_value_cell = worksheet.cell(row=row_num + 1, column=2)
    total_count_value_cell.value = len(ol)
    total_count_value_cell.font = Font(bold=True)
    total_count_value_cell.alignment = Alignment(horizontal="center", vertical="center")

    workbook.save(response)
    return response


@login_required
def order_pdf(request):
    ol = Order.objects.order_by('id')

    # Retrieve filters from session
    order_id = request.session.get('id')
    name = request.session.get('name')
    issued_to = request.session.get('issued_to')
    itemName = request.session.get('item_name')
    date_from = request.session.get('date_from')
    date_to = request.session.get('date_to')
    status = request.session.get('status')
    released_by = request.session.get('released_by')
    received_by = request.session.get('received_by')

    # Apply filters to queryset
    ol = ol.filter(
        Q(date__range=[date_from, date_to]) if date_from and date_to else Q()
    )
    if is_valid_queryparam(order_id):
        ol = ol.filter(id=order_id)
    if is_valid_queryparam(name):
        ol = ol.filter(users__username__icontains=name)
    if is_valid_queryparam(issued_to):
        ol = ol.filter(issued_to__icontains=issued_to)
    if is_valid_queryparam(itemName):
        ol = ol.filter(item_name__name__icontains=itemName)
    if is_valid_queryparam(status):
        ol = ol.filter(status=status)
    if is_valid_queryparam(released_by):
        ol = ol.filter(released_by__icontains=released_by)
    if is_valid_queryparam(received_by):
        ol = ol.filter(returned_to__icontains=received_by)

    # Create a PDF report
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Inventory_Request_Report.pdf"'

    data = []
    header = ['Request ID', 'Issued By', 'Issued To', 'Item Name', 'Quantity', 'Date Created', 'Date Received', 'Status', 'Released By', 'Received By']
    data.append(header)
    for order in ol:
        data.append([order.id, order.users.username, order.issued_to, order.item_name.name, order.request_quantity,
                     order.date.replace(tzinfo=None) if order.date else None,
                     order.returned_date.replace(tzinfo=None) if order.returned_date else None,
                     order.status, order.released_by, order.returned_to])

    total_count = len(ol)

    doc = SimpleDocTemplate(response, pagesize=landscape(letter), leftMargin=20, rightMargin=20, topMargin=20, bottomMargin=20)
    
    table_style = TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])

    table = Table(data, style=table_style)
    styles = getSampleStyleSheet()
    
    elements = []
    elements.append(Paragraph(f"A Report of Requests Generated on {timezone.now()}", styles['title']))
    elements.append(Paragraph(f"Filters used:", styles['title']))
    elements.append(Paragraph(f"Request ID: {order_id if order_id else 'All'}, Name: {name if name else 'All'}, Item Name: {itemName if itemName else 'All'}, Date From: {date_from if date_from else 'All'}, Date To: {date_to if date_to else 'All'}, Status: {status if status else 'All'}, Released By: {released_by if released_by else 'All'}, Received By: {received_by if received_by else 'All'}", styles['Normal']))
    elements.append(table)
    elements.append(Paragraph(f"Total Count of Requests: {total_count}", styles['Normal']))
    
    doc.build(elements)
    return response
