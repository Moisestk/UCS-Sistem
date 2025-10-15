/**
 * Validación de archivos del lado cliente
 * Restringe la carga solo a archivos PDF y DOCX
 */

document.addEventListener('DOMContentLoaded', function() {
    // Función para validar archivos
    function validateFile(file) {
        const allowedTypes = [
            'application/pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        ];
        
        const allowedExtensions = ['.pdf', '.docx'];
        const maxSize = 10 * 1024 * 1024; // 10MB
        
        // Validar extensión
        const fileName = file.name.toLowerCase();
        const hasValidExtension = allowedExtensions.some(ext => fileName.endsWith(ext));
        
        if (!hasValidExtension) {
            return {
                valid: false,
                message: 'Solo se permiten archivos PDF (.pdf) y Word (.docx).'
            };
        }
        
        // Validar tamaño
        if (file.size > maxSize) {
            return {
                valid: false,
                message: 'El archivo no puede ser mayor a 10MB.'
            };
        }
        
        return { valid: true };
    }
    
    // Función para mostrar mensaje de error
    function showError(input, message) {
        // Remover mensaje anterior si existe
        const existingError = input.parentNode.querySelector('.file-error-message');
        if (existingError) {
            existingError.remove();
        }
        
        // Crear nuevo mensaje de error
        const errorDiv = document.createElement('div');
        errorDiv.className = 'file-error-message text-red-600 text-sm mt-1 flex items-center';
        errorDiv.innerHTML = `<i class="fas fa-exclamation-circle mr-1"></i>${message}`;
        
        input.parentNode.appendChild(errorDiv);
        
        // Resaltar el input
        input.classList.add('border-red-500');
        input.classList.remove('border-gray-300');
    }
    
    // Función para limpiar errores
    function clearError(input) {
        const existingError = input.parentNode.querySelector('.file-error-message');
        if (existingError) {
            existingError.remove();
        }
        
        input.classList.remove('border-red-500');
        input.classList.add('border-gray-300');
    }
    
    // Aplicar validación a todos los inputs de archivo
    const fileInputs = document.querySelectorAll('input[type="file"][accept*=".pdf"], input[type="file"][accept*=".docx"]');
    
    fileInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            
            if (file) {
                const validation = validateFile(file);
                
                if (!validation.valid) {
                    showError(input, validation.message);
                    // Limpiar el input
                    input.value = '';
                } else {
                    clearError(input);
                }
            } else {
                clearError(input);
            }
        });
        
        // También validar en el evento 'input' para mayor compatibilidad
        input.addEventListener('input', function(e) {
            const file = e.target.files[0];
            
            if (file) {
                const validation = validateFile(file);
                
                if (!validation.valid) {
                    showError(input, validation.message);
                    input.value = '';
                } else {
                    clearError(input);
                }
            } else {
                clearError(input);
            }
        });
    });
    
    // Validación adicional en formularios
    const forms = document.querySelectorAll('form[enctype="multipart/form-data"]');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const fileInputs = form.querySelectorAll('input[type="file"]');
            let hasErrors = false;
            
            fileInputs.forEach(input => {
                const file = input.files[0];
                
                if (file) {
                    const validation = validateFile(file);
                    
                    if (!validation.valid) {
                        showError(input, validation.message);
                        hasErrors = true;
                    }
                }
            });
            
            if (hasErrors) {
                e.preventDefault();
                
                // Mostrar mensaje general
                const generalError = document.createElement('div');
                generalError.className = 'bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4';
                generalError.innerHTML = '<i class="fas fa-exclamation-triangle mr-2"></i>Por favor, corrige los errores en los archivos antes de continuar.';
                
                // Insertar al inicio del formulario
                form.insertBefore(generalError, form.firstChild);
                
                // Scroll al error
                generalError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                
                // Remover mensaje después de 5 segundos
                setTimeout(() => {
                    if (generalError.parentNode) {
                        generalError.remove();
                    }
                }, 5000);
            }
        });
    });
});
