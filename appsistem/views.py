from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import IntegrityError
from . forms import ProyectoForm
from .models import Pnf, Trayecto, Proyecto, Seccion
# Create your views here.


#pagina inicial
def home (request):
    return render (request, 'home.html')

#rregistro de estudiantes
def registro (request):
    if request.method == 'GET':
       return render (request, 'register.html', {
        'from': UserCreationForm
       })
    else:
        if request.POST['password'] == request.POST['password2']:
            try:
                user = User.objects.create_user(
                    username=request.POST['username'], password=request.POST
                    ['password'], email=request.POST['email'], first_name=request.POST['first_name'])
                user.save()
                login(request, user)
                return redirect('inicio')
            except IntegrityError:
                return render (request, 'register.html', {
                    'from': UserCreationForm,
                    "error": 'El usuario ya existe'
                })
                
        return render (request, 'register.html', {
            'from': UserCreationForm,
            "error": ' Las contraseñas no son iguales'
            })

#inicio de sesion de estudiantes
def loginuser (request):
    if request.method == 'GET':
       return render(request, 'login-user.html',{
       'form': AuthenticationForm 
    })
    else:
        user = authenticate(
            request, username=request.POST['username'], password=request.POST
            ['password'])
        if user is None:
            return render (request, 'login-user.html', {
                'form': AuthenticationForm,
                'error': 'Datos Invalidos, asegurate de ingresarlos correctamente'
            })
        else:   
            login(request, user)
            return redirect('inicio')
        
#cerrar sesion estudiantes
def cerrar (request):
    logout (request)
    return redirect('login')

        
#Pagina con sesion iniciada        
@login_required(login_url='/login')
def inicio (request):
    return render (request, 'inicio.html')
  
#subir de proyectos
@login_required(login_url='/login')
def subir_proyecto (request):
    form= ProyectoForm(request.POST or None,request.FILES or None)
    pnfs= list(Pnf.objects.all())
    trayectos= list(Trayecto.objects.all())
    seccions= list(Seccion.objects.all())
    print(request.POST)
    print(request.FILES)
    if request.POST:
        if form.is_valid():
            form.save() 
            return redirect('/misproyectos')
        else:
            return render (request, 'subir.html',{"form":form,"pnfs":pnfs, "trayectos":trayectos, "seccions":seccions})
    else:
        form=ProyectoForm()
        return render (request, 'subir.html',{"pnfs":pnfs, "trayectos":trayectos, "seccions":seccions})
    
    
#misproyectos
@login_required(login_url='/login') 
def misproyectos (request):
    ProyectosRegistrados = Proyecto.objects.filter(usuario= request.user.id)
    return render (request, 'misproyectos.html', {'Proyectos': ProyectosRegistrados},)

#editar registro
@login_required (login_url='/editar')
def editar (request, id):
    proyecto = get_object_or_404 (Proyecto, id=id)
    form= ProyectoForm(request.POST or None,request.FILES or None, instance=proyecto)
    pnfs= list(Pnf.objects.all())   
    trayectos= list(Trayecto.objects.all())
    seccions= list(Seccion.objects.all())
    print(request.POST)
    print(request.FILES)
   
    data= {
        "pnfs":pnfs, "trayectos":trayectos, "secciones":seccions,
        'form':form
    }
    if request.POST:
        if form.is_valid():
            form.save()
            return redirect('/misproyectos')
        else:
            return render (request, 'editar.html', data)
    else:
        form=ProyectoForm(instance=proyecto)
        return render (request, 'editar.html', data)
 