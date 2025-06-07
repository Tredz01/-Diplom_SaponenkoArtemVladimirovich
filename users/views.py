from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm, LoginForm
from .models import CustomUser


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('users:login_view')
    else:
        form = RegistrationForm()
    return render(request, 'users/register.html', {'form': form})
    

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('users:profile')
    else:
        form = LoginForm()
    return render(request, 'users/authorization.html', {'form': form})




@login_required
def profile_views(request):
    return render(request, 'users/profile.html', {'user': request.user})


@login_required
def account_details(request):
    user = CustomUser.objects.get(id=request.user.id)
    return render(request, 'users/partials/account_details.html',
                  {'user': user})
     
       
def logout_view(request):
    logout(request)
    return redirect('users:register')
