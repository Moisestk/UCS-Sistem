from django.urls import path, re_path
from appsistem import views
from django.conf import settings
from django.views.static import serve
from django.contrib.auth import views as auth_views 

urlpatterns = [
  
    path('', views.home, name='home'),
    
    path('inicio/', views.inicio, name='inicio'),
    
    path('login/', views.loginuser, name='login'),
    
    path('register/', views.registro, name='register'),
    
    path('cerrar/', views.cerrar, name='cerrar'),
    
    path('subir/', views.subir_proyecto, name='subir'),
    
    path ('misproyectos/', views.misproyectos, name='misproyectos'),
    
    path ('editar/<id>/', views.editar, name= 'editarproyectos' ),
        
    #recuperacion de contraseña
    path('password_reset/',auth_views.PasswordResetView.as_view(),name='password_reset'),
    path('password_reset/done/',auth_views.PasswordResetDoneView.as_view(),name='password_reset_done'),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(),name='password_reset_confirm'),
    path('reset/done/',auth_views.PasswordResetCompleteView.as_view(),name='password_reset_complete')
   ]

urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve,{
        'document_root': settings.MEDIA_ROOT,
    })
]

 