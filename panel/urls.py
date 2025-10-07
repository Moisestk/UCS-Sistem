from django.urls import path
from . import views as panel_views
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps
from appsistem import views as app_views

app_name = 'panel'

def panel_access(view):
    @wraps(view)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"/panel/login/?next={request.get_full_path()}")
        if request.user.is_superuser or request.user.is_staff:
            return view(request, *args, **kwargs)
        messages.error(request, 'Debes autenticarte como administrador para acceder al panel.')
        return redirect(f"/panel/login/?next={request.get_full_path()}")
    return _wrapped

def admin_only(view):
    @wraps(view)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"/panel/login/?next={request.get_full_path()}")
        if request.user.is_superuser or request.user.is_staff:
            return view(request, *args, **kwargs)
        messages.error(request, 'Debes autenticarte como administrador para gestionar usuarios.')
        return redirect(f"/panel/login/?next={request.get_full_path()}")
    return _wrapped

urlpatterns = [
    path('login/', panel_views.admin_login, name='login'),
    path('logout/', panel_views.admin_logout, name='logout'),

    path('', panel_access(panel_views.dashboard), name='dashboard'),
    path('usuarios/', admin_only(panel_views.users_list), name='users_list'),
    path('usuarios/crear/', admin_only(app_views.panel_user_create), name='users_create'),
    path('usuarios/papelera/', admin_only(panel_views.users_trash_list), name='users_trash_list'),
    path('usuarios/<int:user_id>/accion/', admin_only(panel_views.user_action), name='user_action'),
    path('usuarios/<int:user_id>/papelera/confirmar/', admin_only(panel_views.user_trash_confirm), name='user_trash_confirm'),
    path('usuarios/<int:user_id>/get/', admin_only(panel_views.user_get), name='user_get'),
    path('usuarios/<int:user_id>/update/', admin_only(panel_views.user_update), name='user_update'),
    path('proyectos/', panel_access(panel_views.projects_list), name='projects_list'),
    path('proyectos/<int:pk>/', panel_access(panel_views.project_detail), name='project_detail'),
    path('notificaciones/', panel_access(panel_views.notifications_list), name='notifications_list'),
    path('notificaciones/<int:pk>/', panel_access(panel_views.notification_open), name='notification_open'),
    path('notificaciones/leer_todas/', panel_access(panel_views.notifications_mark_all_read), name='notifications_mark_all_read'),
    path('notificaciones/<int:pk>/marcar/', panel_access(panel_views.notification_mark_read), name='notification_mark_read'),
    path('perfil/', panel_access(panel_views.admin_profile), name='profile'),
]