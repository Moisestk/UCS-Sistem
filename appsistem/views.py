from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseForbidden
from django.core.exceptions import PermissionDenied, ValidationError
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.contrib.auth.password_validation import validate_password
from django.db.models import Q

from .forms import ProyectoForm, RegistrationStep1Form, RegistrationStep2Form, LoginWithCaptchaForm
from .models import Pnf, Trayecto, Proyecto, Seccion, Momento, MomentoVersion, Notification, Profile


def home(request):
    return render(request, 'home.html')


def registro(request):
    step = request.POST.get('step') if request.method == 'POST' else '1'
    if request.method == 'GET' or step == '1':
        form1 = RegistrationStep1Form(request.POST or None)
        if request.method == 'POST' and form1.is_valid():
            request.session['reg_first_name'] = form1.cleaned_data['first_name']
            request.session['reg_last_name'] = form1.cleaned_data['last_name']
            request.session['reg_email'] = form1.cleaned_data['email']
            request.session['reg_password'] = form1.cleaned_data['password1']
            form2 = RegistrationStep2Form()
            return render(request, 'register.html', {'step': '2', 'form2': form2})
        return render(request, 'register.html', {'step': '1', 'form1': form1})

    form2 = RegistrationStep2Form(request.POST, request.FILES)
    if form2.is_valid():
        username = form2.cleaned_data['username']
        photo = form2.cleaned_data.get('photo')
        try:
            user = User.objects.create_user(
                username=username,
                password=request.session.get('reg_password'),
                email=request.session.get('reg_email'),
                first_name=request.session.get('reg_first_name'),
                last_name=request.session.get('reg_last_name', '')
            )
            user.save()
            if photo:
                prof, _ = Profile.objects.get_or_create(user=user)
                prof.photo = photo
                prof.save()

            for k in ['reg_first_name', 'reg_last_name', 'reg_email', 'reg_password']:
                request.session.pop(k, None)

            login(request, user)
            # Solo panel si es staff/superuser
            if user.is_superuser or user.is_staff:
                return redirect('/panel/')
            return redirect('inicio')
        except IntegrityError:
            messages.error(request, 'El nombre de usuario ya existe.')
    return render(request, 'register.html', {'step': '2', 'form2': form2})


def loginuser(request):
    form = LoginWithCaptchaForm(request, data=request.POST or None)
    if request.method == 'POST':
        username = (request.POST.get('username') or '').strip()
        if form.is_valid():
            user = form.get_user()
            if not user.is_active:
                messages.error(request, 'Tu usuario está bloqueado. Contacta al administrador para desbloquearlo.')
                return render(request, 'login-user.html', {'form': form})
            try:
                prof = user.profile
            except Profile.DoesNotExist:
                prof = Profile.objects.create(user=user)
            prof.failed_login_attempts = 0
            prof.locked_at = None
            prof.save(update_fields=['failed_login_attempts', 'locked_at'])

            login(request, user)
            # Solo panel si es staff/superuser
            if user.is_superuser or user.is_staff:
                return redirect('/panel/')
            return redirect('inicio')
        else:
            try:
                user = User.objects.get(username=username)
                prof, _ = Profile.objects.get_or_create(user=user)
                if not user.is_active:
                    messages.error(request, 'Tu usuario está bloqueado. Contacta al administrador para desbloquearlo.')
                else:
                    prof.failed_login_attempts = (prof.failed_login_attempts or 0) + 1
                    prof.save(update_fields=['failed_login_attempts'])
                    if prof.failed_login_attempts >= 5:
                        user.is_active = False
                        user.save(update_fields=['is_active'])
                        prof.locked_at = timezone.now()
                        prof.save(update_fields=['locked_at'])
                        admins = User.objects.filter(is_staff=True)
                        preview = f'Usuario "{user.username}" bloqueado por múltiples intentos fallidos.'
                        Notification.objects.bulk_create([
                            Notification(recipient=admin, proyecto=None, preview=preview)
                            for admin in admins
                        ])
                        messages.error(request, 'Has superado el número de intentos permitidos. Tu cuenta fue bloqueada y un administrador ha sido notificado.')
                    else:
                        restantes = 5 - prof.failed_login_attempts
                        messages.error(request, f'Credenciales inválidas. Intentos restantes: {restantes}.')
            except User.DoesNotExist:
                messages.error(request, 'Credenciales inválidas.')
    return render(request, 'login-user.html', {'form': form})


def cerrar(request):
    logout(request)
    return redirect('login')


@login_required(login_url='/login')
def inicio(request):
    latest = Proyecto.objects.filter(usuario=request.user.id).order_by('-fecha_subido').first()
    has_projects = latest is not None
    return render(request, 'inicio.html', {'latest': latest, 'has_projects': has_projects})


@login_required(login_url='/login')
def subir_proyecto(request):
    form = ProyectoForm(request.POST or None, request.FILES or None)
    pnfs = list(Pnf.objects.all())
    trayectos = list(Trayecto.objects.all())
    seccions = list(Seccion.objects.all())

    if request.method == 'POST' and form.is_valid():
        profile_photo = request.FILES.get('profile_photo')
        if profile_photo:
            prof, _ = Profile.objects.get_or_create(user=request.user)
            prof.photo = profile_photo
            prof.save()

        proyecto = form.save(commit=False)
        if not getattr(proyecto, 'usuario_id', None):
            proyecto.usuario = request.user
        proyecto.save()
        return redirect('proyecto_detalle', pk=proyecto.id)

    if request.method == 'POST':
        return render(request, 'subir.html', {
            'form': form, 'pnfs': pnfs, 'trayectos': trayectos, 'seccions': seccions
        })

    return render(request, 'subir.html', {
        'pnfs': pnfs, 'trayectos': trayectos, 'seccions': seccions
    })


@login_required(login_url='/login')
def misproyectos(request):
    ProyectosRegistrados = Proyecto.objects.filter(usuario=request.user.id)
    return render(request, 'misproyectos.html', {'Proyectos': ProyectosRegistrados})


@login_required(login_url='/editar')
def editar(request, id):
    proyecto = get_object_or_404(Proyecto, id=id)
    form = ProyectoForm(request.POST or None, request.FILES or None, instance=proyecto)
    pnfs = list(Pnf.objects.all())
    trayectos = list(Trayecto.objects.all())
    seccions = list(Seccion.objects.all())
    data = {'pnfs': pnfs, 'trayectos': trayectos, 'secciones': seccions, 'form': form}

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('/misproyectos')
    if request.method == 'POST':
        return render(request, 'editar.html', data)
    return render(request, 'editar.html', data)


@login_required(login_url='/login')
def student_project_detail(request, pk):
    proyecto = get_object_or_404(Proyecto, pk=pk)
    if proyecto.usuario_id != request.user.id:
        raise PermissionDenied

    fixed = ["MOMENTO I", "MOMENTO II", "MOMENTO III", "MOMENTO IV"]
    existing = set(proyecto.momentos.values_list('nombre', flat=True))
    to_create = [m for m in fixed if m not in existing]
    for nombre in to_create:
        Momento.objects.create(proyecto=proyecto, nombre=nombre)

    momentos = proyecto.momentos.prefetch_related('versions').order_by('nombre')
    order = ["MOMENTO I", "MOMENTO II", "MOMENTO III", "MOMENTO IV"]
    enabled = set()
    for i, name in enumerate(order):
        if i == 0:
            enabled.add(name)
        else:
            prev = proyecto.momentos.filter(nombre=order[i - 1]).first()
            if prev and prev.estado_revision == 'CORREGIDO':
                enabled.add(name)

    return render(request, 'proyecto_detalle.html', {
        'proyecto': proyecto, 'momentos': momentos, 'enabled_moments': list(enabled),
    })


@login_required(login_url='/login')
def momento_upload_version(request, momento_id):
    if request.method != 'POST':
        return HttpResponseForbidden('Método no permitido')

    momento = get_object_or_404(Momento, pk=momento_id)
    if momento.proyecto.usuario_id != request.user.id:
        raise PermissionDenied

    order = ["MOMENTO I", "MOMENTO II", "MOMENTO III", "MOMENTO IV"]
    if momento.nombre in order:
        idx = order.index(momento.nombre)
        if idx > 0:
            prev = momento.proyecto.momentos.filter(nombre=order[idx - 1]).first()
            if not prev or prev.estado_revision != 'CORREGIDO':
                messages.error(request, f'Debes tener aprobado {order[idx - 1]} antes de subir {momento.nombre}.')
                return redirect('proyecto_detalle', pk=momento.proyecto_id)

    archivo = request.FILES.get('archivo')
    if not archivo:
        return redirect('proyecto_detalle', pk=momento.proyecto_id)

    MomentoVersion.objects.create(momento=momento, archivo=archivo, origen='ESTUDIANTE', subido_por=request.user)

    admins = User.objects.filter(is_staff=True)
    preview = f"Nueva versión en {momento.nombre} del Proyecto #{momento.proyecto_id}"
    for admin in admins:
        Notification.objects.create(recipient=admin, proyecto=momento.proyecto, preview=preview)

    return redirect('proyecto_detalle', pk=momento.proyecto_id)


@login_required(login_url='/login')
def student_notifications_list(request):
    qs = (Notification.objects
          .filter(recipient=request.user)
          .select_related('proyecto')
          .order_by('-created_at'))
    return render(request, 'mis_notificaciones.html', {'notifs': qs})


@login_required(login_url='/login')
def student_notification_mark_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
    if not notif.is_read:
        notif.is_read = True
        notif.save(update_fields=['is_read'])
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        from django.http import JsonResponse
        return JsonResponse({'ok': True})
    return redirect('mis_notificaciones')


@login_required(login_url='/login')
@require_POST
def student_notifications_mark_all_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        from django.http import JsonResponse
        return JsonResponse({'ok': True})
    return redirect('mis_notificaciones')


@login_required(login_url='/login')
def student_profile(request):
    user = request.user
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_info':
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            email = request.POST.get('email', '').strip()
            username = request.POST.get('username', '').strip() or user.username

            # Validar cédula (solo números y exactamente 7 u 8 dígitos)
            if not username.isdigit() or len(username) not in (7, 8):
                messages.error(request, 'La cédula debe ser numérica y tener 7 u 8 dígitos.')
                return redirect('student_profile')

            # (Opcional) Evitar duplicados si cambia la cédula
            if username != user.username and User.objects.filter(username=username).exists():
                messages.error(request, 'Esta cédula ya está registrada como usuario.')
                return redirect('student_profile')

            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.username = username
            user.save(update_fields=['first_name', 'last_name', 'email', 'username'])
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('student_profile')

        elif action == 'change_password':
            current = request.POST.get('current_password')
            new1 = request.POST.get('new_password1')
            new2 = request.POST.get('new_password2')

            if not user.check_password(current):
                messages.error(request, 'La contraseña actual es incorrecta.')
                return redirect('student_profile')
            if new1 != new2:
                messages.error(request, 'Las contraseñas nuevas no coinciden.')
                return redirect('student_profile')
            if not new1:
                messages.error(request, 'La nueva contraseña no puede estar vacía.')
                return redirect('student_profile')

            user.set_password(new1)
            user.save()
            login(request, user)
            messages.success(request, 'Contraseña cambiada exitosamente.')
            return redirect('student_profile')

        elif action == 'update_photo':
            photo = request.FILES.get('photo')
            if photo:
                prof, _ = Profile.objects.get_or_create(user=user)
                prof.photo = photo
                prof.save()
                messages.success(request, 'Foto de perfil actualizada.')
            else:
                messages.error(request, 'No se recibió un archivo de imagen.')
            return redirect('student_profile')

    return render(request, 'student_profile.html', {'user_obj': user})


# ===== Panel: Listado (flag) y Creación de usuarios =====

@login_required(login_url='/login')
def panel_users_list(request):
    current = request.user
    try:
        current_role = getattr(current.profile, 'role', 'ESTUDIANTE')
    except Profile.DoesNotExist:
        current_role = 'ESTUDIANTE'

    can_add = bool(current.is_superuser or current_role == 'ADMIN')
    if not can_add:
        raise PermissionDenied

    name_q = (request.GET.get('name') or '').strip()
    email_q = (request.GET.get('email') or '').strip()

    qs = User.objects.all().select_related('profile').order_by('id')
    if name_q:
        qs = qs.filter(
            Q(username__icontains=name_q) |
            Q(first_name__icontains=name_q) |
            Q(last_name__icontains=name_q)
        )
    if email_q:
        qs = qs.filter(email__icontains=email_q)

    return render(request, 'panel_users.html', {
        'users': qs,
        'can_add_users': can_add,
    })


@login_required(login_url='/login')
def panel_user_create(request):
    """
    Crear usuarios ADMIN o ESTUDIANTE desde el panel.
    Permitido solo a superuser o Profile.role == 'ADMIN'.
    UI: panel/templates/panel/users_create.html
    """
    current = request.user
    try:
        role = getattr(current.profile, 'role', 'ESTUDIANTE')
    except Profile.DoesNotExist:
        role = 'ESTUDIANTE'

    if not (current.is_superuser or role == 'ADMIN'):
        raise PermissionDenied

    if request.method == 'POST':
        username   = (request.POST.get('username') or '').strip()
        first_name = (request.POST.get('first_name') or '').strip()
        last_name  = (request.POST.get('last_name') or '').strip()
        email      = (request.POST.get('email') or '').strip()
        role_sel   = request.POST.get('role')  # ADMIN | ESTUDIANTE
        p1         = request.POST.get('password1')
        p2         = request.POST.get('password2')

        # Campos requeridos y rol válido
        if not username or not p1 or not p2 or role_sel not in ('ADMIN', 'ESTUDIANTE'):
            messages.error(request, 'Completa los campos requeridos y selecciona un rol válido.')
            return render(request, 'panel/users_create.html', {
                'username': username, 'first_name': first_name, 'last_name': last_name,
                'email': email, 'role_sel': role_sel,
            })

        # Username = cédula numérica (exactamente 7 u 8 dígitos)
        if not username.isdigit() or len(username) not in (7, 8):
            messages.error(request, 'La cédula debe ser numérica y tener 7 u 8 dígitos.')
            return render(request, 'panel/users_create.html', {
                'username': username, 'first_name': first_name, 'last_name': last_name,
                'email': email, 'role_sel': role_sel,
            })
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Esta cédula ya está registrada.')
            return render(request, 'panel/users_create.html', {
                'username': username, 'first_name': first_name, 'last_name': last_name,
                'email': email, 'role_sel': role_sel,
            })

        # Contraseñas iguales
        if p1 != p2:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'panel/users_create.html', {
                'username': username, 'first_name': first_name, 'last_name': last_name,
                'email': email, 'role_sel': role_sel,
            })

        # Email único si se proporcionó
        if email and User.objects.filter(email__iexact=email).exists():
            messages.error(request, 'Este correo ya está registrado.')
            return render(request, 'panel/users_create.html', {
                'username': username, 'first_name': first_name, 'last_name': last_name,
                'email': email, 'role_sel': role_sel,
            })

        # Política de contraseña
        try:
            validate_password(p1)
        except ValidationError as ve:
            messages.error(request, '; '.join(ve.messages))
            return render(request, 'panel/users_create.html', {
                'username': username, 'first_name': first_name, 'last_name': last_name,
                'email': email, 'role_sel': role_sel,
            })

        # Crear usuario
        try:
            new_user = User.objects.create_user(
                username=username,
                password=p1,
                email=email,
                first_name=first_name,
                last_name=last_name,
            )
        except IntegrityError:
            messages.error(request, 'El nombre de usuario ya existe.')
            return render(request, 'panel/users_create.html', {
                'username': username, 'first_name': first_name, 'last_name': last_name,
                'email': email, 'role_sel': role_sel,
            })

        # Si el rol es ADMIN -> acceso al panel
        if role_sel == 'ADMIN':
            new_user.is_staff = True
            new_user.save(update_fields=['is_staff'])

        # Guardar rol en Profile (sin DOCENTE)
        prof, _ = Profile.objects.get_or_create(user=new_user)
        prof.role = role_sel
        prof.save(update_fields=['role'])

        messages.success(request, f'Usuario {username} creado como {role_sel.lower()}.')
        return redirect('panel:users_list')

    return render(request, 'panel/users_create.html')