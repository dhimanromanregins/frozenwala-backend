from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .forms import CustomAuthenticationForm  # Assuming you have a custom authentication form
AUTH_USER_MODEL = 'backendlogin.BackendCustomUser'

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password,is_staff=True)

            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', reverse('backend/dashboard'))
                return redirect(next_url)
            else:
                return render(request, 'backend/login.html', {'form': form, 'error': 'Invalid login credentials'})
    else:
        form = CustomAuthenticationForm()

    return render(request, 'backend/login.html', {'form': form, 'error': 'Invalid login credentials'})



def logout_view(request):
    logout(request)
    return redirect('backend/login')
@login_required(login_url='backend/login')
def dashboard(request):
    return render(request, 'backend/dashboard.html')