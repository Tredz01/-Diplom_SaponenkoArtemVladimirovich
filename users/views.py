from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoginForm, RegistrationForm, PasswordResetRequestForm, PasswordResetConfimForm
from .models import CustomUser
from .tasks import send_password_reset_email
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import  urlsafe_base64_decode
from django.utils.encoding import force_str
import logging
logger = logging.getLogger(__name__)


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


def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = CustomUser.objects.filter(email=email).first()
            if user:
                logger.info(f"Attempting to send password reset email to {email} for user ID {user.pk}")
                send_password_reset_email.delay(email, user.pk)
                messages.success(request, "электронное письмо для сброса пароля помещено в очередь. Пожалуйста, проверьте свой почтовый ящик или папку со спамом")
                return render(request, 'users/password_reset_done.html')
            else:
                messages.warning(request, "No account found with this email.")
        else:
            messages.error(request, "Please enter a valid email address.")
    else:
        form = PasswordResetRequestForm()
    return render(request, 'users/password_reset_request.html', {'form': form})


def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = PasswordResetConfimForm(request.POST)
            if form.is_valid():
                user.set_password(form.cleaned_data['new_password1'])
                user.save()
                messages.success(request, "ваш пароль был успешно измминен")
                return render(request, 'users/password_reset_complete.html')
        else:
            form = PasswordResetConfimForm()
        return render(request, 'users/password_reset_confirm.html', {'form': form, 'validlink': True})
    else:
        return render(request, 'users/password_reset_confirm.html', {'validlink': False})