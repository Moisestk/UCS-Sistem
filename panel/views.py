from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import Q, Count
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.http import url_has_allowed_host_and_scheme
from django.conf import settings
import os

from appsistem.forms import (
    ProyectoForm,
    RegistrationStep1Form,
    RegistrationStep2Form,
    validate_document_file,
    LoginWithCaptchaForm,
)
from appsistem.models import (
    Pnf, Trayecto, Proyecto, Seccion, Momento, MomentoVersion,
    Notification, Profile
)
from appsistem.forms import PnfForm

# =========================
# Utilidades
# =========================

def norm(val):
    if val is None:
        return ''
    s = str(val).strip()
    return '' if s.lower() == 'none' else s

def to_int(val):
    try:
        return int(val)
    except (TypeError, ValueError):
        return None

# Autorización
# ---------------------------------------------------------
def is_admin(u):
    return u.is_staff

# =========================
# Panel Admin (auth + dashboard)
# =========================

def admin_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if not user.is_staff:
                return HttpResponseForbidden('Acceso restringido al panel (solo administradores).')
            login(request, user)
            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
                return redirect(next_url)
            return redirect('panel:dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'panel/login.html', {"form": form})

@login_required(login_url='/panel/login')
def admin_logout(request):
    logout(request)
    return redirect('panel:login')

# Logout: disponible para cualquier usuario autenticado
@login_required(login_url='/panel/login')
def admin_logout(request):
    logout(request)
    # Llevar al login del panel
    return redirect('panel:login')

@login_required(login_url='/panel/login')
def dashboard(request):
    # Estadísticas básicas (excluyendo proyectos en papelera)
    total = Proyecto.objects.filter(is_trashed=False).count()
    sin_revisar = Proyecto.objects.filter(revisado=False, is_trashed=False).count()
    aprobados = Proyecto.objects.filter(estado_revision='APROBADO', is_trashed=False).count()
    rechazados = Proyecto.objects.filter(estado_revision='RECHAZADO', is_trashed=False).count()
    en_revision = Proyecto.objects.filter(estado_revision='EN_REVISION', is_trashed=False).count()
    pendientes = Proyecto.objects.filter(estado_revision='PENDIENTE', is_trashed=False).count()
    usuarios_activos = User.objects.filter(is_active=True).count()

    # Estadísticas por PNF (excluyendo proyectos en papelera)
    pnf_stats = (
        Proyecto.objects
        .filter(is_trashed=False)
        .values('pnf__nombre_pnf')
        .annotate(
            total_proyectos=Count('id'),
            aprobados=Count('id', filter=Q(estado_revision='APROBADO')),
            rechazados=Count('id', filter=Q(estado_revision='RECHAZADO')),
            pendientes=Count('id', filter=Q(estado_revision__in=['PENDIENTE', 'EN_REVISION']))
        )
        .order_by('-total_proyectos')
    )

    # Cantidad total de PNFs
    total_pnfs = Pnf.objects.count()

    # Proyectos sin aprobar (pendientes + en revisión)
    proyectos_sin_aprobar = Proyecto.objects.filter(
        Q(estado_revision='PENDIENTE') |
        Q(estado_revision='EN_REVISION') | 
        Q(estado_revision__isnull=True) | 
        Q(estado_revision='') |
        ~Q(estado_revision__in=['APROBADO', 'RECHAZADO'])
    ).count()

    # Usuarios registrados por PNF
    usuarios_por_pnf = (
        User.objects
        .filter(proyecto__isnull=False)
        .values('proyecto__pnf__nombre_pnf')
        .annotate(usuarios_count=Count('id', distinct=True))
        .order_by('-usuarios_count')
    )

    # Estadísticas de momentos revisados
    momentos_stats = (
        Momento.objects
        .values('estado_revision')
        .annotate(
            cantidad=Count('id'),
            proyectos=Count('proyecto', distinct=True)
        )
        .order_by('estado_revision')
    )

    # Total de momentos por estado
    total_momentos = Momento.objects.count()
    momentos_corregidos = Momento.objects.filter(estado_revision='CORREGIDO').count()
    momentos_con_correcciones = Momento.objects.filter(estado_revision='CON_CORRECCIONES').count()
    momentos_pendientes = Momento.objects.filter(estado_revision='PENDIENTE').count()

    # Proyectos recientes (excluyendo proyectos en papelera)
    recent_projects = Proyecto.objects.filter(is_trashed=False).select_related('pnf', 'usuario').order_by('-fecha_subido')[:6]

    # Estadísticas de estados geográficos (excluyendo proyectos en papelera)
    estados_geograficos = (
        Proyecto.objects
        .filter(estado__isnull=False, is_trashed=False)
        .values('estado__nombre')
        .annotate(cantidad=Count('id'))
        .order_by('-cantidad')
    )

    # Estadísticas de estados de revisión de proyectos (para el gráfico principal) (excluyendo proyectos en papelera)
    estados_revision_stats = (
        Proyecto.objects
        .filter(is_trashed=False)
        .values('estado_revision')
        .annotate(cantidad=Count('id'))
        .order_by('-cantidad')
    )

    return render(request, 'panel/dashboard.html', {
        # Estadísticas básicas
        'total': total,
        'sin_revisar': sin_revisar,
        'aprobados': aprobados,
        'rechazados': rechazados,
        'en_revision': en_revision,
        'pendientes': pendientes,
        'usuarios_activos': usuarios_activos,
        'proyectos_sin_aprobar': proyectos_sin_aprobar,
        
        # Estadísticas por PNF
        'total_pnfs': total_pnfs,
        'pnf_stats': pnf_stats,
        'usuarios_por_pnf': usuarios_por_pnf,
        
        # Estadísticas de momentos
        'total_momentos': total_momentos,
        'momentos_corregidos': momentos_corregidos,
        'momentos_con_correcciones': momentos_con_correcciones,
        'momentos_pendientes': momentos_pendientes,
        'momentos_stats': momentos_stats,
        
        # Otros datos
        'recent_projects': recent_projects,
        'estados_geograficos': estados_geograficos,
        'estados_revision_stats': estados_revision_stats,
    })

# =========================
# Panel (proyectos)
# =========================

@login_required(login_url='/panel/login')
def projects_list(request):
    qs = Proyecto.objects.select_related('pnf', 'trayecto').filter(is_trashed=False)

    pnf_raw = request.GET.get('pnf')
    tray_raw = request.GET.get('trayecto')
    tutor = norm(request.GET.get('tutor'))
    fecha = norm(request.GET.get('fecha'))  # YYYY-MM-DD
    q = norm(request.GET.get('q'))
    estado_revision = request.GET.get('estado_revision')

    pnf = norm(pnf_raw)
    tray = norm(tray_raw)
    pnf_id = to_int(pnf)
    tray_id = to_int(tray)

    if pnf_id is not None:
        qs = qs.filter(pnf_id=pnf_id)
    if tray_id is not None:
        qs = qs.filter(trayecto_id=tray_id)
    if tutor:
        qs = qs.filter(tutor__icontains=tutor)
    if fecha:
        qs = qs.filter(fecha_subido=fecha)
    if q:
        qs = qs.filter(
            Q(autores__icontains=q) |
            Q(cedula__icontains=q) |
            Q(titulo__icontains=q)
        )
    if estado_revision:
        qs = qs.filter(estado_revision=estado_revision)

    # Conteos por estado sobre TODO el conjunto filtrado (no solo la página)
    # Los proyectos que se muestran como "En Revisión" en la tabla son:
    # - Los que tienen estado 'EN_REVISION' 
    # - Los que tienen estado nulo o vacío (se muestran como "En Revisión" por defecto)
    # - Los que tienen estados no reconocidos (como 'FALCON')
    en_revision_count = qs.filter(
        Q(estado_revision='EN_REVISION') | 
        Q(estado_revision__isnull=True) | 
        Q(estado_revision='') |
        ~Q(estado_revision__in=['PENDIENTE', 'APROBADO', 'RECHAZADO'])
    ).count()
    pending_count = qs.filter(estado_revision='PENDIENTE').count()
    approved_count = qs.filter(estado_revision='APROBADO').count()
    rejected_count = qs.filter(estado_revision='RECHAZADO').count()

    paginator = Paginator(qs.order_by('-fecha_subido'), 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    # Contar proyectos en papelera
    trash_count = Proyecto.objects.filter(is_trashed=True).count()
    
    return render(request, 'panel/projects_list.html', {
        'page_obj': page_obj,
        'pnfs': Pnf.objects.all(),
        'trayectos': Trayecto.objects.all(),
        'filters': {'pnf': pnf, 'trayecto': tray, 'tutor': tutor, 'fecha': fecha, 'q': q, 'estado_revision': estado_revision},
        'stats': {'pendientes': pending_count, 'en_revision': en_revision_count, 'aprobados': approved_count, 'rechazados': rejected_count},
        'trash_count': trash_count,
    })

@login_required(login_url='/panel/login')
def project_detail(request, pk):
    proyecto = get_object_or_404(Proyecto, pk=pk)

    # Asegurar momentos fijos
    fixed = ["MOMENTO I", "MOMENTO II", "MOMENTO III", "MOMENTO IV"]
    existing = set(proyecto.momentos.values_list('nombre', flat=True))
    for nombre in [m for m in fixed if m not in existing]:
        Momento.objects.create(proyecto=proyecto, nombre=nombre)

    momentos = proyecto.momentos.prefetch_related('versions').order_by('nombre')

    total_m = momentos.count()
    approved_m = momentos.filter(estado_revision='CORREGIDO').count()
    all_momentos_aprobados = (total_m >= 4 and approved_m == total_m)

    if request.method == 'POST':
        if request.POST.get('action') == 'aprobar_proyecto':
            if all_momentos_aprobados:
                proyecto.revisado = True
                proyecto.estado_revision = 'APROBADO'
                proyecto.save(update_fields=['revisado', 'estado_revision'])
                messages.success(request, 'Proyecto marcado como APROBADO.')
                Notification.objects.create(
                    recipient=proyecto.usuario,
                    proyecto=proyecto,
                    preview='Tu proyecto ha sido APROBADO por el administrador.'
                )
            else:
                messages.error(request, 'No se puede aprobar: aún hay momentos sin "Corregido".')
            return redirect('panel:project_detail', pk=pk)

        if request.POST.get('action') == 'desaprobar_proyecto':
            proyecto.revisado = False
            proyecto.estado_revision = 'RECHAZADO'
            proyecto.save(update_fields=['revisado', 'estado_revision'])
            messages.success(request, 'Proyecto marcado como RECHAZADO.')
            Notification.objects.create(
                recipient=proyecto.usuario,
                proyecto=proyecto,
                preview='Tu proyecto ha sido RECHAZADO por el administrador.'
            )
            return redirect('panel:project_detail', pk=pk)

        if request.POST.get('action') == 'quitar_aprobacion':
            proyecto.revisado = False
            proyecto.estado_revision = 'PENDIENTE'
            proyecto.save(update_fields=['revisado', 'estado_revision'])
            messages.success(request, 'Aprobación del proyecto removida. Estado cambiado a PENDIENTE.')
            Notification.objects.create(
                recipient=proyecto.usuario,
                proyecto=proyecto,
                preview='La aprobación de tu proyecto ha sido removida por el administrador.'
            )
            return redirect('panel:project_detail', pk=pk)

        if request.POST.get('action') == 'quitar_desaprobacion':
            proyecto.revisado = False
            proyecto.estado_revision = 'PENDIENTE'
            proyecto.save(update_fields=['revisado', 'estado_revision'])
            messages.success(request, 'Desaprobación del proyecto removida. Estado cambiado a PENDIENTE.')
            Notification.objects.create(
                recipient=proyecto.usuario,
                proyecto=proyecto,
                preview='La desaprobación de tu proyecto ha sido removida por el administrador.'
            )
            return redirect('panel:project_detail', pk=pk)

        if request.POST.get('form_type') == 'proyecto':
            estado = request.POST.get('estado')
            feedback = request.POST.get('feedback')
            nota = request.POST.get('nota')
            archivo = request.FILES.get('archivo')

            if estado:
                proyecto.estado = estado
            if feedback is not None:
                proyecto.feedback = feedback
            if nota:
                try:
                    proyecto.nota = int(nota)
                except ValueError:
                    pass
            if archivo:
                # Validar tipo de archivo
                try:
                    validate_document_file(archivo)
                except ValidationError as e:
                    messages.error(request, str(e))
                    return redirect('panel:project_detail', pk=pk)
                
                proyecto.archivo = archivo

            proyecto.save()
            return redirect('panel:project_detail', pk=pk)

        # Guardar cambios por momento y nueva versión desde admin
        m_id = request.POST.get('m_id')
        if m_id:
            momento = get_object_or_404(Momento, pk=m_id, proyecto_id=proyecto.id)
            m_estado = request.POST.get('m_estado_revision')
            m_feedback = request.POST.get('m_feedback')
            m_archivo = request.FILES.get('m_archivo')

            if m_estado is not None:
                momento.estado_revision = m_estado
            if m_feedback is not None:
                momento.feedback = m_feedback
            momento.save()

            if m_archivo:
                # Validar tipo de archivo
                try:
                    validate_document_file(m_archivo)
                except ValidationError as e:
                    messages.error(request, str(e))
                    return redirect('panel:project_detail', pk=pk)
                
                MomentoVersion.objects.create(
                    momento=momento,
                    archivo=m_archivo,
                    origen='ADMIN',
                    subido_por=request.user,
                )

            changes = []
            if m_estado is not None: changes.append(f"estado: {m_estado}")
            if m_feedback: changes.append("nuevo comentario")
            if m_archivo: changes.append("nueva versión subida por el admin")
            preview = f"Actualización en {momento.nombre}: " + ", ".join(changes) if changes else f"Actualización en {momento.nombre}"
            Notification.objects.create(
                recipient=proyecto.usuario,
                proyecto=proyecto,
                preview=preview[:250]
            )
            return redirect('panel:project_detail', pk=pk)

    keywords = []
    if getattr(proyecto, 'palabras_clave', None):
        keywords = [p.strip() for p in str(proyecto.palabras_clave).split(',') if p and p.strip()]

    return render(request, 'panel/project_detail.html', {
        'proyecto': proyecto,
        'ESTADOS': Proyecto.ESTADOS_REVISION,
        'momentos': momentos,
        'all_momentos_aprobados': all_momentos_aprobados,
        'keywords': keywords,
    })

# =========================
# Panel (gestión de usuarios) – SOLO ADMIN
# =========================

@login_required(login_url='/panel/login')
@user_passes_test(is_admin)
def users_list(request):
    qs = User.objects.filter(
        Q(profile__is_trashed=False) | Q(profile__isnull=True)
    ).order_by('id')

    nombre = norm(request.GET.get('nombre'))
    cedula = norm(request.GET.get('cedula'))
    q = norm(request.GET.get('q'))

    if nombre:
        qs = qs.filter(Q(first_name__icontains=nombre))
    if cedula:
        qs = qs.filter(username__icontains=cedula)
    if q:
        qs = qs.filter(
            Q(username__icontains=q) |
            Q(first_name__icontains=q) |
            Q(email__icontains=q)
        )

    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    # Contar usuarios en papelera
    users_trash_count = User.objects.filter(profile__is_trashed=True).count()

    return render(request, 'panel/users_list.html', {
        'page_obj': page_obj,
        'filters': {'nombre': nombre, 'cedula': cedula, 'q': q},
        'users_trash_count': users_trash_count,
    })

@login_required(login_url='/panel/login')
@user_passes_test(is_admin)
def users_trash_list(request):
    qs = (
        User.objects
        .select_related('profile')
        .filter(profile__is_trashed=True)
        .order_by('-profile__trashed_at')
    )
    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'panel/users_trash.html', {
        'page_obj': page_obj,
        'total_trashed': paginator.count,
    })

@login_required(login_url='/panel/login')
@user_passes_test(is_admin)
def user_trash_confirm(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if not getattr(user, 'profile', None) or not user.profile.is_trashed:
        messages.error(request, 'El usuario no está en papelera.')
        return redirect('panel:users_list')
    if user.is_superuser:
        messages.error(request, 'No puedes eliminar definitivamente a un superusuario.')
        return redirect('panel:users_trash_list')
    if user.id == request.user.id:
        messages.error(request, 'No puedes eliminar tu propia cuenta.')
        return redirect('panel:users_trash_list')
    return render(request, 'panel/user_hard_delete_confirm.html', {'user_obj': user})

@login_required(login_url='/panel/login')
@user_passes_test(is_admin)
def user_action(request, user_id):
    if request.method != 'POST':
        return HttpResponse('Método no permitido', status=405)
    action = request.POST.get('action')
    user = get_object_or_404(User, pk=user_id)

    if action == 'activate':
        user.is_active = True
        user.save(update_fields=['is_active'])
        messages.success(request, 'Usuario activado.')
    elif action == 'suspend':
        user.is_active = False
        user.save(update_fields=['is_active'])
        messages.success(request, 'Usuario suspendido.')
    elif action == 'delete':
        if user.is_superuser:
            messages.error(request, 'No puedes enviar a papelera a un superusuario.')
            return redirect('panel:users_list')
        if user.id == request.user.id:
            messages.error(request, 'No puedes enviarte a papelera a ti mismo.')
            return redirect('panel:users_list')
        prof, _ = Profile.objects.get_or_create(user=user)
        prof.is_trashed = True
        prof.trashed_at = timezone.now()
        prof.save(update_fields=['is_trashed', 'trashed_at'])
        user.is_active = False
        user.save(update_fields=['is_active'])
        messages.success(request, 'Usuario movido a la papelera.')
        return redirect('panel:users_trash_list')
    elif action == 'restore':
        prof, _ = Profile.objects.get_or_create(user=user)
        prof.is_trashed = False
        prof.trashed_at = None
        prof.save(update_fields=['is_trashed', 'trashed_at'])
        user.is_active = True
        user.save(update_fields=['is_active'])
        messages.success(request, 'Usuario restaurado.')
        return redirect('panel:users_list')
    elif action == 'hard_delete':
        if user.is_superuser:
            messages.error(request, 'No puedes eliminar definitivamente a un superusuario.')
            return redirect('panel:users_trash_list')
        if user.id == request.user.id:
            messages.error(request, 'No puedes eliminar tu propia cuenta.')
            return redirect('panel:users_trash_list')
        prof = getattr(user, 'profile', None)
        if not prof or not prof.is_trashed:
            messages.error(request, 'El usuario no está en la papelera.')
            return redirect('panel:users_list')
        password = request.POST.get('password') or ''
        if not request.user.check_password(password):
            messages.error(request, 'Contraseña de confirmación inválida.')
            return redirect('panel:user_trash_confirm', user_id=user.id)
        user.delete()
        messages.success(request, 'Usuario eliminado definitivamente.')
        return redirect('panel:users_trash_list')

    return redirect('panel:users_list')

# =========================
# Panel (perfil y notificaciones)
# =========================

@login_required(login_url='/panel/login')
def admin_profile(request):
    user = request.user
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_info':
            first_name = request.POST.get('first_name', '').strip()
            email = request.POST.get('email', '').strip()
            user.first_name = first_name
            user.email = email
            user.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('panel:profile')

        elif action == 'change_password':
            current = request.POST.get('current_password')
            new1 = request.POST.get('new_password1')
            new2 = request.POST.get('new_password2')

            if not user.check_password(current):
                messages.error(request, 'La contraseña actual es incorrecta.')
                return redirect('panel:profile')
            if new1 != new2:
                messages.error(request, 'Las contraseñas nuevas no coinciden.')
                return redirect('panel:profile')
            if not new1:
                messages.error(request, 'La nueva contraseña no puede estar vacía.')
                return redirect('panel:profile')

            user.set_password(new1)
            user.save()
            login(request, user)
            messages.success(request, 'Contraseña cambiada exitosamente.')
            return redirect('panel:profile')

        elif action == 'update_photo':
            photo = request.FILES.get('photo')
            if photo:
                profile, _ = Profile.objects.get_or_create(user=user)
                profile.photo = photo
                profile.save()
                messages.success(request, 'Foto de perfil actualizada.')
            else:
                messages.error(request, 'No se recibió un archivo de imagen.')
            return redirect('panel:profile')

    return render(request, 'panel/profile.html', {'user_obj': user})

@login_required(login_url='/panel/login')
def notifications_list(request):
    qs = Notification.objects.filter(recipient=request.user).select_related('proyecto').order_by('-created_at')
    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'panel/notifications_list.html', {'page_obj': page_obj})

@login_required(login_url='/panel/login')
def notification_open(request, pk):
    notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
    if not notif.is_read:
        notif.is_read = True
        notif.save(update_fields=['is_read'])
    if notif.proyecto_id:
        return redirect(notif.get_absolute_url())
    return redirect('panel:users_list')

@login_required(login_url='/panel/login')
@require_POST
def notifications_mark_all_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'ok': True})
    return redirect('panel:notifications_list')

# Alias opcional
@login_required(login_url='/panel/login')
@require_POST
def notification_mark_all_read(request):
    return notifications_mark_all_read(request)

@login_required(login_url='/panel/login')
@require_POST
def notification_mark_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
    if not notif.is_read:
        notif.is_read = True
        notif.save(update_fields=['is_read'])
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'ok': True})
    return redirect('panel:notifications_list')

# =========================
# Sitio público (estudiantes)
# =========================

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
            # Destino tras registro: solo staff/superuser va al panel
            if user.is_staff or user.is_superuser:
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
                messages.error(request, 'Tu usuario está bloqueado. Contacta al administrador para desbloquearlo.', extra_tags='blocked')
                return render(request, 'login-user.html', {'form': form})

            # Resetear intentos fallidos
            try:
                prof = user.profile
            except Profile.DoesNotExist:
                prof = Profile.objects.create(user=user)
            prof.failed_login_attempts = 0
            prof.locked_at = None
            prof.save(update_fields=['failed_login_attempts', 'locked_at'])

            login(request, user)
            # Destino tras login: solo staff/superuser va al panel
            if user.is_staff or user.is_superuser:
                return redirect('/panel/')
            return redirect('inicio')

        # Manejo de errores de login + CAPTCHA (simplificado)
        messages.error(request, 'Credenciales inválidas.', extra_tags='compact')

    return render(request, 'login-user.html', {'form': form})

def cerrar(request):
    logout(request)
    return redirect('login')

@login_required(login_url='/login')
def inicio(request):
    latest = Proyecto.objects.filter(usuario=request.user.id).order_by('-fecha_subido').first()
    has_projects = latest is not None
    return render(request, 'inicio.html', {
        'latest': latest,
        'has_projects': has_projects,
    })

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
    for nombre in [m for m in fixed if m not in existing]:
        Momento.objects.create(proyecto=proyecto, nombre=nombre)

    momentos = proyecto.momentos.prefetch_related('versions').order_by('nombre')

    order = ["MOMENTO I", "MOMENTO II", "MOMENTO III", "MOMENTO IV"]
    enabled = set()
    for i, name in enumerate(order):
        if i == 0:
            enabled.add(name)
        else:
            prev = proyecto.momentos.filter(nombre=order[i-1]).first()
            if prev and prev.estado_revision == 'CORREGIDO':
                enabled.add(name)

    return render(request, 'proyecto_detalle.html', {
        'proyecto': proyecto,
        'momentos': momentos,
        'enabled_moments': list(enabled),
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
            prev = momento.proyecto.momentos.filter(nombre=order[idx-1]).first()
            if not prev or prev.estado_revision != 'CORREGIDO':
                messages.error(request, f'Debes tener aprobado {order[idx-1]} antes de subir {momento.nombre}.')
                return redirect('proyecto_detalle', pk=momento.proyecto_id)

    archivo = request.FILES.get('archivo')
    if not archivo:
        return redirect('proyecto_detalle', pk=momento.proyecto_id)
    
    # Validar tipo de archivo
    try:
        validate_document_file(archivo)
    except ValidationError as e:
        messages.error(request, str(e))
        return redirect('proyecto_detalle', pk=momento.proyecto_id)

    MomentoVersion.objects.create(
        momento=momento,
        archivo=archivo,
        origen='ESTUDIANTE',
        subido_por=request.user,
    )

    admins = User.objects.filter(is_staff=True)
    preview = f"Nueva versión en {momento.nombre} del Proyecto #{momento.proyecto_id}"
    for admin in admins:
        Notification.objects.create(
            recipient=admin,
            proyecto=momento.proyecto,
            preview=preview,
        )

    return redirect('proyecto_detalle', pk=momento.proyecto_id)

@login_required(login_url='/login')
def student_notifications_list(request):
    qs = Notification.objects.filter(recipient=request.user).select_related('proyecto').order_by('-created_at')
    return render(request, 'mis_notificaciones.html', {'notifs': qs})

@login_required(login_url='/login')
def student_notification_mark_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
    if not notif.is_read:
        notif.is_read = True
        notif.save(update_fields=['is_read'])
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'ok': True})
    return redirect('mis_notificaciones')

@login_required(login_url='/login')
@require_POST
def student_notifications_mark_all_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
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
            user.first_name = f"{first_name} {last_name}".strip()
            user.email = email
            user.username = username
            user.save()
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

# === Endpoints para edición de usuarios (modal) – SOLO ADMIN ===

@login_required(login_url='/panel/login')
@user_passes_test(is_admin)
def user_get(request, user_id):
    """Devuelve datos para el modal de edición con rol inferido cuando falta."""
    user = get_object_or_404(User, pk=user_id)
    prof, _ = Profile.objects.get_or_create(user=user)

    role = (prof.role or '').strip().upper()
    if not role:
        role = 'ADMIN' if (user.is_superuser or user.is_staff) else 'ESTUDIANTE'
        try:
            prof.role = role
            prof.save(update_fields=['role'])
        except Exception:
            pass

    return JsonResponse({
        'ok': True,
        'user': {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name or '',
            'last_name': user.last_name or '',
            'email': user.email or '',
            'is_active': bool(user.is_active),
            'role': role,
        }
    })

@login_required(login_url='/panel/login')
@user_passes_test(is_admin)
@require_POST
def user_update(request, user_id):
    """Actualiza los datos recibidos desde el modal (AJAX o normal)."""
    user = get_object_or_404(User, pk=user_id)

    first_name = (request.POST.get('first_name') or '').strip()
    last_name  = (request.POST.get('last_name') or '').strip()
    email      = (request.POST.get('email') or '').strip()
    is_active  = request.POST.get('is_active') in ('1', 'true', 'True', 'on')
    role       = (request.POST.get('role') or '').strip()

    user.first_name = first_name
    user.last_name  = last_name
    user.email      = email
    user.is_active  = is_active
    user.save(update_fields=['first_name', 'last_name', 'email', 'is_active'])

    if role in ('ADMIN', 'ESTUDIANTE'):
        prof, _ = Profile.objects.get_or_create(user=user)
        prof.role = role
        prof.save(update_fields=['role'])

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'ok': True})
    messages.success(request, 'Usuario actualizado correctamente.')
    return redirect('panel:users_list')

# =========================
# Panel (gestión de PNFs)
# =========================

@login_required(login_url='/panel/login')
@user_passes_test(is_admin)
def pnfs_list(request):
    """Lista todos los PNFs con opciones de gestión"""
    qs = Pnf.objects.all().order_by('nombre_pnf')
    
    # Búsqueda
    search = norm(request.GET.get('search'))
    if search:
        qs = qs.filter(nombre_pnf__icontains=search)
    
    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    return render(request, 'panel/pnfs_list.html', {
        'page_obj': page_obj,
        'search': search,
        'total_pnfs': Pnf.objects.count(),
    })

@login_required(login_url='/panel/login')
@user_passes_test(is_admin)
def pnf_create(request):
    """Crear nuevo PNF"""
    if request.method == 'POST':
        form = PnfForm(request.POST)
        if form.is_valid():
            pnf = form.save()
            messages.success(request, f'PNF "{pnf.nombre_pnf}" creado exitosamente.')
            return redirect('panel:pnfs_list')
    else:
        form = PnfForm()
    
    return render(request, 'panel/pnf_form.html', {
        'form': form,
        'title': 'Crear Nuevo PNF',
        'action': 'Crear',
    })

@login_required(login_url='/panel/login')
@user_passes_test(is_admin)
def pnf_edit(request, pk):
    """Editar PNF existente"""
    pnf = get_object_or_404(Pnf, pk=pk)
    
    if request.method == 'POST':
        form = PnfForm(request.POST, instance=pnf)
        if form.is_valid():
            form.save()
            messages.success(request, f'PNF "{pnf.nombre_pnf}" actualizado exitosamente.')
            return redirect('panel:pnfs_list')
    else:
        form = PnfForm(instance=pnf)
    
    return render(request, 'panel/pnf_form.html', {
        'form': form,
        'title': f'Editar PNF: {pnf.nombre_pnf}',
        'action': 'Actualizar',
        'pnf': pnf,
    })

@login_required(login_url='/panel/login')
@user_passes_test(is_admin)
@require_POST
def pnf_delete(request, pk):
    """Eliminar PNF"""
    pnf = get_object_or_404(Pnf, pk=pk)
    
    # Verificar si hay proyectos asociados
    proyectos_count = Proyecto.objects.filter(pnf=pnf).count()
    if proyectos_count > 0:
        messages.error(request, f'No se puede eliminar el PNF "{pnf.nombre_pnf}" porque tiene {proyectos_count} proyecto(s) asociado(s).')
        return redirect('panel:pnfs_list')
    
    nombre_pnf = pnf.nombre_pnf
    pnf.delete()
    messages.success(request, f'PNF "{nombre_pnf}" eliminado exitosamente.')
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'ok': True})
    return redirect('panel:pnfs_list')

# =========================
# PAPELERA DE PROYECTOS
# =========================

@login_required(login_url='/panel/login')
@user_passes_test(is_admin)
def trash_list(request):
    """Lista de proyectos en papelera"""
    proyectos = Proyecto.objects.filter(is_trashed=True).order_by('-trashed_at')
    
    # Filtros
    search = request.GET.get('search', '')
    if search:
        proyectos = proyectos.filter(
            Q(titulo__icontains=search) |
            Q(usuario__username__icontains=search) |
            Q(usuario__first_name__icontains=search) |
            Q(usuario__last_name__icontains=search) |
            Q(cedula__icontains=search)
        )
    
    # Paginación
    paginator = Paginator(proyectos, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    return render(request, 'panel/trash_list.html', {
        'page_obj': page_obj,
        'search': search,
        'total_proyectos': proyectos.count(),
    })

@login_required(login_url='/panel/login')
@user_passes_test(is_admin)
def send_to_trash(request, proyecto_id):
    """Enviar proyecto a papelera"""
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    
    if request.method == 'POST':
        proyecto.is_trashed = True
        proyecto.trashed_at = timezone.now()
        proyecto.trashed_by = request.user
        proyecto.save()
        
        messages.success(request, f'Proyecto "{proyecto.titulo}" enviado a papelera.')
        return redirect('panel:trash_list')
    
    return render(request, 'panel/confirm_trash.html', {
        'proyecto': proyecto,
    })

@login_required(login_url='/panel/login')
@user_passes_test(is_admin)
def restore_from_trash(request, proyecto_id):
    """Restaurar proyecto desde papelera"""
    proyecto = get_object_or_404(Proyecto, id=proyecto_id, is_trashed=True)
    
    if request.method == 'POST':
        proyecto.is_trashed = False
        proyecto.trashed_at = None
        proyecto.trashed_by = None
        proyecto.save()
        
        messages.success(request, f'Proyecto "{proyecto.titulo}" restaurado exitosamente.')
        return JsonResponse({'success': True, 'message': 'Proyecto restaurado exitosamente'})
    
    # Si no es POST, redirigir a la papelera
    return redirect('panel:trash_list')

@login_required(login_url='/panel/login')
@user_passes_test(is_admin)
def permanent_delete(request, proyecto_id):
    """Eliminar proyecto permanentemente con verificación de contraseña"""
    proyecto = get_object_or_404(Proyecto, id=proyecto_id, is_trashed=True)
    
    if request.method == 'POST':
        password = request.POST.get('password', '')
        
        # Verificar contraseña del administrador
        if not request.user.check_password(password):
            messages.error(request, 'Contraseña incorrecta. No se pudo eliminar el proyecto.')
            return render(request, 'panel/confirm_permanent_delete.html', {
                'proyecto': proyecto,
                'error': 'Contraseña incorrecta'
            })
        
        # Eliminar archivos asociados
        if proyecto.archivo:
            try:
                if os.path.exists(proyecto.archivo.path):
                    os.remove(proyecto.archivo.path)
            except:
                pass  # Ignorar errores de archivos
        
        # Eliminar momentos y versiones
        for momento in proyecto.momentos.all():
            for version in momento.versions.all():
                try:
                    if os.path.exists(version.archivo.path):
                        os.remove(version.archivo.path)
                except:
                    pass
            momento.delete()
        
        titulo = proyecto.titulo
        proyecto.delete()
        
        messages.success(request, f'Proyecto "{titulo}" eliminado permanentemente.')
        return redirect('panel:trash_list')
    
    return render(request, 'panel/confirm_permanent_delete.html', {
        'proyecto': proyecto,
    })
