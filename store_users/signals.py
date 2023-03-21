from django.db.models.signals import post_save
from django.dispatch import receiver

from store.models import Customer

from django.contrib.auth import get_user_model

User = get_user_model()


# https://stackoverflow.com/questions/69990075/create-user-and-userprofile-on-user-signup-with-django-allauth

@receiver(post_save, sender=User)
def create_customer(sender, instance, created, **kwargs):
    if created:
        name = instance.name
        email = instance.email

        Customer.objects.get_or_create(user=instance, name=name, email=email)