# Configuración de reCAPTCHA
## Para Desarrollo Local
El sistema está configurado para usar claves de prueba de Google en modo desarrollo, pero estas muestran el mensaje "This reCAPTCHA is for testing purposes only".

## Para Eliminar el Mensaje de Prueba

### Opción 1: Usar Claves Reales (Recomendado)

1. Ve a [Google reCAPTCHA Admin](https://www.google.com/recaptcha/admin)
2. Crea un nuevo sitio con:
   - **Tipo**: reCAPTCHA v2
   - **Dominios**: `localhost`, `127.0.0.1`
3. Copia las claves generadas
4. Actualiza `sistema/settings.py`:

```python
# Reemplazar estas líneas en settings.py
RECAPTCHA_PUBLIC_KEY = 'TU_CLAVE_PUBLICA_AQUI'
RECAPTCHA_PRIVATE_KEY = 'TU_CLAVE_PRIVADA_AQUI'
```

### Opción 2: Variables de Entorno

1. Crea un archivo `.env` en la raíz del proyecto:
```
RECAPTCHA_PUBLIC_KEY=TU_CLAVE_PUBLICA_AQUI
RECAPTCHA_PRIVATE_KEY=TU_CLAVE_PRIVADA_AQUI
```

2. Instala python-dotenv:
```bash
pip install python-dotenv
```

3. Agrega al inicio de `settings.py`:
```python
from dotenv import load_dotenv
load_dotenv()
```

## Claves Actuales (Solo para Desarrollo)

- **Pública**: `6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI`
- **Privada**: `6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe`

Estas claves funcionan pero muestran el mensaje de prueba.

## Para Producción

Asegúrate de usar claves reales registradas para tu dominio de producción.
