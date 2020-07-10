from celery import shared_task
from django.core.mail import send_mail

from aubergine_test.settings import FRONTEND_VERIFICATION_HANDLE
from users.utils import generate_verification_token


@shared_task
def send_verification_mail(user_data):
    verification_token = generate_verification_token(user_data)
    verification_link = FRONTEND_VERIFICATION_HANDLE + '/' + verification_token

    send_mail(
        'MyApp - Please verify your email',
        'Please click link below to start uploading images. \n %s' % verification_link,
        'hello@myapp.com',
        [user_data['email']],
        fail_silently=False,
    )
