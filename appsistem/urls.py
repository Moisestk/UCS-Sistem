from django.urls import path, re_path
from appsistem import views
from django.conf import settings
from django.views.static import serve

urlpatterns = [
    path('', views.home, name='home'),
    path('inicio/', views.inicio, name='inicio'),
    path('login/', views.loginuser, name='login'),
    path('register/', views.registro, name='register'),
    path('cerrar/', views.cerrar, name='cerrar'),

    # Perfil estudiante
    path('perfil/', views.student_profile, name='student_profile'),

    path('subir/', views.subir_proyecto, name='subir'),
    path('misproyectos/', views.misproyectos, name='misproyectos'),
    path('editar/<id>/', views.editar, name='editarproyectos'),

    # Detalle estudiante y subida por momento
    path('proyecto/<int:pk>/', views.student_project_detail, name='proyecto_detalle'),
    path('momento/<int:momento_id>/upload/', views.momento_upload_version, name='momento_upload'),

    # Notificaciones estudiante
    path('notificaciones/', views.student_notifications_list, name='mis_notificaciones'),
    path('notificaciones/<int:pk>/leer/', views.student_notification_mark_read, name='notif_leer'),
    path('notificaciones/leer_todas/', views.student_notifications_mark_all_read, name='mis_notificaciones_leer_todas'),

    # Panel - Usuarios
    path('panel/usuarios/', views.panel_users_list, name='panel_users_list'),
    path('panel/usuarios/crear/', views.panel_user_create, name='panel_user_create'),
]

if settings.DEBUG:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
        })
    ]