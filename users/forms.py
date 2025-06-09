from logging import PlaceHolder
from tkinter import Widget
from typing import Required
from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags
from .models import CustomUser
import re

User = get_user_model()


class RegistrationForm(UserCreationForm):
    
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'input-register form-control',
            'placeholder': 'Введите email',
            'autofocus': True
        }),
        label='логин (Email)'
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'input-register form-control',
            'placeholder': 'Введите пароль'
        }),
        label='пароль'
    )
    

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'input-register form-control',
            'placeholder': 'Повторите пароль'
        }),
        label='повтор пароля'
    )
    
    
    FIO = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'input-register form-controll',
            'placeholder': 'Введите ФИО'
        }),
        label='ФИО'
    )
    
    phone = forms.CharField(
        max_length=18,
        widget=forms.TextInput(attrs={
            'class': 'input-register form-control',
            'placeholder': '+7 (999) 999-99-99'
        }),
        label='номер телефона'
    )
    

    desired_group = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'input-register form-controll',
            'placeholder': 'название группы'
        }),
        label='Группа для вступления'
    )
    
    class Meta:
        model = CustomUser
        fields = ('email', 'password1', 'password2', 'FIO', 'phone', 'desired_group')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and CustomUser.objects.filter(email=email).exists():
            raise ValidationError('пользователь с таким email уже существует.')
        return email
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            phone_pattern = r'^\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}$'
            if not re.match(phone_pattern, phone):
                raise ValidationError('неверный формат номера телефона.')
            if CustomUser.objects.filter(phone=phone).exists():
                raise ValidationError('пользователь с таким номером телефона уже существует.')
        
        return phone
    
    def clean_FIO(self):
        FIO = self.cleaned_data.get('FIO')
        if FIO:
            words = FIO.strip().split()
            if len(words) < 2:
                raise ValidationError('ФИО должно содержать минимум имя и фамилию.')
        return FIO
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    """Форма авторизации с логином и паролем"""
    
    # Логин (переопределяем username как email)
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'input-auth form-control',
            'placeholder': 'введите логин (email)',
            'autofocus': True
        }),
        label='Логин'
    )
    
    # Пароль
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'input-auth form-control',
            'placeholder': 'введите пароль'
        }),
        label='Пароль'
    )
    

    
    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if email and password:
            self.user_cache = authenticate(
                self.request,
                email=email,
                password=password
            )
            if self.user_cache is None:
                raise ValidationError(
                    'неверная почта или пароль.',
                    code='invalid_login'
                )
            else:
                self.confirm_login_allowed(self.user_cache)
        
        return self.cleaned_data
    

class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField( 
        label="Email",
        max_length=50,
        widget=forms.EmailInput(attrs={'class': 'input-register form-control', 'placeholder': 'ваша почта'})
    )

class PasswordResetConfimForm(forms.Form):
    new_password1 = forms.CharField(
        label="новый пароль",
        widget=forms.PasswordInput(attrs={'class': 'input-register form-control', 'placeholder': 'новый пароль'})
    )
    new_password2 = forms.CharField(
        label="подтвердите новый пароль",
        widget=forms.PasswordInput(attrs={'class': 'input-register form-control', 'placeholder': 'новый пароль'})
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError("пароли не совпадают")
        return cleaned_data