from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_password_reset_email(email, user_id):
    from .models import CustomUser
    from django.urls import reverse
    from django.contrib.auth.tokens import default_token_generator
    from django.utils.http import urlsafe_base64_encode
    from django.utils.encoding import force_bytes

    logger.info(f"Starting password reset email task for {email}, user_id={user_id}")
    try:
        user = CustomUser.objects.get(pk=user_id)
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_url = f"{settings.SITE_URL}{reverse('users:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})}"
        subject = "Восстановление пароля"
        message = f"""
        Привет {user.FIO},

        Пожалуйста нажми на ссылку для восстановления твоего пароля:
        {reset_url}

        Если ты этого не делал проигнорируй данное сообщение


        Joblink
        Люберецкий техникум имени Героя Советского 
        Союза лётчика-космонавта Ю.А. Гагарина
        """
        html_message = f"""
        <h1>Восстановление пароля</h1>
        <p>Привет {user.FIO},</p>
        <p>Пожалуйста кликни по ссылке для восстановления пароля</p>
        <p><a href="{reset_url}">{reset_url}</a></p>
        <p>Если ты этого не делал проигнорируй данное сообщение</p>
        <p>Joblink<br>Люберецкий техникум имени Героя Советского 
        Союза лётчика-космонавта Ю.А. Гагарина, корпус Угреша</p>
        """
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
            html_message=html_message
        )
        logger.info(f"Password reset email sent to {email}")
    except Exception as e:
        logger.error(f"Failed to send password reset email to {email}: {str(e)}")
        raise