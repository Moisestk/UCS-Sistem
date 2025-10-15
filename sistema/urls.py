from django.contrib import admin
from django.urls import path, include
from appsistem import password_reset_views as pr_views  # vistas personalizadas

urlpatterns = [
    path('admin/', admin.site.urls),           # Admin de Django
    path('panel/', include('panel.urls')),     # Panel
    path('', include('appsistem.urls')),       # Sitio público

    # Recuperación de contraseña personalizada (UI del panel)
    path('password_reset/', pr_views.custom_password_reset, name='password_reset'),
    path('password_reset/done/', pr_views.custom_password_reset_done, name='password_reset_done'),
    path('reset/<uidb64>/<token>/', pr_views.custom_password_reset_confirm, name='password_reset_confirm'),
    path('reset/done/', pr_views.custom_password_reset_complete, name='password_reset_complete'),
]