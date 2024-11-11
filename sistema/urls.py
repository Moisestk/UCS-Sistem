
from django.contrib import admin
from django.urls import path,include
from appsistem import views



urlpatterns = [
    path('admin/', admin.site.urls),
    
    #grafica
    
   
    path('',include("appsistem.urls"))
]
