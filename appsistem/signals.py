from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Proyecto, Notification

@receiver(post_save, sender=Proyecto)
def create_notification_on_project(sender, instance: Proyecto, created, **kwargs):
    if not created:
        return
    titulo = getattr(instance, 'titulo', 'Nuevo proyecto')
    autores = getattr(instance, 'autores', '')
    preview = f'Nuevo proyecto: {titulo} — {autores}'.strip(' —')

    admins = User.objects.filter(is_staff=True, is_active=True)
    bulk = [
        Notification(recipient=admin, proyecto=instance, preview=preview)
        for admin in admins
    ]
    if bulk:
        Notification.objects.bulk_create(bulk, ignore_conflicts=True)
