"""
Contexto global de notificaciones.
Retorna conteos seguros incluso si el modelo no está disponible para evitar ImportError.
"""
from django.utils import timezone

# Intento defensivo de importar el modelo de notificaciones, considerando posibles nombres/ubicaciones
NotificationModel = None
try:
    # Caso 1: modelo en la app 'panel' con nombre 'Notificacion'
    from panel.models import Notificacion as NotificationModel  # type: ignore
except Exception:
    try:
        # Caso 2: modelo en 'appsistem' con nombre 'Notification'
        from appsistem.models import Notification as NotificationModel  # type: ignore
    except Exception:
        NotificationModel = None


def notifications(request):
    if not getattr(request, 'user', None) or not request.user.is_authenticated:
        return {
            'unread_count': 0,
            'notif_unread_count': 0,
            'notif_recent': [],
        }

    unread = 0
    recent = []

    if NotificationModel is not None:
        # Intentar con diferentes esquemas de campos sin romper la carga
        try:
            # Esquema: user/read/created_at
            unread = NotificationModel.objects.filter(user=request.user, read=False).count()
            recent = list(
                NotificationModel.objects.filter(user=request.user).order_by('-created_at')[:5]
            )
        except Exception:
            try:
                # Esquema alterno: recipient/is_read/created_at
                unread = NotificationModel.objects.filter(recipient=request.user, is_read=False).count()
                recent = list(
                    NotificationModel.objects.filter(recipient=request.user).order_by('-created_at')[:5]
                )
            except Exception:
                unread = 0
                recent = []

    return {
        'unread_count': unread,
        'notif_unread_count': unread,
        'notif_recent': recent,
    }