# using 'post_save' signal for User model to notify creation of a Profile
# model, due to the fact that we also have the admin app able to create users.

from django.db.models.signals import post_save
from .models import User, Profile, Voto
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from urllib.parse import urlencode
from django.conf import settings
import jwt
from datetime import datetime, timedelta

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()

@receiver(post_save, sender=Voto)
def send_email(sender, instance, created, **kwargs):
    if created:
        expires_in = timedelta(seconds=7)
        token_payload = {
            'vote_id': instance.id,
            'upload_id': instance.upload.id,
            'exp': datetime.utcnow() + expires_in
        }
        token = jwt.encode(token_payload, settings.SECRET_KEY, algorithm='HS256')
        validate_token_link = f"{settings.TOKEN_URL}/check-token"
        query_params = urlencode({'token': str(token)})
        verification_link = f"{validate_token_link}?{query_params}"
        subject = 'Avental - Validar Voto'
        from_email = settings.EMAIL_HOST_USER
        to_email = instance.email
        html_content = render_to_string('users/validate_vote.html', {'expires_in': expires_in, 'email': instance.email, 'verification_link': verification_link})
        text_content = 'Please enable HTML in your email client to view this message.'
        email = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        email.attach_alternative(html_content, 'text/html')
        email.send()