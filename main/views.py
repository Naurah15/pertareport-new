from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from main.forms import RegistrationForm, CustomLoginForm

def show_auth(request):
    context = {
        
    }
    return render(request, "auth.html", context)

def show_mainpage(request):
    context = {
        
    }
    return render(request, "mainpage.html", context)

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('main:login')  
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})


def login_user(request):
   if request.method == 'POST':
      form = CustomLoginForm(data=request.POST)

      if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('main:show_mainpage')

   else:
      form = CustomLoginForm(request)
   context = {'form': form}
   return render(request, 'login.html', context)

def logout_user(request):
    logout(request)
    return redirect('main:show_auth')