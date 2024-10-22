from django.shortcuts import render, redirect
from .models import *
from .forms import Register, UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


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
    return render(request, 'index.html')

def ticketlogs(request):
    return render(request, 'ticketlogs.html')

def faqs(request):
    return render(request, 'faqs.html')
