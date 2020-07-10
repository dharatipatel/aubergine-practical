import datetime
import hashlib
import random
from django.utils import timezone

from users.models import UserVerification


def generate_verification_token(user_data):
    email = user_data['email']
    salt = hashlib.sha1((str(random.random())).encode('utf-8')).hexdigest()[:5]
    token = hashlib.sha1(
        (str(salt + email)).encode('utf-8')).hexdigest()

    expires_at = timezone.now() + datetime.timedelta(hours=24)
    if UserVerification.objects.filter(user_id=user_data['id']).exists():
        user_verification = UserVerification.objects.get(user_id=user_data['id'])
        user_verification.token = token
        user_verification.expires_at = expires_at
    else:
        user_verification = UserVerification(
            user_id=user_data['id'],
            token=token,
            expires_at=expires_at)
    user_verification.save()
    return token

