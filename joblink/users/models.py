from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator

class CustomUserManager(BaseUserManager):
    def create_user(self, email, FIO, password, phone, desired_group, role=None, **extra_fields):
        if not email:
            raise ValueError('поле почты должно быть заполнено')
        if not FIO:
            raise ValueError('поле ФИО должно быть заполнено')
        if not password:
            raise ValueError('поде ввода пороля должно быть заполнено')
        if not phone:
            raise ValueError('поде телефона должно быть заполнено')
        if not desired_group:
            raise ValueError('поде группы должно быть заполнено')
        
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            FIO=FIO,
            phone=phone or '',
            desired_group=desired_group or '',
            role=role or UserRole.STUDENT,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, FIO, password=None, **extra_fields):
        """Создание суперпользователя"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', UserRole.TEACHER)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Суперпользователь должен иметь is_superuser=True.')
        
        return self.create_user(email, FIO, password, **extra_fields)  # Убрали self и явные None

class UserRole(models.TextChoices):
    STUDENT = 'student', 'Ученик'
    TEACHER = 'teacher', 'Учитель'

class CustomUser(AbstractUser):
    """Кастомная модель пользователя"""
    
    email = models.EmailField(
        unique=True, 
        max_length=50, 
        verbose_name='Email', 
        help_text='Обязательное поле'
    )
    FIO = models.CharField(max_length=100, verbose_name='ФИО')
    
    phone_regex = RegexValidator(
        regex=r'^\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}$',
        message="Номер телефона должен быть в формате: '+7 (999) 999-99-99'"
    )
    phone = models.CharField(
        validators=[phone_regex], 
        max_length=18, 
        verbose_name='Номер телефона',
        blank=True
    )
    
    role = models.CharField(
        max_length=10, 
        choices=UserRole.choices, 
        default=UserRole.STUDENT, 
        verbose_name='Роль'
    )
    
    desired_group = models.CharField(
        max_length=50, 
        verbose_name='Группа для вступления', 
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['FIO']

    def __str__(self):
        return self.FIO
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email.split('@')[0] if self.email else ''
        super().save(*args, **kwargs)
    
    @property
    def is_student(self):
        return self.role == UserRole.STUDENT
    
    @property
    def is_teacher(self):
        return self.role == UserRole.TEACHER