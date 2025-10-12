from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import send_mail, get_connection
from django.conf import settings
from django.urls import reverse

# ===== Recuperación de contraseña (UI pública) =====

def custom_password_reset(request):
    """
    Formulario para solicitar el enlace de restablecimiento.
    Redirige a password_reset_done para no revelar si el email existe.
    """
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            users = User.objects.filter(email__iexact=email)
            user_count = users.count()
            print(f"[PASSWORD_RESET] email ingresado='{email}', usuarios_encontrados={user_count}")

            # Deduplicar: enviar una sola vez por dirección
            target_user = users.first()

            # Abrir conexión SMTP explícita (para diagnosticar 535)
            conn = get_connection()
            try:
                conn.open()
                try:
                    conn.connection.set_debuglevel(1)  # si está disponible
                except Exception:
                    pass
            except Exception as e:
                print(f"[PASSWORD_RESET][ERROR] No se pudo abrir conexión SMTP: {e!r}")
                messages.warning(request, 'No se pudo enviar el correo en este momento. Inténtalo nuevamente más tarde.')
                return redirect('password_reset_done')

            if target_user:
                uid = urlsafe_base64_encode(force_bytes(target_user.pk))
                token = default_token_generator.make_token(target_user)
                reset_url = request.build_absolute_uri(
                    reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
                )

                subject = (render_to_string('registration/password_reset_subject.txt', {}).strip()
                           or 'Restablece tu contraseña')

                message_html = render_to_string('registration/password_reset_email.html', {
                    'protocol': 'https' if request.is_secure() else 'http',
                    'domain': request.get_host(),
                    'uid': uid,
                    'token': token,
                    'user': target_user,
                    'reset_url': reset_url,
                })

                try:
                    send_mail(
                        subject,
                        message_html,                  # texto plano de fallback
                        settings.DEFAULT_FROM_EMAIL,
                        [target_user.email],
                        fail_silently=False,
                        html_message=message_html,     # HTML real
                        connection=conn,               # usar la conexión abierta
                    )
                    print(f"[PASSWORD_RESET] Envío aceptado para {target_user.email}")
                except Exception as e:
                    print(f"[PASSWORD_RESET][ERROR] Falló el envío para {target_user.email}: {e!r}")
                    messages.warning(request, 'No se pudo enviar el correo en este momento. Inténtalo nuevamente más tarde.')

            messages.info(request, f"Se procesó la solicitud de restablecimiento. Coincidencias: {user_count}.")
            return redirect('password_reset_done')
    else:
        form = PasswordResetForm()

    return render(request, 'panel_auth/reset_form.html', {'form': form})


def custom_password_reset_done(request):
    return render(request, 'panel_auth/reset_done.html')


def custom_password_reset_confirm(request, uidb64, token):
    """
    Página para definir la nueva contraseña si el token es válido.
    """
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except Exception:
        user = None

    if user is None or not default_token_generator.check_token(user, token):
        messages.error(request, 'El enlace de restablecimiento no es válido o ha expirado. Solicita uno nuevo.')
        return redirect('password_reset')

    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tu contraseña fue actualizada correctamente.')
            return redirect('password_reset_complete')
    else:
        form = SetPasswordForm(user)

    return render(request, 'panel_auth/reset_confirm.html', {'form': form})


def custom_password_reset_complete(request):
    return render(request, 'panel_auth/reset_complete.html')