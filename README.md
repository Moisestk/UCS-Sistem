# UCS-Sistem 🚀

**Sistema de Registro y Gestión de Proyectos - Universidad de las Ciencias de la Salud (UCS)**

Este proyecto es una plataforma web desarrollada en **Django** diseñada para centralizar, gestionar y supervisar el registro de proyectos de estudiantes en la UCS. Permite a los estudiantes subir sus trabajos por fases (momentos), recibir retroalimentación de los administradores y mantener un historial organizado de versiones.

---

## 📋 Características Principales

- **Gestión de Proyectos**: Registro completo con metadatos (título, autores, tutor, comunidad, etc.).
- **Sistema de Momentos**: Soporte para las 4 fases del proyecto (Momento I al IV) con control de versiones.
- **Roles de Usuario**:
  - **Estudiante**: Sube proyectos, actualiza versiones y consulta feedback.
  - **Administrador**: Revisa proyectos, asigna estados (Aprobado/Rechazado), y envía correcciones.
- **Seguridad Robusta**: 
  - Integración con **Google reCAPTCHA v2**.
  - Validación estricta de archivos (solo PDF y DOCX, máx 10MB).
  - Sistema de intentos fallidos de login y bloqueo de perfiles.
- **Notificaciones**: Alertas internas sobre cambios de estado y nuevos mensajes.
- **Panel Administrativo Premium**: Interfaz moderna utilizando `django-jazzmin`.
- **Papelera de Reciclaje**: Sistema para archivar y recuperar proyectos eliminados.

---

## 🛠️ Tecnologías Utilizadas

- **Backend**: Python 3.12 / Django 5.x
- **Base de Datos**: SQLite (desarrollo) / Soporta PostgreSQL/MySQL.
- **Seguridad**: `django-recaptcha`, `django-ratelimit`.
- **UI/UX**: HTML5, CSS3, JavaScript, `django-jazzmin` (Admin).
- **Herramientas**: `python-dotenv` para configuración, `Pillow` para imágenes.

---

## 🚀 Guía de Instalación (Local)

Sigue estos pasos para configurar el proyecto en tu PC:

### 1. Requisitos Previos
- Tener instalado **Python 3.12** o superior.
- Tener instalado **Git**.

### 2. Clonar el Proyecto
```bash
git clone <url-del-repositorio>
cd UCS-Sistem
```

### 3. Crear y Activar Entorno Virtual
```bash
# En Windows
python -m venv venv
.\venv\Scripts\activate

# En Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 4. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 5. Configurar Variables de Entorno
Crea un archivo `.env` en la raíz del proyecto (puedes copiar los valores del `.env` existente si está disponible) y configura lo siguiente:
```env
DJANGO_DEBUG=True
DJANGO_SECRET_KEY=tu-clave-secreta
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

# Configuración de Email (Opcional para desarrollo)
EMAIL_HOST_USER=tu-correo@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password
```

### 6. Ejecutar Migraciones
Crea la estructura de la base de datos:
```bash
python manage.py migrate
```

### 7. Crear Superusuario (Administrador)
Para acceder al panel de control:
```bash
python manage.py createsuperuser
```

### 8. Iniciar el Servidor
```bash
python manage.py runserver
```
Visita `http://127.0.0.1:8000` en tu navegador.

---

## 🔑 Configuración de reCAPTCHA
El proyecto usa claves de prueba para `localhost` por defecto en modo DEBUG. Si deseas usar claves reales:
1. Regístrate en [Google reCAPTCHA](https://www.google.com/recaptcha/admin).
2. Obtén tus claves (Site Key y Secret Key).
3. Añádelas a tu archivo `.env`:
   ```env
   RECAPTCHA_PUBLIC_KEY=tu_clave_publica
   RECAPTCHA_PRIVATE_KEY=tu_clave_privada
   ```

---

## 📁 Estructura del Proyecto
- `appsistem/`: Lógica principal (modelos, formularios, vistas de estudiantes).
- `panel/`: Vistas y lógica del panel administrativo.
- `sistema/`: Configuración central del proyecto Django.
- `media/`: Archivos subidos (proyectos y fotos de perfil).
- `staticfiles/`: Archivos estáticos recolectados.

---

**Desarrollado para la UCS - Gestión Eficiente de Proyectos de Investigación.**
