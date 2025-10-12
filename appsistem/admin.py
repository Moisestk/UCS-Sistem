from django.contrib import admin
from .models import Pnf, Proyecto, Trayecto, Seccion, Profile


@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    search_fields = ('pnf__nombre_pnf','trayecto__nombre_trayecto', 'autores','tutor','cedula',)
    list_display = ('autores', 'cedula','pnf','trayecto', 'tutor', 'fecha_subido' )
    list_filter = ('pnf', 'trayecto', 'tutor', 'fecha_subido', )

admin.site.register(Seccion)
admin.site.register(Pnf)
admin.site.register(Trayecto)

@admin.action(description="Desbloquear usuarios seleccionados")
def desbloquear_usuarios(modeladmin, request, queryset):
    for profile in queryset.select_related('user'):
        user = profile.user
        if not user.is_active:
            user.is_active = True
            user.save(update_fields=['is_active'])
        profile.failed_login_attempts = 0
        profile.locked_at = None
        profile.save(update_fields=['failed_login_attempts', 'locked_at'])

# Acciones para cambiar rol
@admin.action(description="Marcar como Estudiante")
def set_role_estudiante(modeladmin, request, queryset):
    queryset.update(role='ESTUDIANTE')

@admin.action(description="Marcar como Docente")
def set_role_docente(modeladmin, request, queryset):
    queryset.update(role='DOCENTE')

@admin.action(description="Marcar como Administrador (no superuser)")
def set_role_admin(modeladmin, request, queryset):
    queryset.update(role='ADMIN')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'failed_login_attempts', 'locked_at', 'is_active')
    list_filter = ('role', 'locked_at')
    search_fields = ('user__username', 'user__email')
    actions = [desbloquear_usuarios, set_role_estudiante, set_role_docente, set_role_admin]

    def is_active(self, obj):
        return obj.user.is_active
    is_active.boolean = True
    is_active.short_description = 'Activo'