"""
Middleware personalizado para ocultar mensajes de reCAPTCHA en desarrollo
"""
import re
from django.utils.deprecation import MiddlewareMixin

class RecaptchaDevMiddleware(MiddlewareMixin):
    """
    Middleware para ocultar mensajes de reCAPTCHA en desarrollo local
    """
    
    def process_response(self, request, response):
        # Solo aplicar en desarrollo
        from django.conf import settings
        if not settings.DEBUG:
            return response
            
        # Solo aplicar a respuestas HTML
        if 'text/html' not in response.get('Content-Type', ''):
            return response
            
        # Obtener el contenido de la respuesta
        content = response.content.decode('utf-8')
        
        # Patrones para ocultar mensajes de reCAPTCHA
        patterns = [
            # Mensaje de prueba en inglés
            r'<div[^>]*style="[^"]*color:\s*rgb\(204,\s*0,\s*0\)[^"]*"[^>]*>.*?testing purposes.*?</div>',
            r'<span[^>]*style="[^"]*color:\s*rgb\(204,\s*0,\s*0\)[^"]*"[^>]*>.*?testing purposes.*?</span>',
            r'<p[^>]*style="[^"]*color:\s*rgb\(204,\s*0,\s*0\)[^"]*"[^>]*>.*?testing purposes.*?</p>',
            
            # Mensaje de prueba en español
            r'<div[^>]*style="[^"]*color:\s*rgb\(204,\s*0,\s*0\)[^"]*"[^>]*>.*?solo para pruebas.*?</div>',
            r'<span[^>]*style="[^"]*color:\s*rgb\(204,\s*0,\s*0\)[^"]*"[^>]*>.*?solo para pruebas.*?</span>',
            r'<p[^>]*style="[^"]*color:\s*rgb\(204,\s*0,\s*0\)[^"]*"[^>]*>.*?solo para pruebas.*?</p>',
            
            # Mensaje genérico de reCAPTCHA
            r'<div[^>]*style="[^"]*color:\s*#cc0000[^"]*"[^>]*>.*?reCAPTCHA.*?</div>',
            r'<span[^>]*style="[^"]*color:\s*#cc0000[^"]*"[^>]*>.*?reCAPTCHA.*?</span>',
        ]
        
        # Aplicar cada patrón
        for pattern in patterns:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
        
        # Actualizar el contenido de la respuesta
        response.content = content.encode('utf-8')
        
        return response
